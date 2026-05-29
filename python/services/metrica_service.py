"""
MetricaService
Genera estadísticas y métricas de uso del chatbot.
"""
from repositories import conversacion_repository, producto_repository


def obtener_metricas():
    """Retorna un resumen de métricas del sistema."""
    metricas_chat = conversacion_repository.obtener_metricas_interacciones()
    promociones = producto_repository.obtener_promociones_vigentes()
    productos_con_stock = producto_repository.obtener_productos_con_stock()
    todos = producto_repository.obtener_todos_los_productos()

    return {
        "total_interacciones": metricas_chat.get("total_interacciones", 0),
        "clientes_unicos": metricas_chat.get("clientes_unicos", 0),
        "promociones_activas": len(promociones),
        "productos_en_catalogo": len(todos),
        "productos_con_stock": len(productos_con_stock),
        "productos_agotados": len(todos) - len(productos_con_stock),
    }
