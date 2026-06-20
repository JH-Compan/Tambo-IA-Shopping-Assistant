from copy import deepcopy
from datetime import datetime


class ContextResolver:
    ORDINAL_MAP = {
        "primero": 1,
        "primera": 1,
        "segundo": 2,
        "segunda": 2,
        "tercero": 3,
        "tercera": 3,
        "cuarto": 4,
        "cuarta": 4,
    }

    LAST_TOKENS = {"ultimo", "ultima"}
    REJECTION_PATTERNS = ("ese no", "esa no", "eso no", "este no", "esta no")
    OTHER_OPTION_PATTERNS = ("otra opcion", "otro opcion", "otra alternativa", "otro producto")
    PRICE_PATTERNS = ("cuanto cuesta", "cual es el precio", "precio")
    ADD_PATTERNS = ("agrega", "agregalo", "agregala", "dame", "ponlo", "ponla")

    def resolve(self, mensaje, analysis, context_state):
        updated_analysis = deepcopy(analysis or {})
        state = deepcopy(context_state or {})
        normalized_text = self._normalize(mensaje)
        recommendations = self._safe_recommendations(state.get("last_recommendations"))
        selected_item = self._safe_item(state.get("last_selected_item"))
        result = {
            "analysis": updated_analysis,
            "context_state": state,
            "client_action": None,
            "response_override": None,
            "skip_recommendation": False,
        }

        if not recommendations:
            return result

        if self._contains_any(normalized_text, self.OTHER_OPTION_PATTERNS):
            return self._resolve_other_option(result, recommendations, selected_item)

        if self._contains_any(normalized_text, self.REJECTION_PATTERNS):
            return self._resolve_rejection(result, recommendations, selected_item)

        if "mas barato" in normalized_text:
            return self._resolve_cheapest(result, recommendations)

        if self._looks_like_price_question(normalized_text):
            return self._resolve_price_question(result, recommendations, selected_item)

        if self._looks_like_add_to_cart(normalized_text):
            return self._resolve_add_to_cart(result, normalized_text, recommendations, selected_item)

        return result

    def build_recommendation_context(self, recommendation_result, items, item_type, previous_state=None):
        state = deepcopy(previous_state or {})
        previous_exclusions = list(state.get("excluded_item_ids") or [])
        rec_rows = (recommendation_result or {}).get("data") or []
        last_recommendations = []

        for index, item in enumerate((items or [])[:10], start=1):
            row = rec_rows[index - 1] if index - 1 < len(rec_rows) and isinstance(rec_rows[index - 1], dict) else {}
            item_id = item.get("id")
            if not item_id:
                continue
            last_recommendations.append({
                "recommendation_id": row.get("id"),
                "item_id": item_id,
                "item_type": item_type,
                "name": item.get("name") or item.get("title") or item.get("nombre"),
                "brand": item.get("brand"),
                "price": float(item.get("price") or item.get("promo_price") or 0),
                "rank_position": index,
            })

        state["last_recommendations"] = last_recommendations
        state["last_selected_item"] = None
        state["excluded_item_ids"] = previous_exclusions
        state["updated_at"] = self._timestamp()
        return self._json_safe(state)

    def mark_selected_item(self, context_state, selected_item):
        state = deepcopy(context_state or {})
        state["last_selected_item"] = self._safe_item(selected_item)
        state["updated_at"] = self._timestamp()
        return self._json_safe(state)

    def append_excluded_item(self, context_state, item_id):
        state = deepcopy(context_state or {})
        excluded = list(state.get("excluded_item_ids") or [])
        if item_id and item_id not in excluded:
            excluded.append(item_id)
        state["excluded_item_ids"] = excluded
        state["updated_at"] = self._timestamp()
        return self._json_safe(state)

    def _resolve_other_option(self, result, recommendations, selected_item):
        excluded_ids = list(result["context_state"].get("excluded_item_ids") or [])
        for rec in recommendations:
            item_id = rec.get("item_id")
            if item_id and item_id not in excluded_ids:
                excluded_ids.append(item_id)
        if selected_item and selected_item.get("item_id") and selected_item["item_id"] not in excluded_ids:
            excluded_ids.append(selected_item["item_id"])

        result["context_state"]["excluded_item_ids"] = excluded_ids
        result["context_state"]["updated_at"] = self._timestamp()
        result["analysis"]["intent"]["value"] = "pedir_recomendacion"
        result["analysis"]["context"]["used_previous_turns"] = True
        result["analysis"]["decision"]["next_action"] = "refresh_recommendations"
        result["analysis"]["decision"]["requires_clarification"] = False
        result["analysis"]["metadata"]["context_resolution_method"] = "excluded_previous_recommendations"
        result["analysis"]["metadata"]["excluded_item_ids"] = excluded_ids
        return result

    def _resolve_rejection(self, result, recommendations, selected_item):
        reference = selected_item or recommendations[-1]
        if not reference:
            result["analysis"]["decision"]["requires_clarification"] = True
            result["analysis"]["decision"]["clarification_question"] = "¿Cuál opción deseas descartar?"
            result["response_override"] = "¿Cuál opción deseas descartar?"
            result["skip_recommendation"] = True
            return result

        result["context_state"] = self.append_excluded_item(result["context_state"], reference.get("item_id"))
        self._apply_reference(result["analysis"], reference, "rejected_previous_recommendation")
        result["analysis"]["intent"]["value"] = "pedir_recomendacion"
        result["analysis"]["decision"]["next_action"] = "refresh_recommendations"
        result["analysis"]["metadata"]["excluded_item_ids"] = list(result["context_state"].get("excluded_item_ids") or [])
        return result

    def _resolve_cheapest(self, result, recommendations):
        reference = min(recommendations, key=lambda rec: float(rec.get("price") or 0))
        self._apply_reference(result["analysis"], reference, "cheapest_previous_recommendation")
        result["analysis"]["decision"]["next_action"] = "respond"
        result["context_state"] = self.mark_selected_item(result["context_state"], reference)
        return result

    def _resolve_price_question(self, result, recommendations, selected_item):
        if selected_item:
            self._apply_reference(result["analysis"], selected_item, "selected_item")
            result["analysis"]["decision"]["requires_clarification"] = False
            return result

        if len(recommendations) == 1:
            reference = recommendations[0]
            self._apply_reference(result["analysis"], reference, "single_recommendation")
            result["context_state"] = self.mark_selected_item(result["context_state"], reference)
            return result

        result["analysis"]["decision"]["requires_clarification"] = True
        result["analysis"]["decision"]["clarification_field"] = "product"
        result["analysis"]["decision"]["clarification_question"] = "Te mostré varias opciones. ¿Cuál deseas consultar?"
        result["analysis"]["decision"]["next_action"] = "ask"
        result["analysis"]["metadata"]["context_resolution_method"] = "ambiguous_previous_recommendations"
        result["response_override"] = "Te mostré varias opciones. ¿Cuál deseas consultar?"
        result["skip_recommendation"] = True
        return result

    def _resolve_add_to_cart(self, result, normalized_text, recommendations, selected_item):
        quantity = self._extract_quantity(normalized_text)
        reference = None
        rank = self._extract_rank(normalized_text)

        if rank == "last":
            reference = recommendations[-1]
        elif isinstance(rank, int):
            reference = next((rec for rec in recommendations if rec.get("rank_position") == rank), None)
            if not reference:
                result["analysis"]["decision"]["requires_clarification"] = True
                result["analysis"]["decision"]["clarification_field"] = "product"
                result["analysis"]["decision"]["clarification_question"] = f"Solo te mostré {len(recommendations)} opciones. ¿Cuál deseas elegir?"
                result["analysis"]["decision"]["next_action"] = "ask"
                result["analysis"]["metadata"]["context_resolution_method"] = "invalid_rank_reference"
                result["analysis"]["metadata"]["referenced_rank_position"] = rank
                result["response_override"] = result["analysis"]["decision"]["clarification_question"]
                result["skip_recommendation"] = True
                return result
        elif selected_item:
            reference = selected_item
        elif len(recommendations) == 1:
            reference = recommendations[0]
        else:
            result["analysis"]["decision"]["requires_clarification"] = True
            result["analysis"]["decision"]["clarification_field"] = "product"
            result["analysis"]["decision"]["clarification_question"] = "¿Cuál opción deseas agregar?"
            result["analysis"]["decision"]["next_action"] = "ask"
            result["analysis"]["metadata"]["context_resolution_method"] = "ambiguous_previous_recommendations"
            result["response_override"] = "¿Cuál opción deseas agregar?"
            result["skip_recommendation"] = True
            return result

        self._apply_reference(result["analysis"], reference, "ranked_previous_recommendation")
        result["analysis"]["intent"]["value"] = "agregar_carrito"
        result["analysis"]["entities"]["quantity"] = quantity
        result["analysis"]["decision"]["next_action"] = "add_to_cart"
        result["analysis"]["decision"]["requires_clarification"] = False
        result["analysis"]["metadata"]["referenced_rank_position"] = reference.get("rank_position")
        result["client_action"] = {
            "type": "add_to_cart",
            "item_type": reference.get("item_type"),
            "item_id": reference.get("item_id"),
            "quantity": quantity,
        }
        result["context_state"] = self.mark_selected_item(result["context_state"], reference)
        return result

    def _apply_reference(self, analysis, reference, method):
        analysis["context"]["used_previous_turns"] = True
        analysis["context"]["referenced_recommendation_id"] = reference.get("recommendation_id")
        analysis["context"]["referenced_rank_position"] = reference.get("rank_position")
        analysis["metadata"]["context_resolution_method"] = method
        if reference.get("rank_position") is not None:
            analysis["metadata"]["referenced_rank_position"] = reference.get("rank_position")
        if reference.get("item_type") == "promotion":
            analysis["entities"]["promotion_id"] = reference.get("item_id")
            analysis["context"]["referenced_promotion_id"] = reference.get("item_id")
            analysis["context"]["referenced_product_id"] = None
        else:
            analysis["entities"]["product_id"] = reference.get("item_id")
            analysis["context"]["referenced_product_id"] = reference.get("item_id")
            analysis["context"]["referenced_promotion_id"] = None

    def _extract_rank(self, normalized_text):
        for token, value in self.ORDINAL_MAP.items():
            if token in normalized_text:
                return value
        if any(token in normalized_text for token in self.LAST_TOKENS):
            return "last"
        return None

    def _extract_quantity(self, normalized_text):
        tokens = normalized_text.split()
        number_words = {
            "un": 1, "uno": 1, "una": 1,
            "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
        }
        for token in tokens:
            if token.isdigit():
                return max(1, int(token))
            if token in number_words:
                return number_words[token]
        return 1

    def _looks_like_price_question(self, normalized_text):
        return self._contains_any(normalized_text, self.PRICE_PATTERNS)

    def _looks_like_add_to_cart(self, normalized_text):
        return self._contains_any(normalized_text, self.ADD_PATTERNS)

    def _contains_any(self, normalized_text, patterns):
        return any(pattern in normalized_text for pattern in patterns)

    def _safe_recommendations(self, recommendations):
        result = []
        for item in recommendations or []:
            safe_item = self._safe_item(item)
            if safe_item and safe_item.get("item_id"):
                result.append(safe_item)
        return result

    def _safe_item(self, item):
        if not isinstance(item, dict):
            return None
        return {
            "recommendation_id": item.get("recommendation_id"),
            "item_id": item.get("item_id"),
            "item_type": item.get("item_type") or "product",
            "name": item.get("name"),
            "brand": item.get("brand"),
            "price": float(item.get("price") or 0),
            "rank_position": item.get("rank_position"),
        }

    def _timestamp(self):
        return datetime.now().isoformat(timespec="seconds")

    def _json_safe(self, data):
        return deepcopy(data)

    def _normalize(self, text):
        return (
            str(text or "")
            .lower()
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("¿", "")
            .replace("?", "")
            .strip()
        )
