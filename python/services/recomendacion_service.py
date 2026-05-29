"""
RecomendacionService
Genera recomendaciones personalizadas según historial o popularidad.
"""
from repositories import conversacion_repository, producto_repository
from services import producto_service


def recomendar(telefono: str):
    """
    Punto de entrada principal.
    - Si el cliente tiene historial → recomendaciones personalizadas.
    - Si no tiene historial → productos populares (HU-03).
    Retorna un dict con: tipo, mensaje y lista de productos recomendados.
    """
    historial = conversacion_repository.obtener_historial_cliente(telefono)

    if historial:
        return _recomendar_por_historial(telefono)
    else:
        return _recomendar_populares()


def _recomendar_por_historial(telefono: str):
    """
    HU-04: Recomienda productos relacionados a los más comprados por el cliente.
    """
    frecuentes = conversacion_repository.obtener_productos_frecuentes(telefono, top=3)
    stock_todos = {s["id_producto"]: s["stock_disponible"]
                   for s in producto_repository.obtener_stock_todos()}

    recomendaciones = []
    for item in frecuentes:
        id_prod = item["id_producto"]
        stock_actual = stock_todos.get(id_prod, 0)

        if stock_actual > 0:
            # El producto tiene stock, lo recomendamos directamente
            todos = producto_repository.obtener_todos_los_productos()
            producto = next((p for p in todos if p["id_producto"] == id_prod), None)
            if producto:
                producto["stock"] = stock_actual
                producto["razon"] = "Lo compras frecuentemente"
                recomendaciones.append(producto)
        else:
            # Producto agotado → sugerir alternativa (HU-05)
            alternativa = producto_service.obtener_alternativa(id_prod)
            if alternativa:
                alternativa["razon"] = f"Alternativa a {item['nombre_producto']} (agotado)"
                recomendaciones.append(alternativa)

    return {
        "tipo": "personalizada",
        "mensaje": "Basado en tus compras anteriores, te recomendamos:",
        "productos": recomendaciones
    }


def _recomendar_populares():
    """
    HU-03: Para clientes sin historial, recomienda los más populares.
    """
    populares = producto_service.obtener_productos_populares()
    return {
        "tipo": "popular",
        "mensaje": "¡Hola! Como es tu primera vez, te mostramos los productos más populares:",
        "productos": populares
    }
