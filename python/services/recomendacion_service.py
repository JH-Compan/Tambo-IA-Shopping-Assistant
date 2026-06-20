from repositories.producto_repository import ProductoRepository
from repositories.recomendacion_repository import RecomendacionRepository


class RecomendacionService:

    def __init__(self):
        self.producto_repository = ProductoRepository()
        self.recomendacion_repository = RecomendacionRepository()

    def recomendar_productos(self, mensaje, conversation_id=None):
        texto = mensaje.lower().strip()

        # 0. Si el mensaje es el botón genérico "Mi recomendación IA"
        #    (o frases equivalentes sin un producto específico),
        #    se muestra una recomendación real: promociones vigentes
        #    primero: si no hay, productos destacados.
        frases_genericas = [
            "mi recomendacion ia", "mi recomendación ia",
            "recomiendame", "recomiéndame",
            "recomendacion", "recomendación",
            "que me recomiendas", "qué me recomiendas",
            "ia"
        ]
        texto_sin_tildes = (
            texto.replace("á", "a").replace("é", "e")
                 .replace("í", "i").replace("ó", "o").replace("ú", "u")
        )
        if texto_sin_tildes in [f.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u") for f in frases_genericas]:
            return self._recomendacion_general()

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

        # 1. Buscar coincidencia con el NOMBRE de alguna categoría real
        categorias = self.producto_repository.listar_categorias()

        for categoria in categorias:
            nombre_categoria = categoria["name"].lower()
            if nombre_categoria in texto:
                productos = self.producto_repository.buscar_productos_por_categoria_id(
                    categoria["id"], limite=10
                )
                if productos:
                    return {
                        "tipo": "productos",
                        "items": productos,
                        "razon": f"El usuario mencionó la categoría {categoria['name']}."
                    }

        # 2. Buscar directamente por CADA PALABRA que escribió el usuario
        #    contra el nombre real de los productos en Supabase.
        palabras = [w for w in texto.split() if len(w) > 2]

        variantes = set(palabras)
        for w in palabras:
            if w.endswith("s") and len(w) > 3:
                variantes.add(w[:-1])

        for palabra in variantes:
            productos = self.producto_repository.buscar_productos_por_nombre(palabra, limite=10)
            if productos:
                return {
                    "tipo": "productos",
                    "items": productos,
                    "razon": f"El usuario buscó '{palabra}' y se encontraron coincidencias por nombre."
                }

        # 3. Buscar también por palabra dentro de la DESCRIPCIÓN
        for palabra in variantes:
            productos = self._buscar_por_descripcion(palabra, limite=10)
            if productos:
                return {
                    "tipo": "productos",
                    "items": productos,
                    "razon": f"El usuario mencionó '{palabra}', relacionado con la descripción de estos productos."
                }

        # 4. Si de verdad no hay coincidencia con nada de lo que escribió,
        #    en vez de decir "no encontré nada", se cae a una
        #    recomendación general (promociones o destacados).
        return self._recomendacion_general()

    def _recomendacion_general(self):
        """
        Recomendación de respaldo cuando el usuario pide una
        recomendación genérica o cuando no hubo match con su mensaje.
        Prioridad: promociones activas → si no hay, productos destacados.
        """
        promociones = self.producto_repository.listar_promociones_activas(limite=5)
        if promociones:
            return {
                "tipo": "promociones",
                "items": promociones,
                "razon": "Recomendación general: promociones vigentes en este momento."
            }

        productos = self.producto_repository.listar_productos(limite=5)
        return {
            "tipo": "productos",
            "items": productos,
            "razon": "Recomendación general: no hay promociones activas, se muestran productos disponibles."
        }

    def _buscar_por_descripcion(self, texto, limite=10):
        """Busca productos cuya descripción contenga la palabra dada."""
        from config.supabase_client import supabase
        response = (
            supabase
            .table("cat_products")
            .select("*")
            .eq("is_active", True)
            .ilike("description", f"%{texto}%")
            .limit(limite)
            .execute()
        )
        return response.data

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