import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SECRET_KEY", "test-key")

fake_supabase = types.ModuleType("supabase")
fake_supabase.Client = object
fake_supabase.create_client = MagicMock(return_value=MagicMock())
fake_config_supabase_client = types.ModuleType("config.supabase_client")
fake_config_supabase_client.supabase = MagicMock()

with patch.dict(sys.modules, {"supabase": fake_supabase, "config.supabase_client": fake_config_supabase_client}):
    from app import crear_app
    from services.availability_service import AvailabilityService


class AvailabilityServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.service = AvailabilityService()
        self.service.producto_repository.listar_productos = MagicMock(return_value=[
            {"id": "PROD1", "is_active": True, "stock": 2, "price": 5},
            {"id": "PROD2", "is_active": False, "stock": 5, "price": 7},
            {"id": "PROD3", "is_active": True, "stock": 0, "price": 3},
            {"id": "PROD4", "is_active": True, "stock": 2, "price": None},
        ])
        self.service.producto_repository.listar_items_promocion = MagicMock(return_value=[
            {"promotion_id": "PROMO1", "product_id": "PROD1", "quantity": 1}
        ])
        self.service.producto_repository.obtener_cantidad_promocion_comprada_por_usuario = MagicMock(return_value=2)

    def test_filter_products_excluye_inactivos_sin_stock_y_sin_precio(self):
        result = self.service.listar_productos_disponibles()
        self.assertEqual([item["id"] for item in result], ["PROD1"])

    def test_promocion_con_limite_por_cliente_alcanzado_no_esta_disponible(self):
        result = self.service.filtrar_promociones_disponibles([
            {
                "id": "PROMO1",
                "is_active": True,
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "max_per_customer": 2,
            }
        ], user_id="USR1")
        self.assertEqual(result, [])

    def test_evaluate_item_promocion_devuelve_detalles_producto_invalido(self):
        result = self.service.evaluate_item("promotion", "PROMO1", requested_quantity=2, user_id="USR9")
        self.assertFalse(result["available"])
        self.assertEqual(result["reason_code"], "customer_limit_reached")

    def test_evaluate_item_producto_sin_stock_devuelve_contrato(self):
        self.service.producto_repository.obtener_producto_por_id = MagicMock(return_value={
            "id": "PROD9", "is_active": True, "stock": 0, "price": 5
        })
        result = self.service.evaluate_item("product", "PROD9", requested_quantity=1)
        self.assertFalse(result["available"])
        self.assertEqual(result["reason_code"], "insufficient_stock")
        self.assertEqual(result["details"]["requested_quantity"], 1)


class ProductoControllerAvailabilityTestCase(unittest.TestCase):

    def setUp(self):
        self.app = crear_app()
        self.client = self.app.test_client()

    @patch("controllers.producto_controller.producto_service.listar_productos")
    def test_api_productos_devuelve_solo_disponibles(self, listar_mock):
        listar_mock.return_value = [{"id": "PROD1"}]
        response = self.client.get("/api/productos")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [{"id": "PROD1"}])

    @patch("controllers.producto_controller.producto_service.listar_promociones")
    def test_api_promociones_pasa_user_id_a_servicio(self, listar_mock):
        listar_mock.return_value = [{"id": "PROMO1"}]
        response = self.client.get("/api/promociones?user_id=USR1")
        self.assertEqual(response.status_code, 200)
        listar_mock.assert_called_once_with(user_id="USR1")


if __name__ == "__main__":
    unittest.main()
