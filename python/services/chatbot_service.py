from repositories.conversacion_repository import ConversacionRepository
from services.recomendacion_service import RecomendacionService


class ChatbotService:

    def __init__(self):
        self.conversacion_repository = ConversacionRepository()
        self.recomendacion_service = RecomendacionService()

    def procesar_mensaje(self, user_id, mensaje, conversation_id=None):
        if not conversation_id:
            conversacion = self.conversacion_repository.crear_conversacion(user_id)
            conversation_id = conversacion["id"]

        intent = self.detectar_intencion(mensaje)

        self.conversacion_repository.guardar_mensaje(
            conversation_id=conversation_id,
            sender_type="user",
            content=mensaje,
            intent=intent
        )

        respuesta_data = self.generar_respuesta(
            user_id=user_id,
            conversation_id=conversation_id,
            mensaje=mensaje,
            intent=intent
        )

        self.conversacion_repository.guardar_mensaje(
            conversation_id=conversation_id,
            sender_type="bot",
            content=respuesta_data["respuesta"],
            intent=intent
        )

        return {
            "conversation_id": conversation_id,
            "intent": intent,
            "respuesta": respuesta_data["respuesta"],
            "items": respuesta_data["items"],
            "tipo": respuesta_data["tipo"]
        }

    def detectar_intencion(self, mensaje):
        texto = mensaje.lower()

        if any(p in texto for p in ["hola", "buenas", "hey"]):
            return "saludo"

        if any(p in texto for p in ["promo", "promoción", "oferta", "descuento"]):
            return "buscar_promociones"

        if any(p in texto for p in ["quiero", "busco", "tienes", "recomienda", "comprar", "necesito"]):
            return "recomendar_producto"

        if any(p in texto for p in ["gracias", "ok", "listo"]):
            return "cierre"

        return "consulta_general"

    def generar_respuesta(self, user_id, conversation_id, mensaje, intent):
        if intent == "saludo":
            return {
                "respuesta": "Hola, soy TamboBot. Puedo ayudarte a buscar productos, promociones o recomendaciones.",
                "items": [],
                "tipo": "texto"
            }

        if intent == "cierre":
            return {
                "respuesta": "Gracias por usar TamboBot. Si necesitas otra recomendación, escríbeme nuevamente.",
                "items": [],
                "tipo": "texto"
            }

        recomendacion = self.recomendacion_service.recomendar_productos(
            mensaje=mensaje,
            conversation_id=conversation_id
        )

        items = recomendacion["items"]
        tipo = recomendacion["tipo"]
        razon = recomendacion["razon"]

        if not items:
            return {
                "respuesta": "No encontré resultados relacionados. Puedes intentar con otro producto o categoría.",
                "items": [],
                "tipo": tipo
            }

        if tipo == "productos":
            self.recomendacion_service.guardar_recomendaciones_generadas(
                conversation_id=conversation_id,
                productos=items,
                razon=razon
            )

            self.recomendacion_service.registrar_interacciones_recomendadas(
                user_id=user_id,
                conversation_id=conversation_id,
                productos=items
            )

            return {
                "respuesta": "Encontré estos productos que podrían interesarte:",
                "items": items,
                "tipo": "productos"
            }

        if tipo == "promociones":
            return {
                "respuesta": "Encontré estas promociones activas:",
                "items": items,
                "tipo": "promociones"
            }

        return {
            "respuesta": "Puedo ayudarte buscando productos o promociones.",
            "items": [],
            "tipo": "texto"
        }