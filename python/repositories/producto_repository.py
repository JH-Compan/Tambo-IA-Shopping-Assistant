from config.supabase_client import supabase


class ProductoRepository:

    def listar_productos(self, limite=20):
        query = (
            supabase
            .table("cat_products")
            .select("*")
        )
        if limite:
            query = query.limit(limite)
        response = query.execute()
        return response.data

    def listar_categorias(self):
        response = (
            supabase
            .table("cat_categories")
            .select("*")
            .eq("is_active", True)
            .execute()
        )
        return response.data

    def buscar_productos_por_nombre(self, texto, limite=10):
        query = (
            supabase
            .table("cat_products")
            .select("*")
            .ilike("name", f"%{texto}%")
        )
        if limite:
            query = query.limit(limite)
        response = query.execute()
        return response.data

    def buscar_productos_por_categoria_id(self, category_id, limite=10):
        query = (
            supabase
            .table("cat_products")
            .select("*")
            .eq("category_id", category_id)
        )
        if limite:
            query = query.limit(limite)
        response = query.execute()
        return response.data

    def listar_productos_ordenados_por_precio(self, limite=10):
        query = (
            supabase
            .table("cat_products")
            .select("*")
            .order("price")
        )
        if limite:
            query = query.limit(limite)
        response = query.execute()
        return response.data

    def listar_promociones_activas(self, limite=10):
        query = (
            supabase
            .table("cat_promotions")
            .select("*")
        )
        if limite:
            query = query.limit(limite)
        response = query.execute()
        return response.data

    def listar_items_promocion(self):
        response = (
            supabase
            .table("cat_promotion_items")
            .select("*")
            .execute()
        )
        return response.data

    def obtener_producto_por_id(self, product_id):
        response = (
            supabase
            .table("cat_products")
            .select("*")
            .eq("id", product_id)
            .limit(1)
            .execute()
        )
        return (response.data or [None])[0]

    def obtener_promocion_por_id(self, promotion_id):
        response = (
            supabase
            .table("cat_promotions")
            .select("*")
            .eq("id", promotion_id)
            .limit(1)
            .execute()
        )
        return (response.data or [None])[0]

    def obtener_cantidad_promocion_comprada_por_usuario(self, user_id, promotion_id):
        if not user_id or not promotion_id:
            return 0

        orders_response = (
            supabase
            .table("sales_orders")
            .select("id")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .execute()
        )
        order_ids = [row.get("id") for row in (orders_response.data or []) if row.get("id")]
        if not order_ids:
            return 0

        items_response = (
            supabase
            .table("sales_order_items")
            .select("quantity")
            .eq("promotion_id", promotion_id)
            .in_("order_id", order_ids)
            .execute()
        )
        return sum(int((row or {}).get("quantity") or 0) for row in (items_response.data or []))
