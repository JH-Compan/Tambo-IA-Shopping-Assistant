import re

from rapidfuzz import fuzz, process


class DynamicEntityResolver:
    PRODUCT_THRESHOLD = 88
    BRAND_THRESHOLD = 90
    CATEGORY_THRESHOLD = 88
    PROMOTION_THRESHOLD = 88
    GENERIC_TERMS = {"algo", "quiero", "barato", "tengo", "comer", "beber", "producto", "productos", "marca"}
    NEED_CATEGORY_ALIASES = {
        "sed": ["bebida", "bebidas", "lacteo", "jugo", "agua"],
        "hambre": ["comida", "comidas", "snack", "snacks"],
        "desayuno": ["lacteo", "bebida", "galleta", "cereal"],
        "antojo_dulce": ["dulce", "dulces", "helado", "galleta"],
        "limpieza": ["limpieza"],
        "cuidado_personal": ["cuidado personal", "higiene"],
    }
    NUMBER_WORDS = {
        "media docena": 6,
        "una docena": 12,
        "un": 1,
        "una": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
    }
    NEGATIVE_PATTERNS = ["no quiero", "sin", "menos", "que no sea", "no me gusta", "cualquier marca menos"]

    def __init__(self, normalizer):
        self.normalizer = normalizer

    def resolve(self, mensaje, base_contract, catalog_context):
        normalized = self.normalizer(mensaje)
        updates = {
            "entities": {
                "product_id": None,
                "product_name": None,
                "brand": None,
                "category_id": None,
                "category_name": None,
                "promotion_id": None,
                "promotion_type": None,
                "quantity": 1,
                "budget_min": None,
                "budget_max": None,
            },
            "preferences": [],
            "exclusions": {
                "product_ids": [],
                "products": [],
                "brands": [],
                "category_ids": [],
                "categories": [],
            },
        }
        metadata = {
            "entity_candidates": [],
            "category_candidates": [],
            "match_sources": {},
        }

        self._resolve_quantity(normalized, updates)
        self._resolve_budget(normalized, updates, base_contract)
        self._resolve_preferences(normalized, updates)
        self._resolve_exclusions(normalized, updates, catalog_context)
        self._resolve_entities(normalized, updates, catalog_context, metadata)
        self._resolve_need_categories(base_contract, updates, catalog_context, metadata)

        return {
            "contract_updates": updates,
            "metadata": metadata,
        }

    def _resolve_entities(self, normalized, updates, catalog_context, metadata):
        products = catalog_context.get("products", [])
        promotions = catalog_context.get("promotions", [])
        categories = catalog_context.get("categories", [])
        brands = catalog_context.get("brands", {})

        product_match = self._match_collection(normalized, self._build_product_index(products), self.PRODUCT_THRESHOLD)
        if product_match["resolved"]:
            product = product_match["resolved"]
            updates["entities"]["product_id"] = product.get("id")
            updates["entities"]["product_name"] = product.get("name")
            updates["entities"]["brand"] = product.get("brand")
            updates["entities"]["category_id"] = product.get("category_id")
            updates["entities"]["category_name"] = self._category_name(product.get("category_id"), catalog_context)
            metadata["match_sources"]["product"] = product_match["source"]
        elif product_match["ambiguous"]:
            metadata["entity_candidates"].append({"entity_type": "product", "matches": product_match["ambiguous"]})

        promotion_match = self._match_collection(normalized, self._build_promotion_index(promotions), self.PROMOTION_THRESHOLD)
        if promotion_match["resolved"]:
            promotion = promotion_match["resolved"]
            updates["entities"]["promotion_id"] = promotion.get("id")
            updates["entities"]["promotion_type"] = promotion.get("promotion_type")
            metadata["match_sources"]["promotion"] = promotion_match["source"]
        elif promotion_match["ambiguous"]:
            metadata["entity_candidates"].append({"entity_type": "promotion", "matches": promotion_match["ambiguous"]})

        if not updates["entities"]["product_id"]:
            brand_match = self._match_collection(normalized, brands, self.BRAND_THRESHOLD)
            if brand_match["resolved"]:
                updates["entities"]["brand"] = brand_match["resolved"]
                metadata["match_sources"]["brand"] = brand_match["source"]

        if not updates["entities"]["category_id"]:
            category_index = self._build_category_index(categories)
            category_match = self._match_collection(normalized, category_index, self.CATEGORY_THRESHOLD)
            if category_match["resolved"]:
                category = category_match["resolved"]
                updates["entities"]["category_id"] = category.get("id")
                updates["entities"]["category_name"] = category.get("name")
                metadata["match_sources"]["category"] = category_match["source"]
            elif category_match["ambiguous"]:
                metadata["category_candidates"] = category_match["ambiguous"]

    def _resolve_need_categories(self, base_contract, updates, catalog_context, metadata):
        need = base_contract["need"]["value"]
        if not need or updates["entities"]["category_id"] or base_contract["entities"]["category_id"]:
            return
        aliases = self.NEED_CATEGORY_ALIASES.get(need, [])
        candidates = []
        for category in catalog_context.get("categories", []):
            haystack = self.normalizer(f"{category.get('name', '')} {category.get('description', '')}")
            if any(self.normalizer(alias) in haystack for alias in aliases):
                candidates.append(category)
        if len(candidates) == 1:
            updates["entities"]["category_id"] = candidates[0].get("id")
            updates["entities"]["category_name"] = candidates[0].get("name")
        elif len(candidates) > 1:
            metadata["category_candidates"] = [item.get("name") for item in candidates]

        if need == "ahorro" and "economic" not in updates["preferences"]:
            updates["preferences"].append("economic")
        if need == "compartir" and "sharing" not in updates["preferences"]:
            updates["preferences"].append("sharing")

    def _resolve_quantity(self, normalized, updates):
        quantity = 1
        for phrase, value in self.NUMBER_WORDS.items():
            if phrase in normalized:
                quantity = value
                break
        if quantity == 1:
            for match in re.finditer(r"(?<!s\/)(?<!\d)(\d{1,3})(?!\s?(?:ml|l|%))(?!\d)", normalized):
                candidate = int(match.group(1))
                suffix = normalized[match.end():match.end() + 4].strip()
                if suffix.startswith(("ml", "l", "%")):
                    continue
                quantity = min(candidate, 100)
                break
        updates["entities"]["quantity"] = quantity

    def _resolve_budget(self, normalized, updates, base_contract):
        if base_contract["intent"]["value"] == "consultar_precio" and "cuanto cuesta" in normalized:
            return
        range_match = re.search(r"(?:entre|de)\s+(\d+(?:[.,]\d+)?)\s+(?:y|a)\s+(\d+(?:[.,]\d+)?)", normalized)
        max_match = re.search(r"(?:menos de|hasta|tengo)\s+(?:s\/\s*)?(\d+(?:[.,]\d+)?)", normalized)
        min_match = re.search(r"(?:desde|mas de|más de)\s+(?:s\/\s*)?(\d+(?:[.,]\d+)?)", normalized)
        if range_match:
            updates["entities"]["budget_min"] = self._to_float(range_match.group(1))
            updates["entities"]["budget_max"] = self._to_float(range_match.group(2))
        elif max_match:
            updates["entities"]["budget_max"] = self._to_float(max_match.group(1))
        elif min_match:
            updates["entities"]["budget_min"] = self._to_float(min_match.group(1))

    def _resolve_preferences(self, normalized, updates):
        mapping = {
            "economic": ["barato", "barata", "economico", "economico", "ahorrar"],
            "promotion": ["oferta", "promocion", "descuento"],
            "popular": ["popular", "mas vendido"],
            "sharing": ["para compartir", "varias personas"],
            "sweet": ["dulce"],
            "salty": ["salado"],
            "with_gas": ["con gas"],
            "without_gas": ["sin gas"],
        }
        for preference, patterns in mapping.items():
            if any(pattern in normalized for pattern in patterns) and preference not in updates["preferences"]:
                updates["preferences"].append(preference)

    def _resolve_exclusions(self, normalized, updates, catalog_context):
        for pattern in self.NEGATIVE_PATTERNS:
            if pattern not in normalized:
                continue
            fragment = normalized.split(pattern, 1)[1].strip()
            product_match = self._match_collection(fragment, self._build_product_index(catalog_context.get("products", [])), self.PRODUCT_THRESHOLD)
            if product_match["resolved"]:
                updates["exclusions"]["product_ids"].append(product_match["resolved"].get("id"))
                updates["exclusions"]["products"].append(product_match["resolved"].get("name"))
                continue
            brand_match = self._match_collection(fragment, catalog_context.get("brands", {}), self.BRAND_THRESHOLD)
            if brand_match["resolved"]:
                updates["exclusions"]["brands"].append(brand_match["resolved"])
                continue
            category_match = self._match_collection(fragment, self._build_category_index(catalog_context.get("categories", [])), self.CATEGORY_THRESHOLD)
            if category_match["resolved"]:
                updates["exclusions"]["category_ids"].append(category_match["resolved"].get("id"))
                updates["exclusions"]["categories"].append(category_match["resolved"].get("name"))
                continue
            if "dulce" in fragment and "sweet" in updates["preferences"]:
                updates["preferences"] = [value for value in updates["preferences"] if value != "sweet"]

    def _build_product_index(self, products):
        index = {}
        for product in products:
            candidates = [
                self.normalizer(product.get("name")),
                self.normalizer(f"{product.get('brand', '')} {product.get('name', '')}"),
            ]
            for candidate in candidates:
                if candidate:
                    index[candidate] = product
        return index

    def _build_promotion_index(self, promotions):
        return {
            self.normalizer(promotion.get("title")): promotion
            for promotion in promotions
            if self.normalizer(promotion.get("title"))
        }

    def _build_category_index(self, categories):
        index = {}
        for category in categories:
            name = self.normalizer(category.get("name"))
            description = self.normalizer(category.get("description"))
            if name:
                index[name] = category
            if description:
                index[description] = category
        return index

    def _match_collection(self, normalized, index, threshold):
        exact = self._exact_match(normalized, index)
        if exact["resolved"]:
            return exact

        keys = [key for key in index.keys() if key and len(key) >= 4 and key not in self.GENERIC_TERMS]
        if not keys:
            return {"resolved": None, "ambiguous": [], "source": None}
        matches = process.extract(normalized, keys, scorer=fuzz.WRatio, limit=2)
        if not matches or matches[0][1] < threshold:
            return {"resolved": None, "ambiguous": [], "source": None}
        if len(matches) > 1 and matches[1][1] >= threshold and abs(matches[0][1] - matches[1][1]) < 5:
            return {
                "resolved": None,
                "ambiguous": [self._candidate_label(index[matches[0][0]]), self._candidate_label(index[matches[1][0]])],
                "source": "ambiguous"
            }
        return {"resolved": index[matches[0][0]], "ambiguous": [], "source": "fuzzy"}

    def _exact_match(self, normalized, index):
        compact = normalized.replace(" ", "")
        matches = []
        seen = set()
        for key, value in index.items():
            if not key or key in self.GENERIC_TERMS:
                continue
            if (
                key in normalized
                or normalized in key
                or key.replace(" ", "") in compact
                or compact in key.replace(" ", "")
            ):
                entity_key = self._entity_key(value)
                if entity_key not in seen:
                    matches.append(value)
                    seen.add(entity_key)
        if not matches:
            return {"resolved": None, "ambiguous": [], "source": None}
        if len(matches) > 1:
            return {
                "resolved": None,
                "ambiguous": [self._candidate_label(match) for match in matches[:3]],
                "source": "ambiguous"
            }
        return {"resolved": matches[0], "ambiguous": [], "source": "exact"}

    def _candidate_label(self, entity):
        if isinstance(entity, dict):
            return entity.get("name") or entity.get("title") or entity.get("brand") or entity.get("id")
        return entity

    def _entity_key(self, entity):
        if isinstance(entity, dict):
            return entity.get("id") or entity.get("name") or entity.get("title") or entity.get("brand")
        return entity

    def _category_name(self, category_id, catalog_context):
        category = (catalog_context.get("category_by_id") or {}).get(category_id) or {}
        return category.get("name")

    def _to_float(self, value):
        try:
            return float(str(value).replace(",", "."))
        except Exception:
            return None
