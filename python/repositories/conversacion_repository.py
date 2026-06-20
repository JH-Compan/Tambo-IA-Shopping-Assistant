from datetime import datetime

from config.supabase_client import supabase
from utils.id_generator import generar_id


class ConversacionRepository:

    def crear_conversacion(self, user_id):
        nueva_conversacion = {
            "id": generar_id("CONV"),
            "user_id": user_id,
            "status": "open",
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "ended_at": None
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

    def guardar_mensaje(self, conversation_id, sender_type, content, intent=None):
        nuevo_mensaje = {
            "id": generar_id("MSG"),
            "conversation_id": conversation_id,
            "sender_type": sender_type,
            "content": content,
            "intent": intent,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        return self._insert_single("chat_messages", nuevo_mensaje)

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

    def _sanitize_error(self, error):
        return str(error).splitlines()[0][:300]
