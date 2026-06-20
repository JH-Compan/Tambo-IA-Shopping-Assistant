from datetime import datetime, timedelta

from repositories.producto_repository import ProductoRepository


class CatalogContextService:
    CACHE_TTL = timedelta(minutes=5)

    def __init__(self, producto_repository=None, normalizer=None):
        self.producto_repository = producto_repository or ProductoRepository()
        self.normalizer = normalizer or (lambda value: str(value or "").strip().lower())
        self._cache = None
        self._expires_at = None

    def get_context(self):
        now = datetime.now()
        if self._cache and self._expires_at and now < self._expires_at:
            cached = dict(self._cache)
            cached["cache_used"] = True
            return cached

        try:
            categories = self.producto_repository.listar_categorias() or []
            products = self.producto_repository.listar_productos(limite=None) or []
            promotions = self.producto_repository.listar_promociones_activas(limite=None) or []
            promotion_items = self.producto_repository.listar_items_promocion() or []
            context = self._build_context(categories, products, promotions, promotion_items)
            self._cache = context
            self._expires_at = now + self.CACHE_TTL
            fresh = dict(context)
            fresh["cache_used"] = False
            return fresh
        except Exception:
            if self._cache:
                cached = dict(self._cache)
                cached["cache_used"] = True
                return cached
            raise

    def invalidate_cache(self):
        self._cache = None
        self._expires_at = None

    def _build_context(self, categories, products, promotions, promotion_items):
        category_by_id = {item.get("id"): item for item in categories if item.get("id")}
        products_by_id = {item.get("id"): item for item in products if item.get("id")}
        promotions_by_id = {item.get("id"): item for item in promotions if item.get("id")}
        brands = {}
        for product in products:
            brand = str(product.get("brand") or "").strip()
            if brand:
                brands[self.normalizer(brand)] = brand

        promotion_products = {}
        for item in promotion_items:
            promotion_id = item.get("promotion_id")
            product_id = item.get("product_id")
            if not promotion_id or not product_id:
                continue
            promotion_products.setdefault(promotion_id, []).append(products_by_id.get(product_id))

        return {
            "categories": categories,
            "products": products,
            "promotions": promotions,
            "promotion_items": promotion_items,
            "category_by_id": category_by_id,
            "products_by_id": products_by_id,
            "promotions_by_id": promotions_by_id,
            "brands": brands,
            "promotion_products": promotion_products,
        }
