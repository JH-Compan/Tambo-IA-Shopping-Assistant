"""
AdminController
Endpoint de métricas para el dashboard administrativo.

GET /api/metricas → resumen de estadísticas del sistema
"""
from flask import Blueprint, jsonify
from services import metrica_service

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/metricas", methods=["GET"])
def metricas():
    """Retorna las métricas generales del chatbot."""
    datos = metrica_service.obtener_metricas()
    return jsonify(datos), 200
