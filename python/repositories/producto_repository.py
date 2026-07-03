from config.supabase_client import supabase


class ProductoRepository:

    def listar_productos(self, limite=20):
        query = (
            supabase
            .table("cat_products")
            .select("*")
            .eq("is_active", True)
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
            .eq("is_active", True)
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
            .eq("is_active", True)
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
            .eq("is_active", True)
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
            .eq("is_active", True)
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
