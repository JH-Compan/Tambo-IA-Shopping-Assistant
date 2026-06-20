from datetime import date

from repositories.producto_repository import ProductoRepository


class AvailabilityService:

    def __init__(self):
        self.producto_repository = ProductoRepository()

    def evaluate_item(self, item_type, item_id, requested_quantity=1, user_id=None):
        normalized_type = str(item_type or "").strip().lower()
        quantity = max(1, int(requested_quantity or 1))

        if normalized_type == "promotion":
            promocion = self.producto_repository.obtener_promocion_por_id(item_id)
            return self._evaluate_promotion(promocion, requested_quantity=quantity, user_id=user_id)

        producto = self.producto_repository.obtener_producto_por_id(item_id)
        return self._evaluate_product(producto, requested_quantity=quantity)

    def listar_productos_disponibles(self, limite=None):
        return self.filter_products(self.producto_repository.listar_productos(limite=limite), quantity=1)

    def listar_promociones_disponibles(self, user_id=None, limite=None):
        promociones = self.producto_repository.listar_promociones_activas(limite=limite)
        return self.filtrar_promociones_disponibles(promociones, user_id=user_id, quantity=1)

    def filter_products(self, productos, quantity=1):
        return [
            producto for producto in (productos or [])
            if self._evaluate_product(producto, requested_quantity=quantity)["available"]
        ]

    def filtrar_promociones_disponibles(self, promociones, user_id=None, quantity=1):
        products_by_id = self._build_products_by_id()
        promotion_items_map = self._build_promotion_items_map()
        return [
            promocion for promocion in (promociones or [])
            if self._evaluate_promotion(
                promocion,
                requested_quantity=quantity,
                user_id=user_id,
                products_by_id=products_by_id,
                promotion_items_map=promotion_items_map
            )["available"]
        ]

    def validate_item_availability(self, item_type, item_id, quantity=1, user_id=None):
        return self.evaluate_item(
            item_type=item_type,
            item_id=item_id,
            requested_quantity=quantity,
            user_id=user_id
        )

    def _evaluate_product(self, producto, requested_quantity=1):
        requested_quantity = max(1, int(requested_quantity or 1))
        if not isinstance(producto, dict):
            return self._result(
                available=False,
                reason_code="not_found",
                reason="El producto no existe.",
                available_quantity=0,
                requested_quantity=requested_quantity
            )
        if not producto.get("is_active", False):
            return self._result(
                available=False,
                reason_code="inactive_product",
                reason="El producto no esta activo.",
                available_quantity=producto.get("stock") or 0,
                requested_quantity=requested_quantity
            )

        price = producto.get("price")
        if price is None or price <= 0:
            return self._result(
                available=False,
                reason_code="invalid_price",
                reason="El producto no tiene un precio valido.",
                available_quantity=producto.get("stock") or 0,
                requested_quantity=requested_quantity
            )

        available_stock = int(producto.get("stock") or 0)
        if available_stock < requested_quantity:
            return self._result(
                available=False,
                reason_code="insufficient_stock",
                reason="El producto no tiene stock suficiente.",
                available_quantity=available_stock,
                requested_quantity=requested_quantity
            )

        return self._result(
            available=True,
            available_quantity=available_stock,
            requested_quantity=requested_quantity
        )

    def _evaluate_promotion(
        self,
        promocion,
        requested_quantity=1,
        user_id=None,
        products_by_id=None,
        promotion_items_map=None
    ):
        requested_quantity = max(1, int(requested_quantity or 1))
        if not isinstance(promocion, dict):
            return self._result(
                available=False,
                reason_code="not_found",
                reason="La promocion no existe.",
                requested_quantity=requested_quantity
            )
        if not promocion.get("is_active", False):
            return self._result(
                available=False,
                reason_code="inactive_promotion",
                reason="La promocion no esta activa.",
                requested_quantity=requested_quantity
            )
        if not self._is_current(promocion):
            return self._result(
                available=False,
                reason_code="promotion_out_of_date",
                reason="La promocion no esta vigente.",
                requested_quantity=requested_quantity
            )
        if user_id and self._limit_reached(promocion, user_id=user_id, quantity=requested_quantity):
            return self._result(
                available=False,
                reason_code="customer_limit_reached",
                reason="El usuario ya alcanzo el limite por cliente de esta promocion.",
                requested_quantity=requested_quantity
            )

        promotion_items = (
            promotion_items_map.get(promocion.get("id"), [])
            if isinstance(promotion_items_map, dict)
            else []
        )
        if not promotion_items:
            promotion_items = [
                item for item in (self.producto_repository.listar_items_promocion() or [])
                if item.get("promotion_id") == promocion.get("id")
            ]
        if not promotion_items:
            return self._result(
                available=False,
                reason_code="promotion_without_items",
                reason="La promocion no tiene productos asociados.",
                requested_quantity=requested_quantity
            )

        products_by_id = products_by_id or self._build_products_by_id()
        unavailable_products = []
        min_available_quantity = None

        for promotion_item in promotion_items:
            required_quantity = int(promotion_item.get("quantity") or 0)
            if required_quantity < 1:
                unavailable_products.append({
                    "product_id": promotion_item.get("product_id"),
                    "required_quantity": required_quantity * requested_quantity,
                    "available_stock": 0
                })
                continue

            producto = products_by_id.get(promotion_item.get("product_id"))
            product_result = self._evaluate_product(
                producto,
                requested_quantity=required_quantity * requested_quantity
            )
            if not product_result["available"]:
                unavailable_products.append({
                    "product_id": promotion_item.get("product_id"),
                    "required_quantity": required_quantity * requested_quantity,
                    "available_stock": product_result["details"].get("available_quantity") or 0
                })
                continue

            stock = int((producto or {}).get("stock") or 0)
            item_available_quantity = stock // required_quantity
            if min_available_quantity is None or item_available_quantity < min_available_quantity:
                min_available_quantity = item_available_quantity

        if unavailable_products:
            return self._result(
                available=False,
                reason_code="insufficient_stock",
                reason="Esta promocion ya no esta disponible.",
                available_quantity=min_available_quantity,
                requested_quantity=requested_quantity,
                unavailable_products=unavailable_products
            )

        return self._result(
            available=True,
            available_quantity=min_available_quantity,
            requested_quantity=requested_quantity
        )

    def _result(
        self,
        available,
        reason_code=None,
        reason=None,
        available_quantity=None,
        requested_quantity=1,
        unavailable_products=None
    ):
        return {
            "available": bool(available),
            "reason_code": reason_code,
            "reason": reason,
            "details": {
                "available_quantity": available_quantity,
                "requested_quantity": max(1, int(requested_quantity or 1)),
                "unavailable_products": list(unavailable_products or [])
            }
        }

    def _build_products_by_id(self):
        return {
            producto.get("id"): producto
            for producto in (self.producto_repository.listar_productos(limite=None) or [])
            if producto.get("id")
        }

    def _build_promotion_items_map(self):
        result = {}
        for item in (self.producto_repository.listar_items_promocion() or []):
            promotion_id = item.get("promotion_id")
            if not promotion_id:
                continue
            result.setdefault(promotion_id, []).append(item)
        return result

    def _is_current(self, promocion):
        today = date.today()
        start_date = self._to_date(promocion.get("start_date"))
        end_date = self._to_date(promocion.get("end_date"))
        if start_date and today < start_date:
            return False
        if end_date and today > end_date:
            return False
        return True

    def _limit_reached(self, promocion, user_id, quantity):
        max_per_customer = promocion.get("max_per_customer")
        if max_per_customer is None:
            return False
        purchased = self.producto_repository.obtener_cantidad_promocion_comprada_por_usuario(
            user_id=user_id,
            promotion_id=promocion.get("id")
        )
        return purchased + max(1, int(quantity or 1)) > int(max_per_customer)

    def _to_date(self, value):
        try:
            return date.fromisoformat(str(value)) if value else None
        except Exception:
            return None
