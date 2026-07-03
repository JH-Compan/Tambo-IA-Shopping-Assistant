from flask import Blueprint, jsonify, request
from services.producto_service import ProductoService

producto_bp = Blueprint("producto_bp", __name__)
producto_service = ProductoService()


@producto_bp.route("/api/productos", methods=["GET"])
def listar_productos():
    productos = producto_service.listar_productos()
    return jsonify(productos), 200


@producto_bp.route("/api/productos/buscar", methods=["GET"])
def buscar_productos():
    texto = request.args.get("q", "")
    productos = producto_service.buscar_productos(texto)
    return jsonify(productos), 200


@producto_bp.route("/api/categorias", methods=["GET"])
def listar_categorias():
    categorias = producto_service.listar_categorias()
    return jsonify(categorias), 200


@producto_bp.route("/api/promociones", methods=["GET"])
def listar_promociones():
    promociones = producto_service.listar_promociones(user_id=request.args.get("user_id"))
    return jsonify(promociones), 200
