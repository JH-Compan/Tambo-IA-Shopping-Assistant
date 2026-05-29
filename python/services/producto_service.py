"""
ProductoService
Lógica de negocio para consulta de productos, stock y promociones.
"""
from repositories import producto_repository


def buscar_productos(termino: str):
    """
    Busca productos por nombre o categoría.
    Para cada producto encontrado, adjunta su stock actual.
    """
    productos = producto_repository.buscar_productos(termino)
    stock_todos = {s["id_producto"]: s["stock_disponible"]
                   for s in producto_repository.obtener_stock_todos()}

    resultado = []
    for p in productos:
        p["stock"] = stock_todos.get(p["id_producto"], 0)
        resultado.append(p)
    return resultado


def obtener_promociones():
    """Retorna las promociones vigentes del día."""
    return producto_repository.obtener_promociones_vigentes()


def verificar_stock(id_producto: int):
    """
    Verifica si un producto tiene stock disponible.
    Retorna True/False y la cantidad disponible.
    """
    cantidad = producto_repository.obtener_stock(id_producto)
    return {
        "disponible": cantidad > 0,
        "stock": cantidad
    }


def obtener_productos_populares():
    """
    Retorna los 5 productos con más stock como 'populares'
    (simula productos más vendidos para clientes sin historial).
    """
    productos = producto_repository.obtener_productos_con_stock()
    # Ordenamos por stock para simular popularidad
    ordenados = sorted(productos, key=lambda x: x.get("stock_disponible", 0), reverse=True)
    return ordenados[:5]


def obtener_alternativa(id_producto: int):
    """
    Si un producto está agotado, sugiere una alternativa de la misma categoría.
    """
    todos = producto_repository.obtener_todos_los_productos()
    stock_todos = {s["id_producto"]: s["stock_disponible"]
                   for s in producto_repository.obtener_stock_todos()}

    # Encontrar la categoría del producto agotado
    categoria_objetivo = None
    for p in todos:
        if p["id_producto"] == id_producto:
            categoria_objetivo = p["categoria"]
            break

    if not categoria_objetivo:
        return None

    # Buscar un sustituto con stock en la misma categoría
    for p in todos:
        if (p["id_producto"] != id_producto and
                p["categoria"] == categoria_objetivo and
                stock_todos.get(p["id_producto"], 0) > 0):
            p["stock"] = stock_todos[p["id_producto"]]
            return p
    return None
