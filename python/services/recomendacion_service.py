from repositories.producto_repository import ProductoRepository
from repositories.recomendacion_repository import RecomendacionRepository


class RecomendacionService:

    def __init__(self):
        self.producto_repository = ProductoRepository()
        self.recomendacion_repository = RecomendacionRepository()

    def recomendar_productos(self, mensaje, conversation_id=None, analysis=None):
        texto = mensaje.lower()
        analysis = analysis or {}
        intent = analysis.get("intent", "consulta_general")
        entities = analysis.get("entities", {})
        product_name = entities.get("product_name")
        category_name = entities.get("category")
        preference = entities.get("preference")
        budget_max = entities.get("budget_max")
        budget_min = entities.get("budget_min")

        if intent == "consultar_promocion":
            return {
                "tipo": "promociones",
                "items": self.producto_repository.listar_promociones_activas(limite=5),
                "razon": "El usuario solicitó promociones u ofertas."
            }

        if intent == "consultar_precio":
            return {
                "tipo": "productos",
                "items": self._resolver_productos(product_name, category_name),
                "razon": "El usuario consultó precios de productos."
            }

        if intent == "consultar_stock":
            return {
                "tipo": "productos",
                "items": self._resolver_productos(product_name, category_name),
                "razon": "El usuario consultó disponibilidad de productos."
            }

        if intent == "pedir_recomendacion" and preference == "economico":
            productos = self.producto_repository.listar_productos_ordenados_por_precio(limite=10)
            return self._filtrar_por_presupuesto(
                productos=productos,
                budget_min=budget_min,
                budget_max=budget_max,
                razon="El usuario mostró interés por productos económicos."
            )

        if intent == "confirmar_interes" and product_name:
            productos = self.producto_repository.buscar_productos_por_nombre(product_name, limite=5)
            return {
                "tipo": "productos",
                "items": productos,
                "razon": "El usuario confirmó interés en un producto."
            }

        if category_name:
            categorias = self.producto_repository.listar_categorias()
            for categoria in categorias:
                if categoria["name"].lower() == str(category_name).lower():
                    productos = self.producto_repository.buscar_productos_por_categoria_id(
                        categoria["id"],
                        limite=10
                    )
                    if budget_min is not None or budget_max is not None:
                        return self._filtrar_por_presupuesto(
                            productos=productos,
                            budget_min=budget_min,
                            budget_max=budget_max,
                            razon=f"El usuario mencionó la categoría {categoria['name']}."
                        )
                    return {
                        "tipo": "productos",
                        "items": productos[:5],
                        "razon": f"El usuario mencionó la categoría {categoria['name']}."
                    }

        if product_name:
            productos = self.producto_repository.buscar_productos_por_nombre(product_name, limite=5)
            if productos:
                return {
                    "tipo": "productos",
                    "items": productos,
                    "razon": f"El usuario mencionó el producto {product_name}."
                }

        if any(p in texto for p in ["barato", "económico", "economico", "menor precio"]):
            productos = self.producto_repository.listar_productos_ordenados_por_precio(limite=10)
            return self._filtrar_por_presupuesto(
                productos=productos,
                budget_min=budget_min,
                budget_max=budget_max,
                razon="El usuario mostró interés por productos económicos."
            )

        palabras_clave = {
            "bebida": ["bebida", "tomar", "gaseosa", "agua", "jugo"],
            "dulce": ["dulce", "chocolate", "galleta", "gomita", "caramelo"],
            "snack": ["snack", "papas", "piqueo", "salado"],
            "limpieza": ["limpieza", "jabón", "detergente", "papel"]
        }

        for _, palabras in palabras_clave.items():
            if any(palabra in texto for palabra in palabras):
                for palabra in palabras:
                    productos = self.producto_repository.buscar_productos_por_nombre(palabra, limite=5)
                    if productos:
                        return {
                            "tipo": "productos",
                            "items": productos,
                            "razon": f"El usuario mencionó una necesidad relacionada con {palabra}."
                        }

        productos = self.producto_repository.listar_productos(limite=10)
        if budget_min is not None or budget_max is not None:
            return self._filtrar_por_presupuesto(
                productos=productos,
                budget_min=budget_min,
                budget_max=budget_max,
                razon="No se detectó una categoría específica; se aplicó el filtro de presupuesto."
            )

        return {
            "tipo": "productos",
            "items": productos[:5],
            "razon": "No se detectó una categoría específica; se muestran productos generales."
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

    def _resolver_productos(self, product_name, category_name):
        if product_name:
            productos = self.producto_repository.buscar_productos_por_nombre(product_name, limite=5)
            if productos:
                return productos

        if category_name:
            for categoria in self.producto_repository.listar_categorias():
                if categoria["name"].lower() == str(category_name).lower():
                    return self.producto_repository.buscar_productos_por_categoria_id(
                        categoria["id"],
                        limite=5
                    )

        return self.producto_repository.listar_productos(limite=5)

    def _filtrar_por_presupuesto(self, productos, budget_min, budget_max, razon):
        filtrados = []
        for producto in productos:
            price = producto.get("price")
            if price is None:
                continue
            if budget_min is not None and price < budget_min:
                continue
            if budget_max is not None and price > budget_max:
                continue
            filtrados.append(producto)

        if filtrados:
            return {
                "tipo": "productos",
                "items": filtrados[:5],
                "razon": razon
            }

        return {
            "tipo": "productos",
            "items": productos[:5],
            "razon": razon
        }
