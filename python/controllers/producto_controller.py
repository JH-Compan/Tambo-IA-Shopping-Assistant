"""
ProductoController
Endpoints para consultar productos, stock y promociones.

GET  /api/productos              → todos los productos
GET  /api/productos/buscar?q=    → búsqueda
GET  /api/productos/promociones  → promociones vigentes
GET  /api/productos/<id>/stock   → stock de un producto específico
"""
from flask import Blueprint, request, jsonify
from services import producto_service

producto_bp = Blueprint("productos", __name__)


@producto_bp.route("/api/productos", methods=["GET"])
def listar_productos():
    """Retorna todos los productos del catálogo con su stock."""
    from repositories import producto_repository
    productos = producto_repository.obtener_todos_los_productos()
    stock_todos = {s["id_producto"]: s["stock_disponible"]
                   for s in producto_repository.obtener_stock_todos()}
    for p in productos:
        p["stock"] = stock_todos.get(p["id_producto"], 0)
    return jsonify(productos), 200


@producto_bp.route("/api/productos/buscar", methods=["GET"])
def buscar():
    """
    Busca productos por nombre o categoría.
    Parámetro: ?q=termino
    """
    termino = request.args.get("q", "").strip()
    if not termino:
        return jsonify({"error": "Parámetro 'q' requerido"}), 400
    resultados = producto_service.buscar_productos(termino)
    return jsonify(resultados), 200


@producto_bp.route("/api/productos/promociones", methods=["GET"])
def promociones():
    """Retorna las promociones vigentes del día."""
    promos = producto_service.obtener_promociones()
    return jsonify(promos), 200


@producto_bp.route("/api/productos/<int:id_producto>/stock", methods=["GET"])
def stock(id_producto):
    """Verifica el stock de un producto por su ID."""
    resultado = producto_service.verificar_stock(id_producto)
    return jsonify(resultado), 200
