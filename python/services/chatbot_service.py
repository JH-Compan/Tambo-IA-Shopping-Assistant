from repositories.conversacion_repository import ConversacionRepository
from repositories.producto_repository import ProductoRepository
from services.nlp_service import NLPService
from services.recomendacion_service import RecomendacionService


class ChatbotService:

    def __init__(self):
        self.conversacion_repository = ConversacionRepository()
        self.producto_repository = ProductoRepository()
        self.recomendacion_service = RecomendacionService()
        self.nlp_service = NLPService()

    def procesar_mensaje(self, user_id, mensaje, conversation_id=None):
        if not conversation_id:
            conversacion = self.conversacion_repository.crear_conversacion(user_id)
            conversation_id = conversacion["id"]

        products, categories = self.obtener_contexto_catalogo()
        analysis = self.detectar_intencion(
            mensaje=mensaje,
            products=products,
            categories=categories
        )
        intent = analysis["intent"]

        user_message_result = self.conversacion_repository.guardar_mensaje(
            conversation_id=conversation_id,
            sender_type="user",
            content=mensaje,
            intent=intent
        )

        respuesta_data = self.generar_respuesta(
            user_id=user_id,
            conversation_id=conversation_id,
            mensaje=mensaje,
            analysis=analysis
        )

        bot_message_result = self.conversacion_repository.guardar_mensaje(
            conversation_id=conversation_id,
            sender_type="bot",
            content=respuesta_data["respuesta"],
            intent="respuesta_bot"
        )

        persistence = self._build_persistence_summary(
            user_message_result=user_message_result,
            bot_message_result=bot_message_result,
            recommendation_result=respuesta_data["recommendation_result"],
            interaction_result=respuesta_data["interaction_result"]
        )

        return {
            "conversation_id": conversation_id,
            "intent": intent,
            "confidence": analysis["confidence"],
            "method": analysis["method"],
            "entities": analysis["entities"],
            "respuesta": respuesta_data["respuesta"],
            "items": respuesta_data["items"],
            "tipo": respuesta_data["tipo"],
            "persistence": persistence
        }

    def detectar_intencion(self, mensaje, products=None, categories=None):
        return self.nlp_service.analyze(
            text=mensaje,
            products=products or [],
            categories=categories or []
        )

    def obtener_contexto_catalogo(self):
        try:
            products = self.producto_repository.listar_productos(limite=200)
        except Exception:
            products = []

        try:
            categories = self.producto_repository.listar_categorias()
        except Exception:
            categories = []

        return products, categories

    def generar_respuesta(self, user_id, conversation_id, mensaje, analysis):
        intent = analysis["intent"]

        if intent == "saludo":
            return self._build_response(
                respuesta="Hola, soy TamboBot. Puedo ayudarte a buscar productos, promociones o recomendaciones.",
                items=[],
                tipo="texto"
            )

        recomendacion = self.recomendacion_service.recomendar_productos(
            mensaje=mensaje,
            conversation_id=conversation_id,
            analysis=analysis
        )

        items = recomendacion["items"]
        tipo = recomendacion["tipo"]
        razon = recomendacion["razon"]
        recommendation_result = self._empty_persistence_result()
        interaction_result = self._empty_persistence_result()

        if not items:
            return self._build_response(
                respuesta="No encontré resultados relacionados. Puedes intentar con otro producto o categoría.",
                items=[],
                tipo=tipo
            )

        if tipo == "productos":
            recommendation_result = self.recomendacion_service.guardar_recomendaciones_generadas(
                conversation_id=conversation_id,
                productos=items,
                razon=razon
            )
            interaction_result = self.recomendacion_service.registrar_interacciones_recomendadas(
                user_id=user_id,
                conversation_id=conversation_id,
                productos=items
            )

            if intent == "consultar_precio":
                return self._build_response(
                    respuesta="Encontré estos productos para revisar su precio:",
                    items=items,
                    tipo="productos",
                    recommendation_result=recommendation_result,
                    interaction_result=interaction_result
                )

            if intent == "consultar_stock":
                return self._build_response(
                    respuesta="Encontré estos productos disponibles para tu consulta:",
                    items=items,
                    tipo="productos",
                    recommendation_result=recommendation_result,
                    interaction_result=interaction_result
                )

            if intent == "confirmar_interes":
                return self._build_response(
                    respuesta="Perfecto, estas son las opciones relacionadas con tu interés:",
                    items=items,
                    tipo="productos",
                    recommendation_result=recommendation_result,
                    interaction_result=interaction_result
                )

            return self._build_response(
                respuesta="Encontré estos productos que podrían interesarte:",
                items=items,
                tipo="productos",
                recommendation_result=recommendation_result,
                interaction_result=interaction_result
            )

        if tipo == "promociones":
            recommendation_result = self.recomendacion_service.guardar_promociones_generadas(
                conversation_id=conversation_id,
                promociones=items,
                razon=razon
            )
            interaction_result = self.recomendacion_service.registrar_interacciones_promociones(
                user_id=user_id,
                conversation_id=conversation_id,
                promociones=items
            )
            return self._build_response(
                respuesta="Encontré estas promociones activas:",
                items=items,
                tipo="promociones",
                recommendation_result=recommendation_result,
                interaction_result=interaction_result
            )

        return self._build_response(
            respuesta="Puedo ayudarte buscando productos o promociones.",
            items=[],
            tipo="texto"
        )

    def _build_response(
        self,
        respuesta,
        items,
        tipo,
        recommendation_result=None,
        interaction_result=None
    ):
        return {
            "respuesta": respuesta,
            "items": items,
            "tipo": tipo,
            "recommendation_result": recommendation_result or self._empty_persistence_result(),
            "interaction_result": interaction_result or self._empty_persistence_result()
        }

    def _build_persistence_summary(
        self,
        user_message_result,
        bot_message_result,
        recommendation_result,
        interaction_result
    ):
        flags = [
            bool(user_message_result["success"]),
            bool(bot_message_result["success"]),
            recommendation_result["saved"] == recommendation_result["attempted"],
            interaction_result["saved"] == interaction_result["attempted"]
        ]

        if all(flags):
            status = "ok"
        elif any(flags):
            status = "partial"
        else:
            status = "failed"

        return {
            "user_message_saved": bool(user_message_result["success"]),
            "bot_message_saved": bool(bot_message_result["success"]),
            "recommendations": {
                "attempted": recommendation_result["attempted"],
                "saved": recommendation_result["saved"]
            },
            "interactions": {
                "attempted": interaction_result["attempted"],
                "saved": interaction_result["saved"]
            },
            "status": status
        }

    def _empty_persistence_result(self):
        return {
            "success": True,
            "attempted": 0,
            "saved": 0,
            "data": [],
            "error": None
        }
