from models.nlp_analysis import get_intent_confidence, get_intent_value, normalize_nlp_analysis


class ClarificationPolicy:
    HIGH_CONFIDENCE = 0.72
    MEDIUM_CONFIDENCE = 0.45
    AMBIGUOUS_DELTA = 0.12

    def evaluate(self, analysis, context_state, clarification_count):
        analysis = normalize_nlp_analysis(analysis)
        intent = get_intent_value(analysis)
        confidence = get_intent_confidence(analysis)
        entities = analysis["entities"]
        need = analysis["need"]["value"]
        referenced_product_id = analysis["context"]["referenced_product_id"]
        referenced_promotion_id = analysis["context"]["referenced_promotion_id"]
        metadata = analysis.get("metadata", {})
        product_candidates = self._get_candidates_by_type(metadata.get("entity_candidates"), "product")

        if analysis["decision"].get("requires_clarification"):
            return self._build_result(
                True,
                analysis["decision"].get("clarification_field"),
                analysis["decision"].get("clarification_question"),
                next_action=analysis["decision"].get("next_action", "ask")
            )

        if clarification_count >= 2:
            return self._build_result(
                True,
                "fallback_options",
                "Puedo ayudarte con una de estas opciones:",
                next_action="fallback_options",
                suggestions=["Ver bebidas", "Ver alimentos", "Ver productos para el hogar", "Ver promociones"],
            )

        if intent == "consultar_promocion":
            return self._build_result(False, None, None)

        if intent == "buscar_producto" and entities["brand"]:
            return self._build_result(False, None, None)

        if intent == "pedir_recomendacion" and need in {"sed", "hambre"}:
            return self._build_result(False, None, None)

        if intent == "consultar_precio" and entities["brand"] and not entities["product_id"]:
            return self._build_result(True, "product", "¿Cuál producto de esa marca deseas consultar?")

        if intent == "consultar_precio" and not any([entities["product_id"], entities["product_name"], referenced_product_id, referenced_promotion_id]):
            return self._build_result(True, "product", "¿De qué producto deseas conocer el precio?")

        if intent == "consultar_stock" and not any([entities["product_id"], entities["product_name"], referenced_product_id]):
            return self._build_result(True, "product", "¿De qué producto deseas consultar la disponibilidad?")

        if intent == "agregar_carrito" and not any([entities["product_id"], entities["product_name"], entities["promotion_id"], referenced_product_id, referenced_promotion_id]):
            return self._build_result(True, "product", "¿Qué producto deseas agregar al carrito?")

        if intent == "quitar_carrito" and not any([entities["product_id"], entities["product_name"], entities["promotion_id"]]):
            return self._build_result(True, "product", "¿Qué producto deseas quitar del carrito?")

        if intent == "comparar_productos":
            return self._build_result(True, "products", "¿Qué productos deseas comparar?")

        if len(product_candidates) >= 2:
            labels = [candidate.get("value") or candidate.get("name") or candidate.get("id") for candidate in product_candidates[:3]]
            labels = [label for label in labels if label]
            if labels:
                return self._build_result(True, "product", f"Encontré varias opciones parecidas: {', '.join(labels)}. ¿Cuál quieres?")

        if intent == "pedir_recomendacion":
            has_useful_signal = any([
                need,
                entities["category_name"],
                entities["product_name"],
                entities["product_id"],
                entities["brand"],
                analysis["metadata"].get("normalized_text"),
            ])
            if has_useful_signal:
                return self._build_result(False, None, None)

        if confidence < self.MEDIUM_CONFIDENCE and not any([
            need,
            entities["product_name"],
            entities["product_id"],
            entities["category_name"],
            entities["promotion_id"],
        ]):
            return self._build_result(
                True,
                "general",
                "No entendí completamente lo que buscas. ¿Quieres algo para comer, beber, para el hogar o deseas ver promociones?"
            )

        return self._build_result(False, None, None)

    def _get_candidates_by_type(self, candidates, expected_type):
        normalized = normalize_nlp_analysis({"metadata": {"entity_candidates": candidates}})["metadata"]["entity_candidates"]
        matches = []
        for candidate in normalized:
            if not isinstance(candidate, dict):
                continue
            candidate_type = candidate.get("entity_type") or candidate.get("type") or candidate.get("kind")
            if str(candidate_type or "").rstrip("s") == expected_type:
                matches.append(candidate)
        return matches

    def _build_result(self, requires_clarification, missing_field, question, next_action="respond", suggestions=None):
        return {
            "requires_clarification": requires_clarification,
            "missing_field": missing_field,
            "question": question,
            "next_action": next_action,
            "suggestions": suggestions or [],
        }
