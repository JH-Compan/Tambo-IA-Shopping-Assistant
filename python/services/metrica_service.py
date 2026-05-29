from config.supabase_client import supabase


class MetricaService:

    def contar_registros(self, tabla):
        response = (
            supabase
            .table(tabla)
            .select("id")
            .execute()
        )
        return len(response.data)

    def obtener_resumen_general(self):
        return {
            "usuarios": self.contar_registros("chat_users"),
            "conversaciones": self.contar_registros("chat_conversations"),
            "mensajes": self.contar_registros("chat_messages"),
            "productos": self.contar_registros("cat_products"),
            "promociones": self.contar_registros("cat_promotions"),
            "pedidos": self.contar_registros("sales_orders"),
            "recomendaciones": self.contar_registros("ai_recommendations"),
            "feedback": self.contar_registros("ai_feedback")
        }