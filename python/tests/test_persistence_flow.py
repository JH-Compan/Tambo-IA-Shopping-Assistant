import json
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SECRET_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.signature")

fake_supabase = types.ModuleType("supabase")
fake_supabase.Client = object
fake_supabase.create_client = MagicMock(return_value=MagicMock())
fake_config_supabase_client = types.ModuleType("config.supabase_client")
fake_config_supabase_client.supabase = MagicMock()

with patch.dict(sys.modules, {"supabase": fake_supabase, "config.supabase_client": fake_config_supabase_client}):
    from repositories.recomendacion_repository import RecomendacionRepository
    from services.chatbot_service import ChatbotService
    from services.context_resolver import ContextResolver
    from services.recomendacion_service import RecomendacionService


class RecomendacionRepositoryTestCase(unittest.TestCase):

    def setUp(self):
        self.repository = RecomendacionRepository()

    @patch("repositories.recomendacion_repository.supabase")
    def test_payload_correcto_recomendacion_producto(self, supabase_mock):
        response = MagicMock()
        response.data = [{"id": "REC1"}]
        supabase_mock.table.return_value.insert.return_value.execute.return_value = response

        result = self.repository.guardar_recomendaciones_generadas(
            conversation_id="CONV1",
            items=[{"id": "P1"}],
            item_type="product",
            reason="razon"
        )

        payload = supabase_mock.table.return_value.insert.call_args.args[0]
        self.assertEqual(payload[0]["recommendation_type"], "product")
        self.assertEqual(payload[0]["product_id"], "P1")
        self.assertIsNone(payload[0]["promotion_id"])
        self.assertGreaterEqual(payload[0]["score"], 0.0)
        self.assertLessEqual(payload[0]["score"], 1.0)
        self.assertTrue(result["success"])

    @patch("repositories.recomendacion_repository.supabase")
    def test_payload_correcto_recomendacion_promocion(self, supabase_mock):
        response = MagicMock()
        response.data = [{"id": "REC1"}]
        supabase_mock.table.return_value.insert.return_value.execute.return_value = response

        self.repository.guardar_recomendaciones_generadas(
            conversation_id="CONV1",
            items=[{"id": "PR1"}],
            item_type="promotion",
            reason="promo"
        )

        payload = supabase_mock.table.return_value.insert.call_args.args[0]
        self.assertEqual(payload[0]["recommendation_type"], "promotion")
        self.assertIsNone(payload[0]["product_id"])
        self.assertEqual(payload[0]["promotion_id"], "PR1")

    @patch("repositories.recomendacion_repository.supabase")
    def test_payload_correcto_interaccion_producto(self, supabase_mock):
        response = MagicMock()
        response.data = [{"id": "INT1"}]
        supabase_mock.table.return_value.insert.return_value.execute.return_value = response

        self.repository.guardar_interacciones_recomendadas(
            user_id="USR1",
            conversation_id="CONV1",
            items=[{"id": "P1"}],
            item_type="product"
        )

        payload = supabase_mock.table.return_value.insert.call_args.args[0]
        self.assertEqual(payload[0]["interaction_type"], "recommended")
        self.assertEqual(payload[0]["product_id"], "P1")
        self.assertIsNone(payload[0]["promotion_id"])
        self.assertEqual(payload[0]["weight"], 0.4)

    @patch("repositories.recomendacion_repository.supabase")
    def test_payload_correcto_interaccion_promocion(self, supabase_mock):
        response = MagicMock()
        response.data = [{"id": "INT1"}]
        supabase_mock.table.return_value.insert.return_value.execute.return_value = response

        self.repository.guardar_interacciones_recomendadas(
            user_id="USR1",
            conversation_id="CONV1",
            items=[{"id": "PR1"}],
            item_type="promotion"
        )

        payload = supabase_mock.table.return_value.insert.call_args.args[0]
        self.assertIsNone(payload[0]["product_id"])
        self.assertEqual(payload[0]["promotion_id"], "PR1")

    @patch("repositories.recomendacion_repository.supabase")
    def test_insercion_batch(self, supabase_mock):
        response = MagicMock()
        response.data = [{"id": "REC1"}, {"id": "REC2"}]
        supabase_mock.table.return_value.insert.return_value.execute.return_value = response

        result = self.repository.guardar_recomendaciones_generadas(
            conversation_id="CONV1",
            items=[{"id": "P1"}, {"id": "P2"}],
            item_type="product",
            reason="razon"
        )

        supabase_mock.table.return_value.insert.assert_called_once()
        self.assertEqual(result["attempted"], 2)
        self.assertEqual(result["saved"], 2)

    @patch("repositories.recomendacion_repository.supabase")
    def test_error_no_se_reporta_como_exito(self, supabase_mock):
        supabase_mock.table.return_value.insert.return_value.execute.side_effect = Exception(
            "42501 permission denied for table ai_recommendations"
        )

        result = self.repository.guardar_recomendaciones_generadas(
            conversation_id="CONV1",
            items=[{"id": "P1"}],
            item_type="product",
            reason="razon"
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["attempted"], 1)
        self.assertEqual(result["saved"], 0)
        self.assertIn("42501", result["error"])

    @patch("repositories.recomendacion_repository.supabase")
    def test_no_inserta_elementos_sin_identificador(self, supabase_mock):
        result = self.repository.guardar_recomendaciones_generadas(
            conversation_id="CONV1",
            items=[{"name": "sin id"}],
            item_type="product",
            reason="razon"
        )

        supabase_mock.table.assert_not_called()
        self.assertEqual(result["attempted"], 0)
        self.assertEqual(result["saved"], 0)

    @patch("repositories.recomendacion_repository.supabase")
    def test_resultado_serializable_json(self, supabase_mock):
        response = MagicMock()
        response.data = [{"id": "INT1"}]
        supabase_mock.table.return_value.insert.return_value.execute.return_value = response

        result = self.repository.guardar_interacciones_recomendadas(
            user_id="USR1",
            conversation_id="CONV1",
            items=[{"id": "PR1"}],
            item_type="promotion"
        )

        payload = json.dumps(result)
        self.assertIsInstance(payload, str)


class ChatbotServicePersistenceTestCase(unittest.TestCase):

    def setUp(self):
        self.service = ChatbotService()
        self.service.availability_service.validate_item_availability = MagicMock(return_value={
            "available": True,
            "reason_code": None,
            "reason": None,
            "details": {"available_quantity": 10, "requested_quantity": 1, "unavailable_products": []}
        })
        self.service.obtener_contexto_catalogo = MagicMock(return_value=([], []))
        self.service.nlp_orchestrator.orchestrate = MagicMock(return_value={
            "analysis_result": {
                "intent": "consultar_promocion",
                "confidence": 0.9,
                "method": "rules+catalog",
                "entities": {}
            },
            "contract": {
                "intent": {"value": "consultar_promocion", "confidence": 0.9},
                "need": {"value": None, "status": "not_mentioned", "confidence": 0.0, "source": "none"},
                "entities": {
                    "product_id": None,
                    "product_name": None,
                    "brand": None,
                    "category_id": None,
                    "category_name": None,
                    "promotion_id": None,
                    "promotion_type": None,
                    "quantity": 1,
                    "budget_min": None,
                    "budget_max": None
                },
                "context": {"referenced_product_id": None},
                "decision": {
                    "requires_clarification": False,
                    "clarification_field": None,
                    "clarification_question": None,
                    "next_action": "respond"
                },
                "preferences": [],
                "exclusions": {"products": [], "brands": [], "categories": []},
                "metadata": {"processing_status": "pending", "errors": []}
            },
            "compact_context": {}
        })
        self.service.clarification_policy.evaluate = MagicMock(return_value={
            "requires_clarification": False,
            "missing_field": None,
            "question": None,
            "next_action": "respond",
            "suggestions": []
        })
        self.service.detectar_intencion = MagicMock(return_value={
            "intent": "consultar_promocion",
            "confidence": 0.9,
            "method": "rules",
            "entities": {}
        })
        self.service.recomendacion_service.recomendar_productos = MagicMock(return_value={
            "tipo": "promociones",
            "items": [{"id": "PR1"}],
            "razon": "promo"
        })
        self.service.recomendacion_service.guardar_promociones_generadas = MagicMock(return_value={
            "success": True,
            "attempted": 1,
            "saved": 1,
            "data": [{"id": "REC1"}],
            "error": None
        })
        self.service.recomendacion_service.registrar_interacciones_promociones = MagicMock(return_value={
            "success": True,
            "attempted": 1,
            "saved": 1,
            "data": [{"id": "INT1"}],
            "error": None
        })
        self.service.recomendacion_service.marcar_recomendacion_seleccionada = MagicMock(return_value={
            "success": True,
            "attempted": 1,
            "saved": 1,
            "data": [{"id": "REC1"}],
            "error": None
        })
        self.service.recomendacion_service.registrar_interaccion_item = MagicMock(return_value={
            "success": True,
            "attempted": 1,
            "saved": 1,
            "data": [{"id": "INT2"}],
            "error": None
        })
        self.service.conversacion_repository.crear_conversacion = MagicMock(return_value={"id": "CONV1"})
        self.service.conversacion_repository.obtener_context_state = MagicMock(return_value={})
        self.service.conversacion_repository.actualizar_context_state = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.incrementar_clarification_count = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.resetear_clarification_count = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.actualizar_analisis_mensaje = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.marcar_mensaje_como_fallido = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.guardar_mensaje = MagicMock(side_effect=[
            {"success": True, "attempted": 1, "saved": 1, "data": [{"id": "MSG1"}], "error": None},
            {"success": True, "attempted": 1, "saved": 1, "data": [{"id": "MSG2"}], "error": None}
        ])

    def test_mensaje_bot_usa_respuesta_bot(self):
        self.service.procesar_mensaje(user_id="USR1", mensaje="Promos")

        second_call = self.service.conversacion_repository.guardar_mensaje.call_args_list[1]
        self.assertEqual(second_call.kwargs["intent"], "respuesta_bot")

    def test_persistence_auditable(self):
        result = self.service.procesar_mensaje(user_id="USR1", mensaje="Promos")

        self.assertEqual(result["persistence"]["status"], "ok")
        self.assertTrue(result["persistence"]["user_message_saved"])
        self.assertTrue(result["persistence"]["bot_message_saved"])
        self.assertEqual(result["persistence"]["recommendations"]["attempted"], 1)
        self.assertEqual(result["persistence"]["interactions"]["saved"], 1)

    def test_estado_partial_cuando_falla_supabase(self):
        self.service.recomendacion_service.guardar_promociones_generadas.return_value = {
            "success": False,
            "attempted": 1,
            "saved": 0,
            "data": [],
            "error": "42501 permission denied"
        }

        result = self.service.procesar_mensaje(user_id="USR1", mensaje="Promos")
        self.assertEqual(result["persistence"]["status"], "partial")

    def test_mensaje_usuario_se_crea_pending(self):
        self.service.procesar_mensaje(user_id="USR1", mensaje="Promos")
        first_call = self.service.conversacion_repository.guardar_mensaje.call_args_list[0]
        self.assertEqual(first_call.kwargs.get("processing_status", "pending"), "pending")

    def test_despues_del_analisis_se_actualiza_processed(self):
        self.service.procesar_mensaje(user_id="USR1", mensaje="Promos")
        self.service.conversacion_repository.actualizar_analisis_mensaje.assert_called_once()
        payload = self.service.conversacion_repository.actualizar_analisis_mensaje.call_args.kwargs
        self.assertEqual(payload["processing_status"], "processed")

    def test_error_marca_failed(self):
        self.service.nlp_orchestrator.orchestrate.side_effect = RuntimeError("boom")
        result = self.service.procesar_mensaje(user_id="USR1", mensaje="Promos")
        self.service.conversacion_repository.marcar_mensaje_como_fallido.assert_called_once()
        self.assertEqual(result["tipo"], "texto")

    def test_aclaracion_no_llama_recomendador_y_actualiza_contexto(self):
        self.service.clarification_policy.evaluate.return_value = {
            "requires_clarification": True,
            "missing_field": "product",
            "question": "¿De qué producto deseas conocer el precio?",
            "next_action": "ask",
            "suggestions": []
        }
        self.service.conversacion_repository.guardar_mensaje = MagicMock(side_effect=[
            {"success": True, "attempted": 1, "saved": 1, "data": [{"id": "MSG1"}], "error": None},
            {"success": True, "attempted": 1, "saved": 1, "data": [{"id": "MSG2"}], "error": None}
        ])

        result = self.service.procesar_mensaje(user_id="USR1", mensaje="Cuanto cuesta")

        self.service.recomendacion_service.recomendar_productos.assert_not_called()
        self.service.conversacion_repository.actualizar_context_state.assert_called()
        self.service.conversacion_repository.incrementar_clarification_count.assert_called_once()
        self.assertTrue(result["requires_clarification"])

    def test_contrato_sigue_incluyendo_todas_las_claves(self):
        result = self.service.procesar_mensaje(user_id="USR1", mensaje="Promos")
        self.assertIn("intent", result)
        self.assertIn("confidence", result)
        self.assertIn("entities", result)
        self.assertIn("response", result)
        self.assertIn("items", result)

    def test_chatbot_service_no_produce_keyerror_en_except(self):
        self.service.nlp_orchestrator.orchestrate.side_effect = RuntimeError("boom")
        result = self.service.procesar_mensaje(user_id="USR1", mensaje="quiero una galleta")
        self.assertFalse(result["success"])
        self.assertIn("response", result)
        self.assertEqual(result["confidence"], 0.0)

    def test_fallo_de_clarification_policy_no_derriba_endpoint(self):
        self.service.clarification_policy.evaluate.side_effect = AttributeError("list object has no attribute get")
        result = self.service.procesar_mensaje(user_id="USR1", mensaje="quiero una galleta")
        self.assertIn("response", result)
        self.assertIn("items", result)
        self.assertIn("intent", result)
        self.assertIn("confidence", result)


class ContextResolverTestCase(unittest.TestCase):

    def setUp(self):
        self.resolver = ContextResolver()
        self.analysis = {
            "intent": {"value": "consulta_general", "confidence": 0.7, "source": "detected"},
            "need": {"value": None, "status": "not_mentioned", "confidence": 0.0, "source": "none"},
            "entities": {
                "product_id": None,
                "product_name": None,
                "brand": None,
                "category_id": None,
                "category_name": None,
                "promotion_id": None,
                "promotion_type": None,
                "quantity": 1,
                "budget_min": None,
                "budget_max": None
            },
            "preferences": [],
            "exclusions": {"products": [], "brands": [], "categories": []},
            "context": {
                "used_previous_turns": False,
                "referenced_message_id": None,
                "referenced_recommendation_id": None,
                "referenced_product_id": None,
                "referenced_promotion_id": None
            },
            "decision": {
                "requires_clarification": False,
                "clarification_field": None,
                "clarification_question": None,
                "next_action": "respond"
            },
            "metadata": {"processing_status": "pending", "errors": []}
        }
        self.context_state = {
            "last_recommendations": [
                {"recommendation_id": "REC1", "item_id": "PROD1", "item_type": "product", "name": "A", "brand": "X", "price": 7.5, "rank_position": 1},
                {"recommendation_id": "REC2", "item_id": "PROD2", "item_type": "product", "name": "B", "brand": "Y", "price": 8.5, "rank_position": 2},
                {"recommendation_id": "REC3", "item_id": "PROD3", "item_type": "product", "name": "C", "brand": "Z", "price": 6.5, "rank_position": 3},
            ],
            "last_selected_item": None,
            "excluded_item_ids": [],
            "updated_at": "2026-06-20T12:00:00"
        }

    def test_agrega_el_segundo_resuelve_posicion_2(self):
        result = self.resolver.resolve("Agrega el segundo", self.analysis, self.context_state)
        self.assertEqual(result["client_action"]["item_id"], "PROD2")
        self.assertEqual(result["analysis"]["metadata"]["referenced_rank_position"], 2)

    def test_dame_dos_del_primero_resuelve_cantidad_2(self):
        result = self.resolver.resolve("Dame dos del primero", self.analysis, self.context_state)
        self.assertEqual(result["client_action"]["quantity"], 2)
        self.assertEqual(result["analysis"]["entities"]["quantity"], 2)

    def test_cuanto_cuesta_con_una_opcion_usa_contexto(self):
        one_option = dict(self.context_state)
        one_option["last_recommendations"] = [self.context_state["last_recommendations"][0]]
        result = self.resolver.resolve("¿Cuánto cuesta?", self.analysis, one_option)
        self.assertEqual(result["analysis"]["context"]["referenced_product_id"], "PROD1")
        self.assertFalse(result["analysis"]["decision"]["requires_clarification"])

    def test_cuanto_cuesta_con_tres_opciones_pide_aclaracion(self):
        result = self.resolver.resolve("¿Cuánto cuesta?", self.analysis, self.context_state)
        self.assertTrue(result["analysis"]["decision"]["requires_clarification"])
        self.assertIn("varias opciones", result["response_override"])

    def test_ese_no_agrega_item_a_excluded(self):
        selected = dict(self.context_state)
        selected["last_selected_item"] = self.context_state["last_recommendations"][1]
        result = self.resolver.resolve("Ese no", self.analysis, selected)
        self.assertIn("PROD2", result["context_state"]["excluded_item_ids"])

    def test_posicion_invalida_produce_aclaracion(self):
        result = self.resolver.resolve("Agrega el cuarto", self.analysis, self.context_state)
        self.assertTrue(result["analysis"]["decision"]["requires_clarification"])
        self.assertIn("Solo te mostré 3 opciones", result["response_override"])

    def test_context_state_es_serializable(self):
        state = self.resolver.build_recommendation_context(
            recommendation_result={"data": [{"id": "REC1"}]},
            items=[{"id": "PROD1", "name": "A", "brand": "X", "price": 5}],
            item_type="product",
            previous_state={}
        )
        self.assertIsInstance(json.dumps(state), str)


class RecomendacionServiceContextTestCase(unittest.TestCase):

    def setUp(self):
        self.service = RecomendacionService()
        self.service.producto_repository.listar_productos = MagicMock(return_value=[
            {"id": "PROD1", "name": "Uno", "brand": "A", "price": 5, "stock": 3, "is_active": True, "category_id": "C1"},
            {"id": "PROD2", "name": "Dos", "brand": "A", "price": 6, "stock": 3, "is_active": True, "category_id": "C1"},
        ])
        self.service.producto_repository.listar_categorias = MagicMock(return_value=[{"id": "C1", "name": "Bebidas"}])
        self.service.availability_service.filter_products = MagicMock(side_effect=lambda items, quantity=1: [
            item for item in (items or []) if item.get("id") != "PROD1"
        ] if items else [])
        self.service.availability_service.filtrar_promociones_disponibles = MagicMock(side_effect=lambda items, user_id=None, quantity=1: items or [])

    def test_dame_otra_opcion_no_retorna_producto_excluido(self):
        result = self.service.recomendar_productos(
            mensaje="otra opcion",
            analysis={
                "intent": {"value": "pedir_recomendacion"},
                "entities": {},
                "preferences": [],
                "exclusions": {"products": [], "brands": [], "categories": []},
                "metadata": {"excluded_item_ids": ["PROD1"], "category_candidates": []}
            }
        )
        returned_ids = [item["id"] for item in result["items"]]
        self.assertNotIn("PROD1", returned_ids)

    def test_producto_no_disponible_no_aparece_en_items_finales(self):
        result = self.service.recomendar_productos(
            mensaje="recomiendame algo",
            analysis={
                "intent": {"value": "pedir_recomendacion"},
                "entities": {},
                "preferences": [],
                "exclusions": {"products": [], "brands": [], "categories": []},
                "metadata": {"excluded_item_ids": [], "category_candidates": []}
            }
        )
        returned_ids = [item["id"] for item in result["items"]]
        self.assertEqual(returned_ids, ["PROD2"])


class ChatbotServiceContextActionTestCase(unittest.TestCase):

    def setUp(self):
        self.service = ChatbotService()
        self.service.availability_service.validate_item_availability = MagicMock(return_value={
            "available": True,
            "reason_code": None,
            "reason": None,
            "details": {"available_quantity": 10, "requested_quantity": 1, "unavailable_products": []}
        })
        self.service.obtener_contexto_catalogo = MagicMock(return_value=([], []))
        self.service.nlp_orchestrator.orchestrate = MagicMock(return_value={
            "analysis_result": {"intent": "consulta_general", "confidence": 0.8, "method": "rules+catalog", "entities": {}},
            "contract": {
                "intent": {"value": "consulta_general", "confidence": 0.8, "source": "detected"},
                "need": {"value": None, "status": "not_mentioned", "confidence": 0.0, "source": "none"},
                "entities": {"product_id": None, "product_name": None, "brand": None, "category_id": None, "category_name": None, "promotion_id": None, "promotion_type": None, "quantity": 1, "budget_min": None, "budget_max": None},
                "preferences": [],
                "exclusions": {"products": [], "brands": [], "categories": []},
                "context": {"used_previous_turns": False, "referenced_message_id": None, "referenced_recommendation_id": None, "referenced_product_id": None, "referenced_promotion_id": None},
                "decision": {"requires_clarification": False, "clarification_field": None, "clarification_question": None, "next_action": "respond"},
                "metadata": {"processing_status": "pending", "errors": []}
            },
            "compact_context": {}
        })
        self.service.clarification_policy.evaluate = MagicMock(return_value={
            "requires_clarification": False,
            "missing_field": None,
            "question": None,
            "next_action": "respond",
            "suggestions": []
        })
        self.service.conversacion_repository.crear_conversacion = MagicMock(return_value={"id": "CONV1"})
        self.service.conversacion_repository.obtener_context_state = MagicMock(return_value={
            "last_recommendations": [
                {"recommendation_id": "REC1", "item_id": "PROD1", "item_type": "product", "name": "A", "brand": "X", "price": 5, "rank_position": 1}
            ],
            "last_selected_item": None,
            "excluded_item_ids": [],
            "updated_at": "2026-06-20T12:00:00"
        })
        self.service.conversacion_repository.actualizar_context_state = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.resetear_clarification_count = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.actualizar_analisis_mensaje = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.marcar_mensaje_como_fallido = MagicMock(return_value={"success": True})
        self.service.conversacion_repository.guardar_mensaje = MagicMock(side_effect=[
            {"success": True, "attempted": 1, "saved": 1, "data": [{"id": "MSG1"}], "error": None},
            {"success": True, "attempted": 1, "saved": 1, "data": [{"id": "MSG2"}], "error": None}
        ])
        self.service.recomendacion_service.marcar_recomendacion_seleccionada = MagicMock(return_value={"success": True, "attempted": 1, "saved": 1, "data": [{"id": "REC1"}], "error": None})
        self.service.recomendacion_service.registrar_interaccion_item = MagicMock(return_value={"success": True, "attempted": 1, "saved": 1, "data": [{"id": "INT1"}], "error": None})

    def test_add_to_cart_action_preserva_item_id_real(self):
        result = self.service.procesar_mensaje(user_id="USR1", mensaje="Agrega el primero")
        self.assertEqual(result["client_action"]["item_id"], "PROD1")

    def test_was_selected_se_actualiza(self):
        self.service.procesar_mensaje(user_id="USR1", mensaje="Agrega el primero")
        self.service.recomendacion_service.marcar_recomendacion_seleccionada.assert_called_once_with("REC1")

    def test_item_no_disponible_no_devuelve_add_to_cart_y_entrega_alternativas(self):
        self.service.availability_service.validate_item_availability.return_value = {
            "available": False,
            "reason_code": "insufficient_stock",
            "reason": "Esta opcion ya no esta disponible.",
            "details": {"available_quantity": 0, "requested_quantity": 1, "unavailable_products": []}
        }
        self.service.recomendacion_service.recomendar_productos = MagicMock(return_value={
            "tipo": "productos",
            "items": [{"id": "PROD2", "name": "B", "price": 6}],
            "razon": "alternativas"
        })

        result = self.service.procesar_mensaje(user_id="USR1", mensaje="Agrega el primero")

        self.assertIsNone(result["client_action"])
        self.assertEqual([item["id"] for item in result["items"]], ["PROD2"])
        self.assertNotIn("PROD1", [item["item_id"] for item in result["items"] if "item_id" in item])
        saved_context = self.service.conversacion_repository.actualizar_context_state.call_args.args[1]
        self.assertNotIn("PROD1", [item["item_id"] for item in saved_context["last_recommendations"]])
        self.assertIn("PROD1", saved_context["excluded_item_ids"])


if __name__ == "__main__":
    unittest.main()
