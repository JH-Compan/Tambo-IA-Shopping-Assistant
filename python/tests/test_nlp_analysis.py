import json
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SECRET_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.signature")

from models.nlp_analysis import (
    build_nlp_analysis,
    get_intent_confidence,
    get_intent_value,
    normalize_nlp_analysis,
)

fake_supabase = types.ModuleType("supabase")
fake_supabase.Client = object
fake_supabase.create_client = MagicMock(return_value=MagicMock())
fake_config_supabase_client = types.ModuleType("config.supabase_client")
fake_config_supabase_client.supabase = MagicMock()

with patch.dict(sys.modules, {"supabase": fake_supabase, "config.supabase_client": fake_config_supabase_client}):
    from repositories.conversacion_repository import ConversacionRepository
    from services.catalog_context_service import CatalogContextService
    from services.clarification_policy import ClarificationPolicy
    from services.nlp_orchestrator import NLPOrchestrator


class NLPAnalysisContractTestCase(unittest.TestCase):

    def test_contrato_incluye_todas_las_claves(self):
        analysis = build_nlp_analysis()
        self.assertIn("schema_version", analysis)
        self.assertIn("intent", analysis)
        self.assertIn("need", analysis)
        self.assertIn("entities", analysis)
        self.assertIn("preferences", analysis)
        self.assertIn("exclusions", analysis)
        self.assertIn("context", analysis)
        self.assertIn("decision", analysis)
        self.assertIn("metadata", analysis)

    def test_contrato_es_serializable(self):
        payload = json.dumps(build_nlp_analysis())
        self.assertIsInstance(payload, str)

    def test_modificar_un_campo_no_elimina_los_demas(self):
        analysis = build_nlp_analysis({
            "intent": {"value": "consultar_stock", "confidence": 0.8}
        })
        self.assertEqual(analysis["intent"]["value"], "consultar_stock")
        self.assertEqual(analysis["intent"]["confidence"], 0.8)
        self.assertEqual(analysis["entities"]["quantity"], 1)

    def test_entity_candidates_antiguo_dict_se_normaliza(self):
        analysis = normalize_nlp_analysis({
            "metadata": {
                "entity_candidates": {
                    "products": ["Galletas Oreo"]
                }
            }
        })
        self.assertIsInstance(analysis["metadata"]["entity_candidates"], list)
        self.assertEqual(analysis["metadata"]["entity_candidates"][0]["entity_type"], "product")

    def test_intent_antiguo_string_se_normaliza(self):
        analysis = normalize_nlp_analysis({"intent": "buscar_producto", "confidence": 0.8})
        self.assertEqual(get_intent_value(analysis), "buscar_producto")
        self.assertEqual(get_intent_confidence(analysis), 0.8)

    def test_ausencia_de_confidence_devuelve_cero(self):
        self.assertEqual(get_intent_confidence({"intent": "buscar_producto"}), 0.0)

    def test_metadata_ausente_se_completa(self):
        analysis = normalize_nlp_analysis({})
        self.assertIn("entity_candidates", analysis["metadata"])
        self.assertIsInstance(analysis["metadata"]["entity_candidates"], list)

    def test_exclusions_incompletas_se_completan(self):
        analysis = normalize_nlp_analysis({"exclusions": {"brands": ["Gloria"]}})
        self.assertIn("product_ids", analysis["exclusions"])
        self.assertIn("category_ids", analysis["exclusions"])
        self.assertEqual(analysis["exclusions"]["brands"], ["Gloria"])


class ConversacionRepositoryNLPTestCase(unittest.TestCase):

    def setUp(self):
        self.repository = ConversacionRepository()

    @patch("repositories.conversacion_repository.supabase")
    def test_actualiza_intent_confidence_y_nlp_analysis(self, supabase_mock):
        response = MagicMock()
        response.data = [{"id": "MSG1"}]
        supabase_mock.table.return_value.update.return_value.eq.return_value.execute.return_value = response

        result = self.repository.actualizar_analisis_mensaje(
            message_id="MSG1",
            intent="consultar_stock",
            intent_confidence=0.9,
            nlp_method="rules+catalog",
            nlp_analysis=build_nlp_analysis({"intent": {"value": "consultar_stock"}}),
            processing_status="processed"
        )

        payload = supabase_mock.table.return_value.update.call_args.args[0]
        self.assertTrue(result["success"])
        self.assertEqual(payload["intent_confidence"], 0.9)
        self.assertEqual(payload["nlp_analysis"]["intent"]["value"], "consultar_stock")

    @patch("repositories.conversacion_repository.supabase")
    def test_fallo_deja_processing_status_failed(self, supabase_mock):
        response = MagicMock()
        response.data = [{"id": "MSG1"}]
        supabase_mock.table.return_value.update.return_value.eq.return_value.execute.return_value = response

        result = self.repository.marcar_mensaje_como_fallido("MSG1", "trace interna\nsecret")

        payload = supabase_mock.table.return_value.update.call_args.args[0]
        self.assertTrue(result["success"])
        self.assertEqual(payload["processing_status"], "failed")
        self.assertEqual(payload["nlp_analysis"]["metadata"]["errors"], ["trace interna"])

    @patch("repositories.conversacion_repository.supabase")
    def test_context_state_vacio_se_interpreta_como_dict(self, supabase_mock):
        response = MagicMock()
        response.data = {"context_state": None}
        supabase_mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = response
        self.assertEqual(self.repository.obtener_context_state("CONV1"), {})

    @patch("repositories.conversacion_repository.supabase")
    def test_clarification_count_nunca_baja_de_cero(self, supabase_mock):
        response_select = MagicMock()
        response_select.data = {"clarification_count": -5}
        response_update = MagicMock()
        response_update.data = [{"id": "CONV1", "clarification_count": 1}]
        supabase_mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = response_select
        supabase_mock.table.return_value.update.return_value.eq.return_value.execute.return_value = response_update
        self.repository.incrementar_clarification_count("CONV1")
        payload = supabase_mock.table.return_value.update.call_args.args[0]
        self.assertGreaterEqual(payload["clarification_count"], 0)


class NLPDynamicCatalogTestCase(unittest.TestCase):

    def setUp(self):
        self.nlp_service = MagicMock()
        self.nlp_service.normalize_text.side_effect = lambda text: (
            str(text or "")
            .lower()
            .replace("’", "'")
            .replace("`", "'")
            .replace("-", " ")
            .replace("'", "")
        )
        self.catalog_context = {
            "categories": [
                {"id": "C1", "name": "Bebidas", "description": "Agua, jugos y gaseosas"},
                {"id": "C2", "name": "Dulces", "description": "Galletas, chocolates y helados"},
                {"id": "C3", "name": "Snacks", "description": "Piqueos y comida ligera"},
            ],
            "products": [
                {"id": "P1", "name": "Agua San Luis 625ml", "brand": "San Luis", "category_id": "C1", "description": "Agua sin gas", "price": 3.5, "stock": 8, "is_active": True},
                {"id": "P2", "name": "Inca Kola 500ml", "brand": "Inca Kola", "category_id": "C1", "description": "Bebida con gas", "price": 4.5, "stock": 10, "is_active": True},
                {"id": "P3", "name": "Galletas Oreo", "brand": "Oreo", "category_id": "C2", "description": "Galletas dulces", "price": 2.5, "stock": 15, "is_active": True},
                {"id": "P4", "name": "Helado D'Onofrio", "brand": "D'Onofrio", "category_id": "C2", "description": "Helado dulce", "price": 5.0, "stock": 6, "is_active": True},
                {"id": "P5", "name": "Leche Gloria", "brand": "Gloria", "category_id": "C1", "description": "Lacteo", "price": 4.2, "stock": 7, "is_active": True},
                {"id": "P6", "name": "Yogurt Gloria Fresa", "brand": "Gloria", "category_id": "C1", "description": "Yogurt", "price": 4.8, "stock": 5, "is_active": True},
            ],
            "promotions": [
                {"id": "PR1", "title": "Promo Lay's", "description": "Descuento en Lay's", "promotion_type": "discount"},
            ],
            "promotion_items": [],
            "products_by_id": {},
            "promotions_by_id": {},
            "category_by_id": {
                "C1": {"id": "C1", "name": "Bebidas"},
                "C2": {"id": "C2", "name": "Dulces"},
                "C3": {"id": "C3", "name": "Snacks"},
            },
            "brands": {
                "san luis": "San Luis",
                "sanluis": "San Luis",
                "donofrio": "D'Onofrio",
                "gloria": "Gloria",
                "oreo": "Oreo",
                "lays": "Lay's",
            },
            "promotion_products": {},
            "cache_used": False,
        }
        catalog_service = MagicMock()
        catalog_service.get_context.return_value = self.catalog_context
        self.orchestrator = NLPOrchestrator(self.nlp_service, catalog_context_service=catalog_service)
        self.policy = ClarificationPolicy()

    def _orchestrate(self, text, analysis=None):
        self.nlp_service.analyze.return_value = analysis or {
            "intent": "consulta_general",
            "confidence": 0.3,
            "method": "rules",
            "normalized_text": self.nlp_service.normalize_text(text),
            "entities": {}
        }
        return self.orchestrator.orchestrate(text, "CONV1", {})

    def test_tengo_sed(self):
        result = self._orchestrate("Tengo sed")
        decision = self.policy.evaluate(result["contract"], {}, 0)
        self.assertEqual(result["contract"]["need"]["value"], "sed")
        self.assertEqual(result["contract"]["entities"]["category_id"], "C1")
        self.assertFalse(decision["requires_clarification"])

    def test_tengo_hambre_y_solo_tengo_8_soles(self):
        result = self._orchestrate("Tengo hambre y solo tengo 8 soles")
        self.assertEqual(result["contract"]["need"]["value"], "hambre")
        self.assertEqual(result["contract"]["entities"]["budget_max"], 8.0)

    def test_que_tienes_de_gloria(self):
        result = self._orchestrate("¿Qué tienes de Gloria?", {
            "intent": "buscar_producto",
            "confidence": 0.8,
            "method": "rules",
            "normalized_text": "que tienes de gloria",
            "entities": {}
        })
        decision = self.policy.evaluate(result["contract"], {}, 0)
        self.assertEqual(result["contract"]["entities"]["brand"], "Gloria")
        self.assertFalse(decision["requires_clarification"])

    def test_productos_sanluis(self):
        result = self._orchestrate("Productos sanluis", {
            "intent": "buscar_producto",
            "confidence": 0.7,
            "method": "rules",
            "normalized_text": "productos sanluis",
            "entities": {}
        })
        self.assertEqual(result["contract"]["entities"]["brand"], "San Luis")

    def test_tienes_donofrio(self):
        result = self._orchestrate("Tienes donofrio?", {
            "intent": "buscar_producto",
            "confidence": 0.7,
            "method": "rules",
            "normalized_text": "tienes donofrio",
            "entities": {}
        })
        self.assertEqual(result["contract"]["entities"]["brand"], "D'Onofrio")

    def test_quiero_dos_aguas_san_luis_por_menos_de_10_soles(self):
        result = self._orchestrate("Quiero dos aguas San Luis por menos de 10 soles", {
            "intent": "buscar_producto",
            "confidence": 0.8,
            "method": "rules",
            "normalized_text": "quiero dos aguas san luis por menos de 10 soles",
            "entities": {}
        })
        self.assertEqual(result["contract"]["entities"]["quantity"], 2)
        self.assertEqual(result["contract"]["entities"]["brand"], "San Luis")
        self.assertEqual(result["contract"]["entities"]["budget_max"], 10.0)

    def test_cuanto_cuesta_inca_kola_500ml(self):
        result = self._orchestrate("¿Cuánto cuesta Inca Kola 500ml?", {
            "intent": "consultar_precio",
            "confidence": 0.9,
            "method": "rules",
            "normalized_text": "cuanto cuesta inca kola 500ml",
            "entities": {}
        })
        self.assertEqual(result["contract"]["entities"]["product_name"], "Inca Kola 500ml")

    def test_cuanto_cuesta_gloria_requiere_aclaracion(self):
        result = self._orchestrate("¿Cuánto cuesta Gloria?", {
            "intent": "consultar_precio",
            "confidence": 0.8,
            "method": "rules",
            "normalized_text": "cuanto cuesta gloria",
            "entities": {}
        })
        decision = self.policy.evaluate(result["contract"], {}, 0)
        self.assertTrue(decision["requires_clarification"])

    def test_hay_promociones_de_lays(self):
        result = self._orchestrate("¿Hay promociones de Lay's?", {
            "intent": "consultar_promocion",
            "confidence": 0.9,
            "method": "rules",
            "normalized_text": "hay promociones de lays",
            "entities": {}
        })
        self.assertEqual(result["contract"]["entities"]["brand"], "Lay's")

    def test_no_quiero_coca_cola(self):
        self.catalog_context["products"].append(
            {"id": "P7", "name": "Coca-Cola 500ml", "brand": "Coca-Cola", "category_id": "C1", "description": "Bebida con gas", "price": 4.0, "stock": 5, "is_active": True}
        )
        result = self._orchestrate("No quiero Coca-Cola", {
            "intent": "buscar_producto",
            "confidence": 0.5,
            "method": "rules",
            "normalized_text": "no quiero coca cola",
            "entities": {}
        })
        self.assertIn("Coca-Cola 500ml", result["contract"]["exclusions"]["products"])

    def test_tengo_hambre_pero_no_quiero_dulces(self):
        result = self._orchestrate("Tengo hambre pero no quiero dulces", {
            "intent": "pedir_recomendacion",
            "confidence": 0.6,
            "method": "rules",
            "normalized_text": "tengo hambre pero no quiero dulces",
            "entities": {}
        })
        self.assertEqual(result["contract"]["need"]["value"], "hambre")
        self.assertIn("Dulces", result["contract"]["exclusions"]["categories"])

    def test_algo_barato_para_compartir(self):
        result = self._orchestrate("Algo barato para compartir", {
            "intent": "pedir_recomendacion",
            "confidence": 0.6,
            "method": "rules",
            "normalized_text": "algo barato para compartir",
            "entities": {}
        })
        self.assertIn("economic", result["contract"]["preferences"])
        self.assertIn("sharing", result["contract"]["preferences"])

    def test_palabra_desconocida_no_inventa(self):
        result = self._orchestrate("zxqplm")
        self.assertIsNone(result["contract"]["entities"]["product_id"])
        self.assertIsNone(result["contract"]["entities"]["brand"])

    def test_ambiguedad_difusa(self):
        self.catalog_context["products"].append(
            {"id": "P8", "name": "Inca Cola 500ml", "brand": "Inca Cola", "category_id": "C1", "description": "Bebida", "price": 4.4, "stock": 5, "is_active": True}
        )
        result = self._orchestrate("cuanto cuesta inca cola 500", {
            "intent": "consultar_precio",
            "confidence": 0.8,
            "method": "rules",
            "normalized_text": "cuanto cuesta inca cola 500",
            "entities": {}
        })
        decision = self.policy.evaluate(result["contract"], {}, 0)
        self.assertTrue(decision["requires_clarification"])

    def test_cache_evita_consultar_supabase_cada_vez(self):
        repository = MagicMock()
        repository.listar_categorias.return_value = self.catalog_context["categories"]
        repository.listar_productos.return_value = self.catalog_context["products"]
        repository.listar_promociones_activas.return_value = self.catalog_context["promotions"]
        repository.listar_items_promocion.return_value = []
        service = CatalogContextService(repository, normalizer=lambda value: str(value or "").lower())
        service.get_context()
        service.get_context()
        repository.listar_categorias.assert_called_once()

    def test_contrato_persistido_conserva_claves(self):
        result = self._orchestrate("Tengo sed")
        self.assertIn("metadata", result["contract"])
        self.assertIn("decision", result["contract"])

    def test_entity_candidates_lista_no_produce_attribute_error(self):
        decision = self.policy.evaluate(normalize_nlp_analysis({
            "intent": {"value": "buscar_producto", "confidence": 0.8},
            "metadata": {
                "entity_candidates": [
                    {"entity_type": "product", "value": "Galletas Oreo"},
                    {"entity_type": "product", "value": "Galletas Casino"},
                ]
            }
        }), {}, 0)
        self.assertTrue(decision["requires_clarification"])

    def test_clarification_policy_acepta_lista_vacia(self):
        decision = self.policy.evaluate(normalize_nlp_analysis({
            "metadata": {"entity_candidates": []}
        }), {}, 0)
        self.assertIn("requires_clarification", decision)


if __name__ == "__main__":
    unittest.main()
