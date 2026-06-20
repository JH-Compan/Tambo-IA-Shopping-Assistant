from copy import deepcopy

from models.nlp_analysis import build_nlp_analysis, normalize_nlp_analysis
from services.catalog_context_service import CatalogContextService
from services.dynamic_entity_resolver import DynamicEntityResolver


class NLPOrchestrator:
    NEED_PATTERNS = {
        "sed": ["tengo sed", "quiero tomar algo", "necesito una bebida", "algo para beber"],
        "hambre": ["tengo hambre", "quiero comer", "necesito algo de comer"],
        "desayuno": ["quiero desayunar", "algo para el desayuno"],
        "antojo_dulce": ["quiero algo dulce", "tengo antojo de dulce"],
        "snack": ["quiero picar algo", "quiero un snack", "algo pequeno para comer", "algo pequeño para comer"],
        "comida_rapida": ["algo rapido para comer", "algo rápido para comer", "comida rapida", "comida rápida"],
        "compartir": ["algo para compartir", "para varias personas"],
        "limpieza": ["quiero limpiar", "algo para limpiar la casa"],
        "cuidado_personal": ["necesito algo para mi higiene", "cuidado personal"],
        "ahorro": ["quiero algo barato", "lo mas economico", "lo más economico", "quiero ahorrar"],
    }

    def __init__(self, nlp_service, catalog_context_service=None, entity_resolver=None):
        self.nlp_service = nlp_service
        self.catalog_context_service = catalog_context_service or CatalogContextService(
            normalizer=self.nlp_service.normalize_text
        )
        self.entity_resolver = entity_resolver or DynamicEntityResolver(self.nlp_service.normalize_text)

    def orchestrate(
        self,
        mensaje,
        conversation_id,
        context_state,
        products=None,
        categories=None,
        analysis_result=None
    ):
        catalog_context = self.catalog_context_service.get_context()
        analysis_result = analysis_result or self.nlp_service.analyze(
            text=mensaje,
            products=products or catalog_context.get("products", []),
            categories=categories or catalog_context.get("categories", [])
        )

        normalized_text = analysis_result.get("normalized_text")
        if normalized_text is None:
            normalized_text = self.nlp_service.normalize_text(mensaje or "")

        contract = normalize_nlp_analysis(build_nlp_analysis())
        contract["intent"]["value"] = analysis_result.get("intent", "consulta_general")
        contract["intent"]["confidence"] = float(analysis_result.get("confidence", 0.0) or 0.0)
        contract["intent"]["source"] = self._resolve_intent_source(
            contract["intent"]["value"],
            contract["intent"]["confidence"],
            analysis_result.get("method")
        )

        entities = analysis_result.get("entities", {}) or {}
        contract["entities"]["product_id"] = entities.get("product_id")
        contract["entities"]["product_name"] = entities.get("product_name")
        contract["entities"]["brand"] = entities.get("brand")
        contract["entities"]["category_id"] = entities.get("category_id")
        contract["entities"]["category_name"] = entities.get("category") or entities.get("category_name")
        contract["entities"]["promotion_id"] = entities.get("promotion_id")
        contract["entities"]["promotion_type"] = entities.get("promotion_type")
        contract["entities"]["quantity"] = entities.get("quantity") or 1
        contract["entities"]["budget_min"] = entities.get("budget_min")
        contract["entities"]["budget_max"] = entities.get("budget_max")

        preference = entities.get("preference")
        if preference:
            contract["preferences"] = [preference]

        need = self._detect_need(normalized_text)
        if need:
            contract["need"]["value"] = need
            contract["need"]["status"] = "detected"
            contract["need"]["confidence"] = 0.9
            contract["need"]["source"] = "message"

        if (
            need in {"sed", "hambre"}
            and (
                contract["intent"]["value"] == "consulta_general"
                or contract["intent"]["confidence"] < 0.45
            )
        ):
            contract["intent"]["value"] = "pedir_recomendacion"
            contract["intent"]["source"] = "inferred"
            contract["intent"]["confidence"] = max(contract["intent"]["confidence"], 0.55)

        referenced_product_id = (
            (context_state or {}).get("pending_clarification", {}).get("partial_analysis", {})
            .get("context", {})
            .get("referenced_product_id")
            or (context_state or {}).get("last_analysis", {}).get("context", {}).get("referenced_product_id")
        )
        referenced_promotion_id = (
            (context_state or {}).get("pending_clarification", {}).get("partial_analysis", {})
            .get("context", {})
            .get("referenced_promotion_id")
            or (context_state or {}).get("last_analysis", {}).get("context", {}).get("referenced_promotion_id")
        )
        if referenced_product_id:
            contract["context"]["used_previous_turns"] = True
            contract["context"]["referenced_product_id"] = referenced_product_id
        if referenced_promotion_id:
            contract["context"]["used_previous_turns"] = True
            contract["context"]["referenced_promotion_id"] = referenced_promotion_id

        resolved = self.entity_resolver.resolve(mensaje, contract, catalog_context)
        self._deep_merge(contract, resolved["contract_updates"])
        contract = normalize_nlp_analysis(contract)

        contract["metadata"]["processing_status"] = "pending"
        contract["metadata"]["nlp_method"] = analysis_result.get("method", "unknown")
        contract["metadata"]["normalized_text"] = normalized_text
        contract["metadata"]["catalog_used"] = True
        contract["metadata"]["cache_used"] = bool(catalog_context.get("cache_used"))
        contract["metadata"]["match_sources"] = resolved["metadata"].get("match_sources", {})
        contract["metadata"]["entity_candidates"] = resolved["metadata"].get("entity_candidates", [])
        contract["metadata"]["category_candidates"] = resolved["metadata"].get("category_candidates", [])
        contract["metadata"]["entity_statuses"] = self._build_entity_statuses(contract)

        method = analysis_result.get("method", "unknown")
        if method == "ml":
            analysis_result["method"] = "ml+catalog"
        elif method == "rules":
            analysis_result["method"] = "rules+catalog"
        else:
            analysis_result["method"] = "hybrid+catalog"

        contract = normalize_nlp_analysis(contract)
        return {
            "analysis_result": analysis_result,
            "contract": contract,
            "compact_context": self.build_compact_context(contract),
            "normalized_text": normalized_text,
            "catalog_context": catalog_context,
        }

    def build_compact_context(self, contract):
        return {
            "intent": deepcopy(contract["intent"]),
            "need": deepcopy(contract["need"]),
            "entities": {
                "product_id": contract["entities"]["product_id"],
                "product_name": contract["entities"]["product_name"],
                "brand": contract["entities"]["brand"],
                "category_id": contract["entities"]["category_id"],
                "category_name": contract["entities"]["category_name"],
                "promotion_id": contract["entities"]["promotion_id"],
                "promotion_type": contract["entities"]["promotion_type"],
                "quantity": contract["entities"]["quantity"],
                "budget_min": contract["entities"]["budget_min"],
                "budget_max": contract["entities"]["budget_max"],
            },
            "preferences": list(contract["preferences"]),
            "exclusions": deepcopy(contract["exclusions"]),
            "context": deepcopy(contract["context"]),
            "decision": deepcopy(contract["decision"]),
            "metadata": {
                "processing_status": contract["metadata"]["processing_status"],
                "nlp_method": contract["metadata"].get("nlp_method", "unknown"),
                "entity_candidates": deepcopy(contract["metadata"].get("entity_candidates", [])),
                "category_candidates": deepcopy(contract["metadata"].get("category_candidates", [])),
                "errors": deepcopy(contract["metadata"].get("errors", [])),
            }
        }

    def _detect_need(self, normalized_text):
        for need, patterns in self.NEED_PATTERNS.items():
            if any(pattern in normalized_text for pattern in patterns):
                return need
        return None

    def _resolve_intent_source(self, intent, confidence, method):
        if method == "ml" and confidence >= 0.72:
            return "detected"
        if method == "rules":
            return "inferred"
        if intent == "consulta_general":
            return "defaulted"
        return "detected"

    def _build_entity_statuses(self, contract):
        statuses = {}
        for key, value in contract["entities"].items():
            if key == "quantity" and value == 1:
                statuses[key] = "defaulted"
            elif value is None:
                statuses[key] = "not_mentioned"
            else:
                statuses[key] = "detected"
        if contract["context"]["referenced_product_id"]:
            statuses["referenced_product_id"] = "context"
        if contract["context"]["referenced_promotion_id"]:
            statuses["referenced_promotion_id"] = "context"
        return statuses

    def _deep_merge(self, target, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
