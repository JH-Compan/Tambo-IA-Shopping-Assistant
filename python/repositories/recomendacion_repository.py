from datetime import datetime

from config.supabase_client import supabase
from utils.id_generator import generar_id


class RecomendacionRepository:

    def guardar_interacciones_recomendadas(self, user_id, conversation_id, items, item_type):
        payload = self._build_interaction_payloads(
            user_id=user_id,
            conversation_id=conversation_id,
            items=items,
            item_type=item_type
        )
        return self._insert_batch("ai_user_interactions", payload)

    def guardar_recomendaciones_generadas(self, conversation_id, items, item_type, reason):
        payload = self._build_recommendation_payloads(
            conversation_id=conversation_id,
            items=items,
            item_type=item_type,
            reason=reason
        )
        return self._insert_batch("ai_recommendations", payload)

    def guardar_feedback(self, conversation_id, rating, comment=None):
        nuevo_feedback = {
            "id": generar_id("FDB"),
            "conversation_id": conversation_id,
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        try:
            response = (
                supabase
                .table("ai_feedback")
                .insert(nuevo_feedback)
                .execute()
            )

            if response.data:
                return response.data[0]

        except Exception as error:
            return {
                "success": False,
                "attempted": 1,
                "saved": 0,
                "data": [],
                "error": self._sanitize_error(error)
            }

        return {
            "success": False,
            "attempted": 1,
            "saved": 0,
            "data": [],
            "error": "No se pudo guardar feedback."
        }

    def marcar_recomendacion_seleccionada(self, recommendation_id):
        if not recommendation_id:
            return {
                "success": True,
                "attempted": 0,
                "saved": 0,
                "data": [],
                "error": None
            }
        return self._update_records(
            table_name="ai_recommendations",
            filters={"id": recommendation_id},
            payload={"was_selected": True}
        )

    def guardar_interaccion(self, user_id, conversation_id, item_id, item_type, interaction_type, weight=1):
        record = {
            "id": generar_id("INT"),
            "user_id": user_id,
            "conversation_id": conversation_id,
            "interaction_type": interaction_type,
            "product_id": item_id if item_type == "product" else None,
            "promotion_id": item_id if item_type == "promotion" else None,
            "weight": weight,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }
        if not self._is_valid_reference(record):
            return {
                "success": False,
                "attempted": 1,
                "saved": 0,
                "data": [],
                "error": "Referencia invalida para interaccion."
            }
        return self._insert_batch("ai_user_interactions", [record])

    def _build_recommendation_payloads(self, conversation_id, items, item_type, reason):
        payload = []
        timestamp = datetime.now().isoformat(timespec="seconds")

        for index, item in enumerate(items[:5]):
            score = self._normalize_score(round(0.95 - (index * 0.08), 2))
            record = {
                "id": generar_id("REC"),
                "conversation_id": conversation_id,
                "recommendation_type": item_type,
                "product_id": None,
                "promotion_id": None,
                "score": score,
                "reason": reason,
                "was_selected": False,
                "created_at": timestamp
            }

            if item_type == "product":
                record["product_id"] = item.get("id")
            elif item_type == "promotion":
                record["promotion_id"] = item.get("id")

            if self._is_valid_reference(record):
                payload.append(record)

        return payload

    def _build_interaction_payloads(self, user_id, conversation_id, items, item_type):
        payload = []
        timestamp = datetime.now().isoformat(timespec="seconds")

        for item in items[:5]:
            record = {
                "id": generar_id("INT"),
                "user_id": user_id,
                "conversation_id": conversation_id,
                "interaction_type": "recommended",
                "product_id": None,
                "promotion_id": None,
                "weight": 0.4,
                "created_at": timestamp
            }

            if item_type == "product":
                record["product_id"] = item.get("id")
            elif item_type == "promotion":
                record["promotion_id"] = item.get("id")

            if self._is_valid_reference(record):
                payload.append(record)

        return payload

    def _insert_batch(self, table_name, payload):
        attempted = len(payload)
        if not payload:
            return {
                "success": True,
                "attempted": 0,
                "saved": 0,
                "data": [],
                "error": None
            }

        try:
            response = (
                supabase
                .table(table_name)
                .insert(payload)
                .execute()
            )
            data = response.data or []
            success = len(data) == attempted
            return {
                "success": success,
                "attempted": attempted,
                "saved": len(data),
                "data": data,
                "error": None if success else f"Persistencia parcial o vacía en {table_name}."
            }
        except Exception as error:
            return {
                "success": False,
                "attempted": attempted,
                "saved": 0,
                "data": [],
                "error": self._sanitize_error(error)
            }

    def _update_records(self, table_name, filters, payload):
        try:
            query = supabase.table(table_name).update(payload)
            for key, value in (filters or {}).items():
                query = query.eq(key, value)
            response = query.execute()
            data = response.data or []
            return {
                "success": len(data) >= 1,
                "attempted": 1,
                "saved": len(data),
                "data": data,
                "error": None if data else f"No se pudo actualizar en {table_name}."
            }
        except Exception as error:
            return {
                "success": False,
                "attempted": 1,
                "saved": 0,
                "data": [],
                "error": self._sanitize_error(error)
            }

    def _normalize_score(self, score):
        return max(0.0, min(float(score), 1.0))

    def _is_valid_reference(self, record):
        product_id = record.get("product_id")
        promotion_id = record.get("promotion_id")
        return bool(product_id) ^ bool(promotion_id)

    def _sanitize_error(self, error):
        return str(error).splitlines()[0][:300]
