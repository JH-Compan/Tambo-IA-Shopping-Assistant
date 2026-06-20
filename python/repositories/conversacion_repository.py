from datetime import datetime

from config.supabase_client import supabase
from models.nlp_analysis import build_nlp_analysis
from utils.id_generator import generar_id


class ConversacionRepository:

    def crear_conversacion(self, user_id):
        nueva_conversacion = {
            "id": generar_id("CONV"),
            "user_id": user_id,
            "status": "open",
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "ended_at": None,
            "context_state": {},
            "clarification_count": 0
        }

        response = (
            supabase
            .table("chat_conversations")
            .insert(nueva_conversacion)
            .execute()
        )

        if response.data:
            return response.data[0]

        raise RuntimeError("No se pudo crear la conversación en Supabase.")

    def guardar_mensaje(
        self,
        conversation_id,
        sender_type,
        content,
        intent=None,
        processing_status="pending",
        nlp_analysis=None,
        intent_confidence=None,
        nlp_method=None,
        processed_at=None
    ):
        nuevo_mensaje = {
            "id": generar_id("MSG"),
            "conversation_id": conversation_id,
            "sender_type": sender_type,
            "content": content,
            "intent": intent,
            "intent_confidence": intent_confidence,
            "nlp_method": nlp_method,
            "nlp_analysis": nlp_analysis or build_nlp_analysis(),
            "processing_status": processing_status,
            "processed_at": processed_at,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        return self._insert_single("chat_messages", nuevo_mensaje)

    def actualizar_analisis_mensaje(
        self,
        message_id,
        intent,
        intent_confidence,
        nlp_method,
        nlp_analysis,
        processing_status="processed"
    ):
        payload = {
            "intent": intent,
            "intent_confidence": intent_confidence,
            "nlp_method": nlp_method,
            "nlp_analysis": nlp_analysis,
            "processing_status": processing_status,
            "processed_at": datetime.now().isoformat(timespec="seconds")
        }
        return self._update_single("chat_messages", message_id, payload)

    def marcar_mensaje_como_fallido(self, message_id, error_message):
        sanitized_error = self._sanitize_error(error_message)
        payload = {
            "processing_status": "failed",
            "processed_at": datetime.now().isoformat(timespec="seconds"),
            "nlp_analysis": build_nlp_analysis({
                "metadata": {
                    "processing_status": "failed",
                    "errors": [sanitized_error]
                }
            })
        }
        return self._update_single("chat_messages", message_id, payload)

    def obtener_historial(self, conversation_id):
        try:
            response = (
                supabase
                .table("chat_messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at")
                .execute()
            )

            return response.data

        except Exception:
            return []

    def cerrar_conversacion(self, conversation_id):
        try:
            response = (
                supabase
                .table("chat_conversations")
                .update({
                    "status": "closed",
                    "ended_at": datetime.now().isoformat(timespec="seconds")
                })
                .eq("id", conversation_id)
                .execute()
            )

            return response.data

        except Exception:
            return []

    def obtener_context_state(self, conversation_id):
        try:
            response = (
                supabase
                .table("chat_conversations")
                .select("context_state")
                .eq("id", conversation_id)
                .single()
                .execute()
            )
            data = response.data or {}
            return data.get("context_state") or {}
        except Exception:
            return {}

    def actualizar_context_state(self, conversation_id, context_state):
        payload = {
            "context_state": context_state or {}
        }
        return self._update_single("chat_conversations", conversation_id, payload)

    def incrementar_clarification_count(self, conversation_id):
        current_state = self._get_conversation_fields(conversation_id, "clarification_count")
        current_count = max(0, int((current_state or {}).get("clarification_count") or 0))
        return self._update_single(
            "chat_conversations",
            conversation_id,
            {"clarification_count": current_count + 1}
        )

    def resetear_clarification_count(self, conversation_id):
        return self._update_single(
            "chat_conversations",
            conversation_id,
            {"clarification_count": 0}
        )

    def _insert_single(self, table_name, payload):
        try:
            response = (
                supabase
                .table(table_name)
                .insert(payload)
                .execute()
            )
            data = response.data or []
            return {
                "success": len(data) == 1,
                "attempted": 1,
                "saved": len(data),
                "data": data,
                "error": None if data else f"No se pudo guardar en {table_name}."
            }
        except Exception as error:
            return {
                "success": False,
                "attempted": 1,
                "saved": 0,
                "data": [],
                "error": self._sanitize_error(error)
            }

    def _update_single(self, table_name, record_id, payload):
        try:
            response = (
                supabase
                .table(table_name)
                .update(payload)
                .eq("id", record_id)
                .execute()
            )
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

    def _get_conversation_fields(self, conversation_id, fields):
        try:
            response = (
                supabase
                .table("chat_conversations")
                .select(fields)
                .eq("id", conversation_id)
                .single()
                .execute()
            )
            return response.data or {}
        except Exception:
            return {}

    def _sanitize_error(self, error):
        return str(error).splitlines()[0][:300]
