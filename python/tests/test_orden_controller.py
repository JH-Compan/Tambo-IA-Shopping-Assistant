import os
import unittest
from unittest.mock import MagicMock, patch


os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SECRET_KEY", "test-secret")

with patch("supabase.create_client", return_value=MagicMock()):
    from app import crear_app
    from controllers.orden_controller import supabase


class OrdenControllerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = crear_app()
        self.client = self.app.test_client()

    def test_payload_vacio_devuelve_400(self):
        response = self.client.post("/api/ordenes", json=None)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_carrito_vacio_devuelve_400(self):
        response = self.client.post("/api/ordenes", json={
            "user_id": "USR1",
            "items": []
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("carrito", response.get_json()["error"].lower())

    def test_cantidad_invalida_devuelve_400(self):
        response = self.client.post("/api/ordenes", json={
            "user_id": "USR1",
            "items": [{"item_id": "PROD1", "item_type": "producto", "quantity": 0}]
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("quantity", response.get_json()["error"].lower())

    @patch.object(supabase, "rpc")
    def test_controlador_ignora_total_y_unit_price(self, rpc_mock):
        execute_result = MagicMock()
        execute_result.data = {
            "success": True,
            "order_id": "ORD1",
            "total_amount": 10.5,
            "items_count": 1,
        }
        rpc_mock.return_value.execute.return_value = execute_result

        response = self.client.post("/api/ordenes", json={
            "user_id": "USR1",
            "conversation_id": "CONV1",
            "total": 9999,
            "items": [{
                "item_id": "PROD1",
                "item_type": "producto",
                "quantity": 2,
                "unit_price": 0.01,
            }]
        })

        self.assertEqual(response.status_code, 201)
        rpc_payload = rpc_mock.call_args.args[1]
        self.assertNotIn("total", rpc_payload)
        self.assertEqual(rpc_payload["p_items"], [{
            "item_id": "PROD1",
            "item_type": "product",
            "quantity": 2,
        }])

    @patch.object(supabase, "rpc")
    def test_controlador_llama_rpc_con_valores_normalizados(self, rpc_mock):
        execute_result = MagicMock()
        execute_result.data = {
            "success": True,
            "order_id": "ORD2",
            "total_amount": 15.0,
            "items_count": 2,
        }
        rpc_mock.return_value.execute.return_value = execute_result

        response = self.client.post("/api/ordenes", json={
            "user_id": "USR1",
            "conversation_id": "CONV1",
            "items": [
                {"item_id": "PROD1", "item_type": "producto", "quantity": 1},
                {"item_id": "PROMO1", "item_type": "promoción", "quantity": 2},
            ]
        })

        self.assertEqual(response.status_code, 201)
        rpc_mock.assert_called_once_with("create_order_transaction", {
            "p_user_id": "USR1",
            "p_conversation_id": "CONV1",
            "p_items": [
                {"item_id": "PROD1", "item_type": "product", "quantity": 1},
                {"item_id": "PROMO1", "item_type": "promotion", "quantity": 2},
            ]
        })

    @patch.object(supabase, "rpc")
    def test_rpc_exitoso_devuelve_201(self, rpc_mock):
        execute_result = MagicMock()
        execute_result.data = {
            "success": True,
            "order_id": "ORD3",
            "total_amount": 20.0,
            "items_count": 1,
        }
        rpc_mock.return_value.execute.return_value = execute_result

        response = self.client.post("/api/ordenes", json={
            "user_id": "USR1",
            "items": [{"item_id": "PROD1", "item_type": "product", "quantity": 1}]
        })

        body = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(body["success"])
        self.assertEqual(body["order_id"], "ORD3")
        self.assertEqual(body["total_amount"], 20.0)
        self.assertEqual(body["items_count"], 1)

    @patch.object(supabase, "rpc")
    def test_error_stock_devuelve_409(self, rpc_mock):
        rpc_mock.return_value.execute.side_effect = Exception("STOCK: Stock insuficiente para el producto PROD1")

        response = self.client.post("/api/ordenes", json={
            "user_id": "USR1",
            "items": [{"item_id": "PROD1", "item_type": "product", "quantity": 5}]
        })

        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.get_json()["success"])
        self.assertIn("stock insuficiente", response.get_json()["error"].lower())

    @patch.object(supabase, "table")
    def test_chat_cerrar_sigue_funcionando(self, table_mock):
        response = self.client.post("/api/chat/cerrar", json={"conversation_id": "CONV1"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        table_mock.assert_called_once_with("chat_conversations")


if __name__ == "__main__":
    unittest.main()
