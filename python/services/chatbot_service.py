import logging

from models.nlp_analysis import get_intent_confidence, get_intent_value, normalize_nlp_analysis
from repositories.conversacion_repository import ConversacionRepository
from repositories.producto_repository import ProductoRepository
from services.clarification_policy import ClarificationPolicy
from services.context_resolver import ContextResolver
from services.nlp_service import NLPService
from services.nlp_orchestrator import NLPOrchestrator
from services.recomendacion_service import RecomendacionService


class ChatbotService:

    def __init__(self):
        self.conversacion_repository = ConversacionRepository()
        self.producto_repository = ProductoRepository()
        self.recomendacion_service = RecomendacionService()
        self.nlp_service = NLPService()
        self.nlp_orchestrator = NLPOrchestrator(self.nlp_service)
        self.clarification_policy = ClarificationPolicy()
        self.context_resolver = ContextResolver()
        self.logger = logging.getLogger(__name__)

    def procesar_mensaje(self, user_id, mensaje, conversation_id=None):
        user_message_result = self._empty_persistence_result()
        bot_message_result = self._empty_persistence_result()
        recommendation_result = self._empty_persistence_result()
        interaction_result = self._empty_persistence_result()
        analysis = normalize_nlp_analysis(self._default_analysis())

        try:
            if not conversation_id:
                conversacion = self.conversacion_repository.crear_conversacion(user_id)
                conversation_id = conversacion["id"]

            user_message_result = self.conversacion_repository.guardar_mensaje(
                conversation_id=conversation_id,
                sender_type="user",
                content=mensaje,
                intent=analysis["intent"]
            )
            user_message_id = self._extract_record_id(user_message_result)

            products, categories = self.obtener_contexto_catalogo()
            context_state = self.conversacion_repository.obtener_context_state(conversation_id)
            orchestration = self.nlp_orchestrator.orchestrate(
                mensaje=mensaje,
                conversation_id=conversation_id,
                context_state=context_state,
                products=products,
                categories=categories
            )
            analysis_result = orchestration["analysis_result"]
            analysis = normalize_nlp_analysis(orchestration["contract"])
            context_resolution = self.context_resolver.resolve(mensaje, analysis, context_state)
            analysis = normalize_nlp_analysis(context_resolution["analysis"])
            context_state = context_resolution["context_state"]

            clarification_count = max(0, int((context_state or {}).get("clarification_count") or 0))
            try:
                clarification = self.clarification_policy.evaluate(analysis, context_state or {}, clarification_count)
            except Exception as error:
                self.logger.exception("ClarificationPolicy failed: %s: %s", type(error).__name__, error)
                analysis["metadata"]["errors"].append(self._sanitize_error(error))
                clarification = {
                    "requires_clarification": False,
                    "missing_field": None,
                    "question": None,
                    "next_action": "respond",
                    "suggestions": []
                }

            existing_next_action = analysis["decision"].get("next_action")
            analysis["decision"]["requires_clarification"] = clarification["requires_clarification"]
            analysis["decision"]["clarification_field"] = clarification["missing_field"]
            analysis["decision"]["clarification_question"] = clarification["question"]
            analysis["decision"]["next_action"] = (
                existing_next_action
                if context_resolution.get("client_action") and existing_next_action == "add_to_cart"
                else clarification["next_action"]
            )
            analysis["metadata"]["processing_status"] = (
                "clarification" if clarification["requires_clarification"] else "processed"
            )

            if user_message_id:
                self.conversacion_repository.actualizar_analisis_mensaje(
                    message_id=user_message_id,
                    intent=analysis["intent"]["value"],
                    intent_confidence=analysis["intent"]["confidence"],
                    nlp_method=analysis_result.get("method"),
                    nlp_analysis=analysis,
                    processing_status=analysis["metadata"]["processing_status"]
                )

            if clarification["requires_clarification"]:
                new_context_state = self._build_clarification_context(
                    context_state=context_state or {},
                    message_id=user_message_id,
                    analysis=analysis,
                    missing_field=clarification["missing_field"],
                    question=clarification["question"],
                    attempt=clarification_count + 1
                )
                self.conversacion_repository.actualizar_context_state(conversation_id, new_context_state)
                self.conversacion_repository.incrementar_clarification_count(conversation_id)

                bot_text = self._build_clarification_response_text(clarification)
                bot_message_result = self.conversacion_repository.guardar_mensaje(
                    conversation_id=conversation_id,
                    sender_type="bot",
                    content=bot_text,
                    intent="respuesta_bot",
                    processing_status="processed"
                )
                persistence = self._build_persistence_summary(
                    user_message_result=user_message_result,
                    bot_message_result=bot_message_result,
                    recommendation_result=recommendation_result,
                    interaction_result=interaction_result
                )
                return {
                    "conversation_id": conversation_id,
                    "intent": get_intent_value(analysis),
                    "confidence": get_intent_confidence(analysis),
                    "method": analysis_result.get("method"),
                    "entities": analysis_result.get("entities", {}),
                    "respuesta": bot_text,
                    "response": bot_text,
                    "items": [],
                    "tipo": "texto",
                    "requires_clarification": True,
                    "clarification_question": clarification["question"],
                    "client_action": None,
                    "persistence": persistence
                }

            cleared_context = dict(context_state or {})
            cleared_context.pop("pending_clarification", None)
            cleared_context["last_analysis"] = self.nlp_orchestrator.build_compact_context(analysis)
            cleared_context["updated_at"] = self._timestamp()
            self.conversacion_repository.resetear_clarification_count(conversation_id)

            respuesta_data = self.generar_respuesta(
                user_id=user_id,
                conversation_id=conversation_id,
                mensaje=mensaje,
                analysis=analysis,
                context_state=cleared_context,
                context_resolution=context_resolution
            )
            recommendation_result = respuesta_data["recommendation_result"]
            interaction_result = respuesta_data["interaction_result"]
            self.conversacion_repository.actualizar_context_state(
                conversation_id,
                respuesta_data.get("context_state", cleared_context)
            )

            bot_message_result = self.conversacion_repository.guardar_mensaje(
                conversation_id=conversation_id,
                sender_type="bot",
                content=respuesta_data["respuesta"],
                intent="respuesta_bot",
                processing_status="processed"
            )

            persistence = self._build_persistence_summary(
                user_message_result=user_message_result,
                bot_message_result=bot_message_result,
                recommendation_result=recommendation_result,
                interaction_result=interaction_result
            )

            return {
                "conversation_id": conversation_id,
                "intent": get_intent_value(analysis),
                "confidence": get_intent_confidence(analysis),
                "method": analysis_result.get("method"),
                "entities": analysis["entities"],
                "respuesta": respuesta_data["respuesta"],
                "response": respuesta_data["respuesta"],
                "items": respuesta_data["items"],
                "tipo": respuesta_data["tipo"],
                "success": True,
                "requires_clarification": False,
                "client_action": respuesta_data.get("client_action"),
                "persistence": persistence
            }
        except Exception as error:
            message_id = self._extract_record_id(user_message_result)
            self.logger.exception("ChatbotService failed: %s: %s", type(error).__name__, error)
            if message_id:
                try:
                    self.conversacion_repository.marcar_mensaje_como_fallido(message_id, error)
                except Exception:
                    pass
            safe_reply = "No pude procesar tu mensaje en este momento. Puedes intentar nuevamente."
            try:
                bot_message_result = self.conversacion_repository.guardar_mensaje(
                    conversation_id=conversation_id,
                    sender_type="bot",
                    content=safe_reply,
                    intent="respuesta_bot",
                    processing_status="processed"
                ) if conversation_id else self._empty_persistence_result()
            except Exception:
                bot_message_result = self._empty_persistence_result()
            persistence = self._build_persistence_summary(
                user_message_result=user_message_result,
                bot_message_result=bot_message_result,
                recommendation_result=recommendation_result,
                interaction_result=interaction_result
            )
            return {
                "conversation_id": conversation_id,
                "success": False,
                "intent": get_intent_value(analysis),
                "confidence": get_intent_confidence(analysis),
                "method": analysis.get("metadata", {}).get("nlp_method", "unknown"),
                "entities": normalize_nlp_analysis(analysis)["entities"],
                "respuesta": safe_reply,
                "response": "No pude procesar tu solicitud en este momento.",
                "items": [],
                "tipo": "texto",
                "requires_clarification": False,
                "client_action": None,
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

    def generar_respuesta(self, user_id, conversation_id, mensaje, analysis, context_state=None, context_resolution=None):
        intent = analysis["intent"]["value"] if isinstance(analysis.get("intent"), dict) else analysis["intent"]
        context_state = dict(context_state or {})
        context_resolution = context_resolution or {}
        response_override = context_resolution.get("response_override")
        client_action = context_resolution.get("client_action")

        if intent == "saludo":
            return self._build_response(
                respuesta="Hola, soy TamboBot. Puedo ayudarte a buscar productos, promociones o recomendaciones.",
                items=[],
                tipo="texto",
                context_state=context_state
            )

        if analysis["decision"].get("next_action") == "add_to_cart" and client_action:
            context_state = self.context_resolver.mark_selected_item(context_state, {
                "recommendation_id": analysis["context"].get("referenced_recommendation_id"),
                "item_id": analysis["context"].get("referenced_promotion_id") or analysis["context"].get("referenced_product_id"),
                "item_type": "promotion" if analysis["context"].get("referenced_promotion_id") else "product",
                "rank_position": analysis["metadata"].get("referenced_rank_position"),
                "price": 0,
                "name": None,
                "brand": None,
            })
            self._track_selected_reference(user_id, conversation_id, analysis)
            return self._build_response(
                respuesta=response_override or "Listo, te ayudo a agregar esa opción al carrito.",
                items=[],
                tipo="texto",
                context_state=context_state,
                client_action=client_action
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
                respuesta=response_override or "No encontré resultados relacionados. Puedes intentar con otro producto o categoría.",
                items=[],
                tipo=tipo,
                context_state=context_state
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
            context_state = self.context_resolver.build_recommendation_context(
                recommendation_result=recommendation_result,
                items=items,
                item_type="product",
                previous_state=context_state
            )

            if intent == "consultar_precio":
                return self._build_response(
                    respuesta=response_override or "Encontré estos productos para revisar su precio:",
                    items=items,
                    tipo="productos",
                    recommendation_result=recommendation_result,
                    interaction_result=interaction_result,
                    context_state=context_state
                )

            if intent == "consultar_stock":
                return self._build_response(
                    respuesta=response_override or "Encontré estos productos disponibles para tu consulta:",
                    items=items,
                    tipo="productos",
                    recommendation_result=recommendation_result,
                    interaction_result=interaction_result,
                    context_state=context_state
                )

            if intent == "confirmar_interes":
                return self._build_response(
                    respuesta=response_override or "Perfecto, estas son las opciones relacionadas con tu interés:",
                    items=items,
                    tipo="productos",
                    recommendation_result=recommendation_result,
                    interaction_result=interaction_result,
                    context_state=context_state
                )

            return self._build_response(
                respuesta=response_override or "Encontré estos productos que podrían interesarte:",
                items=items,
                tipo="productos",
                recommendation_result=recommendation_result,
                interaction_result=interaction_result,
                context_state=context_state
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
            context_state = self.context_resolver.build_recommendation_context(
                recommendation_result=recommendation_result,
                items=items,
                item_type="promotion",
                previous_state=context_state
            )
            return self._build_response(
                respuesta=response_override or "Encontré estas promociones activas:",
                items=items,
                tipo="promociones",
                recommendation_result=recommendation_result,
                interaction_result=interaction_result,
                context_state=context_state
            )

        return self._build_response(
            respuesta=response_override or "Puedo ayudarte buscando productos o promociones.",
            items=[],
            tipo="texto",
            context_state=context_state
        )

    def _build_response(
        self,
        respuesta,
        items,
        tipo,
        recommendation_result=None,
        interaction_result=None,
        context_state=None,
        client_action=None
    ):
        return {
            "respuesta": respuesta,
            "items": items,
            "tipo": tipo,
            "recommendation_result": recommendation_result or self._empty_persistence_result(),
            "interaction_result": interaction_result or self._empty_persistence_result(),
            "context_state": context_state or {},
            "client_action": client_action
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

    def _default_analysis(self):
        return normalize_nlp_analysis({})

    def _extract_record_id(self, persistence_result):
        data = (persistence_result or {}).get("data") or []
        if not data:
            return None
        return data[0].get("id")

    def _build_clarification_context(self, context_state, message_id, analysis, missing_field, question, attempt):
        updated_state = dict(context_state or {})
        updated_state["pending_clarification"] = {
            "original_message_id": message_id,
            "original_intent": analysis["intent"]["value"],
            "missing_field": missing_field,
            "question": question,
            "attempt": attempt,
            "partial_analysis": self.nlp_orchestrator.build_compact_context(analysis)
        }
        updated_state["last_analysis"] = self.nlp_orchestrator.build_compact_context(analysis)
        updated_state["updated_at"] = self._timestamp()
        return updated_state

    def _build_clarification_response_text(self, clarification):
        if clarification["next_action"] == "fallback_options":
            return "Puedo ayudarte con una de estas opciones: Ver bebidas, Ver alimentos, Ver productos para el hogar o Ver promociones."
        return clarification["question"]

    def _timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat(timespec="seconds")

    def _track_selected_reference(self, user_id, conversation_id, analysis):
        referenced_recommendation_id = analysis["context"].get("referenced_recommendation_id")
        item_id = analysis["context"].get("referenced_promotion_id") or analysis["context"].get("referenced_product_id")
        item_type = "promotion" if analysis["context"].get("referenced_promotion_id") else "product"

        self.recomendacion_service.marcar_recomendacion_seleccionada(referenced_recommendation_id)
        if item_id:
            self.recomendacion_service.registrar_interaccion_item(
                user_id=user_id,
                conversation_id=conversation_id,
                item_id=item_id,
                item_type=item_type,
                interaction_type="added_to_cart",
                weight=1
            )

    def _sanitize_error(self, error):
        return str(error).splitlines()[0][:300]
