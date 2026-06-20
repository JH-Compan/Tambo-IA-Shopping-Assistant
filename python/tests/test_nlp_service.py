import json
import math
import unittest
from pathlib import Path

from services.nlp_service import NLPService


class NLPServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.products = [
            {"id": "P1", "name": "Coca-Cola", "price": 4.5, "category_id": "C1"},
            {"id": "P2", "name": "Oreo", "price": 2.5, "category_id": "C2"},
            {"id": "P3", "name": "Inca Kola", "price": 4.0, "category_id": "C1"},
            {"id": "P4", "name": "Agua San Luis", "price": 1.5, "category_id": "C1"}
        ]
        self.categories = [
            {"id": "C1", "name": "Bebidas"},
            {"id": "C2", "name": "Snacks"}
        ]
        missing_model_path = Path(__file__).resolve().parent / "fixtures" / "missing_model.joblib"
        self.service = NLPService(model_path=missing_model_path)

    def analyze(self, text):
        return self.service.analyze(
            text=text,
            products=self.products,
            categories=self.categories
        )

    def test_hola_produce_saludo(self):
        result = self.analyze("Hola")
        self.assertEqual(result["intent"], "saludo")

    def test_promociones_produce_consultar_promocion(self):
        result = self.analyze("Muéstrame las promociones")
        self.assertEqual(result["intent"], "consultar_promocion")

    def test_busco_una_gaseosa_produce_buscar_producto(self):
        result = self.analyze("Busco una gaseosa")
        self.assertEqual(result["intent"], "buscar_producto")
        self.assertEqual(result["entities"]["category"], "Bebidas")

    def test_precio_de_coca_cola(self):
        result = self.analyze("Cuánto cuesta la Coca Cola")
        self.assertEqual(result["intent"], "consultar_precio")
        self.assertEqual(result["entities"]["product_name"], "Coca-Cola")

    def test_stock_de_oreo(self):
        result = self.analyze("Hay stock de Oreo")
        self.assertEqual(result["intent"], "consultar_stock")
        self.assertEqual(result["entities"]["product_name"], "Oreo")

    def test_recomendacion_bebida_barata(self):
        result = self.analyze("Recomiéndame una bebida barata")
        self.assertEqual(result["intent"], "pedir_recomendacion")
        self.assertEqual(result["entities"]["preference"], "economico")

    def test_extrae_budget_max(self):
        result = self.analyze("Quiero algo por menos de 5 soles")
        self.assertEqual(result["entities"]["budget_max"], 5.0)
        self.assertIsNone(result["entities"]["budget_min"])

    def test_extrae_rango_presupuesto(self):
        result = self.analyze("Quiero algo entre 5 y 10 soles")
        self.assertEqual(result["entities"]["budget_min"], 5.0)
        self.assertEqual(result["entities"]["budget_max"], 10.0)

    def test_entrada_vacia_no_falla(self):
        result = self.analyze("")
        self.assertEqual(result["intent"], "consulta_general")
        self.assertEqual(result["normalized_text"], "")

    def test_fallback_sin_modelo(self):
        result = self.analyze("Muéstrame las promociones")
        self.assertEqual(result["method"], "rules")

    def test_match_aproximado_producto(self):
        result = self.analyze("Quiero saber el precio de la cocacola")
        self.assertEqual(result["entities"]["product_name"], "Coca-Cola")
        self.assertGreaterEqual(result["entities"]["product_match_score"], 60.0)

    def test_resultado_serializable(self):
        result = self.analyze("Quiero algo por menos de 5 soles")
        payload = json.dumps(result)
        self.assertIsInstance(payload, str)

    def test_confianza_entre_cero_y_uno(self):
        result = self.analyze("Hola")
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

    def test_no_aparecen_nan(self):
        result = self.analyze("Necesito algo")
        for value in result["entities"].values():
            if isinstance(value, float):
                self.assertFalse(math.isnan(value))


if __name__ == "__main__":
    unittest.main()
