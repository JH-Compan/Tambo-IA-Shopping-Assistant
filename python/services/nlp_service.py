from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path

from joblib import load
from rapidfuzz import fuzz, process


class NLPService:
    MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "intent_classifier.joblib"
    CONFIDENCE_THRESHOLD = 0.55
    PRICE_PATTERN = re.compile(r"(?<!\d)(\d+(?:[.,]\d+)?)")
    RANGE_PATTERN = re.compile(
        r"(?:entre|de)\s+(\d+(?:[.,]\d+)?)\s+(?:y|a)\s+(\d+(?:[.,]\d+)?)"
    )
    MAX_PATTERN = re.compile(
        r"(?:menos de|maximo|maximo de|máximo|máximo de|hasta)\s+(\d+(?:[.,]\d+)?)"
    )
    MIN_PATTERN = re.compile(
        r"(?:mas de|más de|desde)\s+(\d+(?:[.,]\d+)?)"
    )
    QUANTITY_PATTERN = re.compile(
        r"(?:quiero|llevo|dame|me das|necesito)?\s*(\d+)\s+"
        r"(?:unidades?|botellas?|latas?|paquetes?|galletas?|bebidas?|snacks?|productos?)"
    )

    def __init__(self, model_path: Path | None = None):
        self.model_path = model_path or self.MODEL_PATH
        self._model = None
        self._model_loaded = False

    def analyze(
        self,
        text: str,
        products: list[dict] | None = None,
        categories: list[dict] | None = None
    ) -> dict:
        raw_text = text if isinstance(text, str) else ""
        normalized_text = self.normalize_text(raw_text)
        entities = self.extract_entities(
            raw_text=raw_text,
            normalized_text=normalized_text,
            products=products or [],
            categories=categories or []
        )

        if not normalized_text:
            intent = self._infer_intent_by_rules(normalized_text)
            return self._build_result(intent, 1.0, "rules", normalized_text, entities)

        model = self._load_model()
        if model is not None:
            try:
                probabilities = model.predict_proba([normalized_text])[0]
                classes = model.classes_
                best_index = max(range(len(probabilities)), key=probabilities.__getitem__)
                confidence = float(probabilities[best_index])
                intent = str(classes[best_index])
                if intent == "recomendar_producto":
                    intent = "pedir_recomendacion"
                if confidence >= self.CONFIDENCE_THRESHOLD:
                    return self._build_result(intent, confidence, "ml", normalized_text, entities)
            except Exception:
                pass

        rule_intent = self._infer_intent_by_rules(normalized_text)
        return self._build_result(rule_intent, 0.6, "rules", normalized_text, entities)

    def normalize_text(self, text: str) -> str:
        collapsed = " ".join(text.strip().lower().split())
        without_accents = "".join(
            char for char in unicodedata.normalize("NFD", collapsed)
            if unicodedata.category(char) != "Mn"
        )
        cleaned = re.sub(r"[^a-z0-9\s]", " ", without_accents)
        return " ".join(cleaned.split())

    def extract_entities(
        self,
        raw_text: str,
        normalized_text: str,
        products: list[dict],
        categories: list[dict]
    ) -> dict:
        budget_min, budget_max = self._extract_budget(normalized_text)
        quantity = self._extract_quantity(normalized_text)
        category = self._extract_category(normalized_text, categories)
        preference = self._extract_preference(normalized_text)
        product = self._extract_product(normalized_text, products)

        return {
            "category": category,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "quantity": quantity,
            "preference": preference,
            "product_id": product.get("product_id"),
            "product_name": product.get("product_name"),
            "product_match_score": product.get("product_match_score")
        }

    def _load_model(self):
        if self._model_loaded:
            return self._model

        self._model_loaded = True
        if not self.model_path.exists():
            self._model = None
            return None

        try:
            self._model = load(self.model_path)
        except Exception:
            self._model = None

        return self._model

    def _infer_intent_by_rules(self, normalized_text: str) -> str:
        text = normalized_text or ""

        if any(term in text for term in ["promocion", "promo", "oferta", "descuento", "combo"]):
            return "consultar_promocion"
        if any(term in text for term in ["precio", "cuanto cuesta", "cuanto esta", "valor", "cuanto vale", "a como"]):
            return "consultar_precio"
        if any(term in text for term in ["stock", "disponible", "queda", "quedan", "todavia tienen", "aun hay"]):
            return "consultar_stock"
        if any(term in text for term in ["recomienda", "recomendame", "sugiere", "aconseja", "que me aconsejas", "que me recomiendas"]):
            return "pedir_recomendacion"
        if any(term in text for term in ["si", "me interesa", "quiero ese", "ese mismo", "me lo llevo", "confirmo"]):
            return "confirmar_interes"
        if any(term in text for term in ["busco", "tienes", "muestrame", "muestame", "quiero comprar", "necesito", "quiero ver"]):
            return "buscar_producto"
        if any(term in text for term in ["hola", "buenas", "buenos dias", "buen dia", "hey", "holis", "wenas"]):
            return "saludo"
        return "consulta_general"

    def _extract_budget(self, normalized_text: str) -> tuple[float | None, float | None]:
        range_match = self.RANGE_PATTERN.search(normalized_text)
        if range_match:
            minimum = self._to_float(range_match.group(1))
            maximum = self._to_float(range_match.group(2))
            if minimum is not None and maximum is not None:
                return minimum, maximum

        max_match = self.MAX_PATTERN.search(normalized_text)
        if max_match:
            return None, self._to_float(max_match.group(1))

        min_match = self.MIN_PATTERN.search(normalized_text)
        if min_match:
            return self._to_float(min_match.group(1)), None

        return None, None

    def _extract_quantity(self, normalized_text: str) -> int | None:
        quantity_match = self.QUANTITY_PATTERN.search(normalized_text)
        if not quantity_match:
            return None
        return int(quantity_match.group(1))

    def _extract_preference(self, normalized_text: str) -> str | None:
        if any(term in normalized_text for term in ["barato", "barata", "economico", "economica", "menor precio"]):
            return "economico"
        if any(term in normalized_text for term in ["promo", "promocion", "oferta", "descuento"]):
            return "promocion"
        if any(term in normalized_text for term in ["popular", "conocido", "mas vendido", "top"]):
            return "popular"
        return None

    def _extract_category(self, normalized_text: str, categories: list[dict]) -> str | None:
        normalized_categories = {}
        for category in categories:
            name = str(category.get("name", "")).strip()
            if not name:
                continue
            normalized_name = self.normalize_text(name)
            normalized_categories[normalized_name] = name
            if normalized_name and normalized_name in normalized_text:
                return name

        category_aliases = {
            "bebidas": ["bebida", "bebidas", "gaseosa", "agua", "jugo", "tomar"],
            "snacks": ["snack", "snacks", "papitas", "piqueo", "canchita"],
            "dulces": ["dulce", "dulces", "galleta", "galletas", "chocolate", "caramelo"],
            "comida": ["empanada", "comida", "sandwich"],
            "limpieza": ["limpieza", "jabon", "detergente", "papel"]
        }

        for category_name, aliases in category_aliases.items():
            if any(alias in normalized_text for alias in aliases):
                return normalized_categories.get(category_name, category_name)

        return None

    def _extract_product(self, normalized_text: str, products: list[dict]) -> dict:
        if not normalized_text or not products:
            return {
                "product_id": None,
                "product_name": None,
                "product_match_score": None
            }

        choices: dict[str, dict] = {}
        compact_choices: dict[str, dict] = {}
        for product in products:
            name = str(product.get("name", "")).strip()
            if not name:
                continue
            normalized_name = self.normalize_text(name)
            choices[normalized_name] = product
            compact_choices[normalized_name.replace(" ", "")] = product

        if not choices:
            return {
                "product_id": None,
                "product_name": None,
                "product_match_score": None
            }

        compact_text = normalized_text.replace(" ", "")
        for compact_name, product in compact_choices.items():
            if compact_name and compact_name in compact_text:
                return {
                    "product_id": product.get("id"),
                    "product_name": product.get("name"),
                    "product_match_score": 100.0
                }

        match = process.extractOne(
            normalized_text,
            list(choices.keys()),
            scorer=fuzz.WRatio
        )
        if not match:
            return {
                "product_id": None,
                "product_name": None,
                "product_match_score": None
            }

        matched_name, score, _ = match
        compact_match = process.extractOne(
            compact_text,
            list(compact_choices.keys()),
            scorer=fuzz.partial_ratio
        )

        if compact_match and compact_match[1] > score:
            matched_name = compact_match[0]
            score = compact_match[1]
            product = compact_choices[matched_name]
        else:
            product = choices[matched_name]

        if score < 60:
            return {
                "product_id": None,
                "product_name": None,
                "product_match_score": None
            }

        return {
            "product_id": product.get("id"),
            "product_name": product.get("name"),
            "product_match_score": float(score)
        }

    def _build_result(
        self,
        intent: str,
        confidence: float,
        method: str,
        normalized_text: str,
        entities: dict
    ) -> dict:
        safe_confidence = min(max(float(confidence), 0.0), 1.0)
        safe_entities = {}
        for key, value in entities.items():
            if isinstance(value, float) and math.isnan(value):
                safe_entities[key] = None
            else:
                safe_entities[key] = value

        return {
            "intent": intent,
            "confidence": safe_confidence,
            "method": method,
            "normalized_text": normalized_text,
            "entities": safe_entities
        }

    def _to_float(self, value: str | None) -> float | None:
        if value is None:
            return None
        return float(value.replace(",", "."))
