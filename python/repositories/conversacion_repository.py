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

        return response.data[0]

    def guardar_mensaje(self, conversation_id, sender_type, content, intent=None):
        nuevo_mensaje = {
            "id": generar_id("MSG"),
            "conversation_id": conversation_id,
            "sender_type": sender_type,
            "content": content,
            "intent": intent,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }

        response = (
            supabase
            .table("chat_messages")
            .insert(nuevo_mensaje)
            .execute()
        )

        return response.data[0]

    def obtener_historial(self, conversation_id):
        response = (
            supabase
            .table("chat_messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at")
            .execute()
        )

        return response.data

    def cerrar_conversacion(self, conversation_id):
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