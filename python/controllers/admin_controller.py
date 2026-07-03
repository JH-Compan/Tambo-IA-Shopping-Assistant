from flask import Blueprint, jsonify
from services.metrica_service import MetricaService

admin_bp = Blueprint("admin_bp", __name__)
metrica_service = MetricaService()

@admin_bp.route("/api/admin/resumen", methods=["GET"])
def resumen_general():
    resumen = metrica_service.obtener_resumen_general()
    return jsonify(resumen), 200

@admin_bp.route("/api/admin/dashboard", methods=["GET"])
def dashboard_completo():
    data = metrica_service.obtener_dashboard_completo()
    return jsonify(data), 200
