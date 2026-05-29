from datetime import datetime
from config.supabase_client import supabase
from utils.id_generator import generar_id


class RecomendacionRepository:

    def guardar_interaccion_producto(
        self,
        user_id,
        conversation_id,
        interaction_type,
        product_id,
        weight=0.3
    ):
        nueva_interaccion = {
            "id": generar_id("INT"),
            "user_id": user_id,
            "conversation_id": conversation_id,
            "interaction_type": interaction_type,
            "product_id": product_id,
            "promotion_id": None,
            "weight": weight,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        try:
            response = (
                supabase
                .table("ai_user_interactions")
                .insert(nueva_interaccion)
                .execute()
            )

            if response.data:
                return response.data[0]

        except Exception as error:
            print(f"[WARN] No se pudo guardar interacción en Supabase: {error}")

        return nueva_interaccion

    def guardar_recomendacion_producto(
        self,
        conversation_id,
        product_id,
        score,
        reason
    ):
        nueva_recomendacion = {
            "id": generar_id("REC"),
            "conversation_id": conversation_id,
            "recommendation_type": "product",
            "product_id": product_id,
            "promotion_id": None,
            "score": score,
            "reason": reason,
            "was_selected": False,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        try:
            response = (
                supabase
                .table("ai_recommendations")
                .insert(nueva_recomendacion)
                .execute()
            )

            if response.data:
                return response.data[0]

        except Exception as error:
            print(f"[WARN] No se pudo guardar recomendación en Supabase: {error}")

        return nueva_recomendacion

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
            print(f"[WARN] No se pudo guardar feedback en Supabase: {error}")

        return nuevo_feedback
