from repositories.producto_repository import ProductoRepository
from repositories.recomendacion_repository import RecomendacionRepository


class RecomendacionService:

    def __init__(self):
        self.producto_repository = ProductoRepository()
        self.recomendacion_repository = RecomendacionRepository()

    def recomendar_productos(self, mensaje, conversation_id=None):
        texto = mensaje.lower()

        if any(p in texto for p in ["promo", "promoción", "oferta", "descuento"]):
            return {
                "tipo": "promociones",
                "items": self.producto_repository.listar_promociones_activas(limite=5),
                "razon": "El usuario solicitó promociones u ofertas."
            }

        if any(p in texto for p in ["barato", "económico", "economico", "menor precio"]):
            productos = self.producto_repository.listar_productos_ordenados_por_precio(limite=5)
            return {
                "tipo": "productos",
                "items": productos,
                "razon": "El usuario mostró interés por productos económicos."
            }

        categorias = self.producto_repository.listar_categorias()

        for categoria in categorias:
            nombre_categoria = categoria["name"].lower()

            if nombre_categoria in texto:
                productos = self.producto_repository.buscar_productos_por_categoria_id(
                    categoria["id"],
                    limite=5
                )

                return {
                    "tipo": "productos",
                    "items": productos,
                    "razon": f"El usuario mencionó la categoría {categoria['name']}."
                }

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

        productos = self.producto_repository.listar_productos(limite=5)

        return {
            "tipo": "productos",
            "items": productos,
            "razon": "No se detectó una categoría específica; se muestran productos generales."
        }

    def guardar_recomendaciones_generadas(self, conversation_id, productos, razon):
        recomendaciones_guardadas = []

        for index, producto in enumerate(productos[:5]):
            score = round(0.95 - (index * 0.08), 2)

            recomendacion = self.recomendacion_repository.guardar_recomendacion_producto(
                conversation_id=conversation_id,
                product_id=producto["id"],
                score=score,
                reason=razon
            )

            recomendaciones_guardadas.append(recomendacion)

        return recomendaciones_guardadas

    def registrar_interacciones_recomendadas(self, user_id, conversation_id, productos):
        for producto in productos[:5]:
            self.recomendacion_repository.guardar_interaccion_producto(
                user_id=user_id,
                conversation_id=conversation_id,
                interaction_type="recommended",
                product_id=producto["id"],
                weight=0.5
            )