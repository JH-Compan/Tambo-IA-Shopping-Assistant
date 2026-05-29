from repositories.producto_repository import ProductoRepository


class ProductoService:

    def __init__(self):
        self.producto_repository = ProductoRepository()

    def listar_productos(self):
        return self.producto_repository.listar_productos()

    def listar_categorias(self):
        return self.producto_repository.listar_categorias()

    def buscar_productos(self, texto):
        if not texto or len(texto.strip()) < 2:
            return []

        return self.producto_repository.buscar_productos_por_nombre(texto)

    def listar_promociones(self):
        return self.producto_repository.listar_promociones_activas()