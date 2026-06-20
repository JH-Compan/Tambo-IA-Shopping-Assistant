from repositories.producto_repository import ProductoRepository
from services.availability_service import AvailabilityService


class ProductoService:

    def __init__(self):
        self.producto_repository = ProductoRepository()
        self.availability_service = AvailabilityService()

    def listar_productos(self):
        return self.availability_service.listar_productos_disponibles()

    def listar_categorias(self):
        return self.producto_repository.listar_categorias()

    def buscar_productos(self, texto):
        if not texto or len(texto.strip()) < 2:
            return []

        productos = self.producto_repository.buscar_productos_por_nombre(texto)
        return self.availability_service.filter_products(productos)

    def listar_promociones(self, user_id=None):
        return self.availability_service.listar_promociones_disponibles(user_id=user_id)
