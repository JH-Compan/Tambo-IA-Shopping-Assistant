import json
import unittest
from unittest.mock import MagicMock, patch

with patch("supabase.create_client", return_value=MagicMock()):
    from repositories.recomendacion_repository import RecomendacionRepository
    from services.chatbot_service import ChatbotService


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
        self.service.obtener_contexto_catalogo = MagicMock(return_value=([], []))
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
        self.service.conversacion_repository.crear_conversacion = MagicMock(return_value={"id": "CONV1"})
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


if __name__ == "__main__":
    unittest.main()
