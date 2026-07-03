from repositories.producto_repository import ProductoRepository
from repositories.recomendacion_repository import RecomendacionRepository
from services.availability_service import AvailabilityService


class RecomendacionService:

    def __init__(self):
        self.producto_repository = ProductoRepository()
        self.recomendacion_repository = RecomendacionRepository()
        self.availability_service = AvailabilityService()

    def recomendar_productos(self, mensaje, conversation_id=None, analysis=None, user_id=None):
        texto = str(mensaje or "").lower()
        analysis = analysis or {}
        intent = self._read_intent(analysis)
        entities = analysis.get("entities", {}) if isinstance(analysis.get("entities"), dict) else {}
        exclusions = analysis.get("exclusions", {}) if isinstance(analysis.get("exclusions"), dict) else {}
        preferences = analysis.get("preferences", []) if isinstance(analysis.get("preferences"), list) else []
        metadata = analysis.get("metadata", {}) if isinstance(analysis.get("metadata"), dict) else {}
        excluded_item_ids = set(metadata.get("excluded_item_ids", []) or [])

        product_id = entities.get("product_id")
        product_name = entities.get("product_name")
        brand = entities.get("brand")
        category_id = entities.get("category_id")
        category_name = entities.get("category_name") or entities.get("category")
        promotion_id = entities.get("promotion_id")
        promotion_type = entities.get("promotion_type")
        budget_min = entities.get("budget_min")
        budget_max = entities.get("budget_max")
        category_candidates = metadata.get("category_candidates", [])

        if intent == "consultar_promocion":
            promociones = self._filtrar_promociones(
                promociones=self.producto_repository.listar_promociones_activas(limite=None),
                promotion_id=promotion_id,
                promotion_type=promotion_type,
                brand=brand,
                product_name=product_name
            )
            promociones = self.availability_service.filtrar_promociones_disponibles(promociones, user_id=user_id)
            return {
                "tipo": "promociones",
                "items": self.availability_service.filtrar_promociones_disponibles(promociones[:5], user_id=user_id),
                "razon": "El usuario solicito promociones u ofertas."
            }

        if intent in {"consultar_precio", "consultar_stock", "confirmar_interes", "buscar_producto", "pedir_recomendacion"}:
            productos = self._resolver_productos(
                product_id=product_id,
                product_name=product_name,
                brand=brand,
                category_id=category_id,
                category_name=category_name,
                category_candidates=category_candidates,
                budget_min=budget_min,
                budget_max=budget_max,
                preferences=preferences,
                exclusions=exclusions,
                excluded_item_ids=excluded_item_ids
            )

            if intent == "pedir_recomendacion" and any(word in texto for word in ["barato", "economico", "económico"]) and "economic" not in preferences:
                preferences = preferences + ["economic"]

            if intent == "pedir_recomendacion" and "economic" in preferences:
                productos = sorted(productos, key=lambda item: item.get("price") or 0)

            productos = self.availability_service.filter_products(productos)
            if productos:
                return {
                    "tipo": "productos",
                    "items": self.availability_service.filter_products(productos[:5]),
                    "razon": "Se encontraron productos relacionados con la intención detectada."
                }

        productos = self._resolver_productos(
            product_id=None,
            product_name=None,
            brand=None,
            category_id=category_id,
            category_name=category_name,
            category_candidates=category_candidates,
            budget_min=budget_min,
            budget_max=budget_max,
            preferences=preferences,
            exclusions=exclusions,
            excluded_item_ids=excluded_item_ids
        )
        return {
            "tipo": "productos",
            "items": self.availability_service.filter_products(productos[:5]),
            "razon": "No se detecto una categoria especifica; se muestran productos generales."
        }

    def guardar_recomendaciones_generadas(self, conversation_id, productos, razon):
        return self.recomendacion_repository.guardar_recomendaciones_generadas(
            conversation_id=conversation_id,
            items=productos,
            item_type="product",
            reason=razon
        )

    def guardar_promociones_generadas(self, conversation_id, promociones, razon):
        return self.recomendacion_repository.guardar_recomendaciones_generadas(
            conversation_id=conversation_id,
            items=promociones,
            item_type="promotion",
            reason=razon
        )

    def registrar_interacciones_recomendadas(self, user_id, conversation_id, productos):
        return self.recomendacion_repository.guardar_interacciones_recomendadas(
            user_id=user_id,
            conversation_id=conversation_id,
            items=productos,
            item_type="product"
        )

    def registrar_interacciones_promociones(self, user_id, conversation_id, promociones):
        return self.recomendacion_repository.guardar_interacciones_recomendadas(
            user_id=user_id,
            conversation_id=conversation_id,
            items=promociones,
            item_type="promotion"
        )

    def marcar_recomendacion_seleccionada(self, recommendation_id):
        return self.recomendacion_repository.marcar_recomendacion_seleccionada(recommendation_id)

    def registrar_interaccion_item(self, user_id, conversation_id, item_id, item_type, interaction_type, weight=1):
        return self.recomendacion_repository.guardar_interaccion(
            user_id=user_id,
            conversation_id=conversation_id,
            item_id=item_id,
            item_type=item_type,
            interaction_type=interaction_type,
            weight=weight
        )

    def _resolver_productos(
        self,
        product_id,
        product_name,
        brand,
        category_id,
        category_name,
        category_candidates,
        budget_min,
        budget_max,
        preferences,
        exclusions,
        excluded_item_ids
    ):
        productos = self.availability_service.filter_products(
            self.producto_repository.listar_productos(limite=None) or []
        )
        filtrados = []
        for producto in productos:
            if product_id and producto.get("id") != product_id:
                continue
            if product_name and product_name.lower() not in str(producto.get("name", "")).lower():
                continue
            if brand and brand.lower() != str(producto.get("brand", "")).lower():
                continue
            if category_id and producto.get("category_id") != category_id:
                continue
            if self._is_excluded(producto, exclusions):
                continue
            if producto.get("id") in excluded_item_ids:
                continue
            if category_candidates and not category_id and not category_name:
                if not self._matches_category_candidates(producto, category_candidates):
                    continue
            if not self._matches_preferences(producto, preferences):
                continue
            if not self._matches_budget(producto, budget_min, budget_max):
                continue
            filtrados.append(producto)

        if filtrados:
            return filtrados

        if category_name and not category_id:
            categorias = self.producto_repository.listar_categorias() or []
            for categoria in categorias:
                if str(categoria.get("name", "")).lower() == str(category_name).lower():
                    return self._resolver_productos(
                        product_id,
                        product_name,
                        brand,
                        categoria.get("id"),
                        category_name,
                        category_candidates,
                        budget_min,
                        budget_max,
                        preferences,
                        exclusions,
                        excluded_item_ids
                    )

        return []

    def _filtrar_promociones(self, promociones, promotion_id, promotion_type, brand, product_name):
        promociones = promociones or []
        if not any([promotion_id, promotion_type, brand, product_name]):
            return promociones

        filtradas = []
        for promocion in promociones:
            if promotion_id and promocion.get("id") != promotion_id:
                continue
            if promotion_type and promocion.get("promotion_type") != promotion_type:
                continue
            haystack = f"{promocion.get('title', '')} {promocion.get('description', '')}".lower()
            if brand and brand.lower() not in haystack:
                continue
            if product_name and product_name.lower() not in haystack:
                continue
            filtradas.append(promocion)
        return filtradas

    def _is_excluded(self, producto, exclusions):
        return (
            producto.get("id") in set(exclusions.get("product_ids", []))
            or producto.get("category_id") in set(exclusions.get("category_ids", []))
            or producto.get("name") in set(exclusions.get("products", []))
            or producto.get("brand") in set(exclusions.get("brands", []))
            or str(producto.get("category_name") or "") in set(exclusions.get("categories", []))
        )

    def _matches_category_candidates(self, producto, category_candidates):
        category_candidates = {str(candidate).lower() for candidate in category_candidates}
        category_map = {
            str(category.get("id")): str(category.get("name", "")).lower()
            for category in (self.producto_repository.listar_categorias() or [])
        }
        category_name = category_map.get(str(producto.get("category_id")), "")
        return category_name in category_candidates

    def _matches_preferences(self, producto, preferences):
        description = str(producto.get("description", "")).lower()
        if "without_gas" in preferences and "con gas" in description:
            return False
        if "with_gas" in preferences and "sin gas" in description:
            return False
        if "sweet" in preferences and "dulce" not in description and "galleta" not in description:
            return False
        if "salty" in preferences and "salado" not in description:
            return False
        return True

    def _matches_budget(self, producto, budget_min, budget_max):
        price = producto.get("price")
        if price is None:
            return False
        if budget_min is not None and price < budget_min:
            return False
        if budget_max is not None and price > budget_max:
            return False
        return True

    def _read_intent(self, analysis):
        intent = analysis.get("intent", "consulta_general")
        if isinstance(intent, dict):
            return intent.get("value", "consulta_general")
        return intent
