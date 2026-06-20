from config.supabase_client import supabase


class ProductoRepository:

    def listar_productos(self, limite=200):
        """
        Trae el catálogo completo de productos activos.
        Antes el límite era 20, lo que dejaba fuera productos del
        catálogo de forma arbitraria (Supabase no garantiza orden
        sin un .order() explícito). Ahora se sube el límite y se
        ordena por nombre para que el resultado sea predecible.
        """
        response = (
            supabase
            .table("cat_products")
            .select("*")
            .eq("is_active", True)
            .order("name")
            .limit(limite)
            .execute()
        )
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

    def buscar_productos_por_nombre(self, texto, limite=20):
        response = (
            supabase
            .table("cat_products")
            .select("*")
            .eq("is_active", True)
            .ilike("name", f"%{texto}%")
            .limit(limite)
            .execute()
        )
        return response.data

    def buscar_productos_por_categoria_id(self, category_id, limite=20):
        response = (
            supabase
            .table("cat_products")
            .select("*")
            .eq("category_id", category_id)
            .eq("is_active", True)
            .limit(limite)
            .execute()
        )
        return response.data

    def listar_productos_ordenados_por_precio(self, limite=10):
        response = (
            supabase
            .table("cat_products")
            .select("*")
            .eq("is_active", True)
            .order("price")
            .limit(limite)
            .execute()
        )
        return response.data

    def listar_promociones_activas(self, limite=10):
        response = (
            supabase
            .table("cat_promotions")
            .select("*")
            .eq("is_active", True)
            .limit(limite)
            .execute()
        )
        return response.data