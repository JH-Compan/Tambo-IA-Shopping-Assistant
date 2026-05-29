"""
ChatController
Maneja las peticiones HTTP del chat: POST /api/chat
"""
from flask import Blueprint, request, jsonify
from services import chatbot_service

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    """
    Recibe un mensaje del usuario y retorna la respuesta del chatbot.

    Body esperado (JSON):
    {
        "sender_phone": "999888777",
        "message_body": "Quiero ver las ofertas de hoy",
        "timestamp": "2026-05-25T01:15:00Z"   ← opcional
    }
    """
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "Se esperaba un cuerpo JSON"}), 400

    telefono = datos.get("sender_phone", "").strip()
    mensaje  = datos.get("message_body", "").strip()

    if not telefono:
        return jsonify({"error": "El campo 'sender_phone' es obligatorio"}), 400
    if not mensaje:
        return jsonify({"error": "El campo 'message_body' es obligatorio"}), 400

    respuesta = chatbot_service.procesar_mensaje(telefono, mensaje)

    return jsonify({
        "recipient_phone": telefono,
        **respuesta
    }), 200
