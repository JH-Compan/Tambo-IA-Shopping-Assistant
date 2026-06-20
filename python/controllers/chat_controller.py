from flask import Blueprint, jsonify, request
from services.chatbot_service import ChatbotService
from repositories.recomendacion_repository import RecomendacionRepository

chat_bp = Blueprint("chat_bp", __name__)
chatbot_service = ChatbotService()
recomendacion_repository = RecomendacionRepository()


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id", "USR001")
    mensaje = data.get("mensaje")
    conversation_id = data.get("conversation_id")

    if not mensaje:
        return jsonify({"error": "El campo 'mensaje' es obligatorio"}), 400

    try:
        resultado = chatbot_service.procesar_mensaje(
            user_id=user_id,
            mensaje=mensaje,
            conversation_id=conversation_id
        )
        return jsonify(resultado), 200
    except Exception:
        return jsonify({
            "success": False,
            "response": "No pude procesar tu solicitud en este momento.",
            "items": [],
            "intent": "consulta_general",
            "confidence": 0.0,
            "requires_clarification": False
        }), 500


@chat_bp.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True) or {}

    conversation_id = data.get("conversation_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not conversation_id:
        return jsonify({"error": "El campo 'conversation_id' es obligatorio"}), 400

    if not rating:
        return jsonify({"error": "El campo 'rating' es obligatorio"}), 400

    if rating < 1 or rating > 5:
        return jsonify({"error": "El rating debe estar entre 1 y 5"}), 400

    feedback_guardado = recomendacion_repository.guardar_feedback(
        conversation_id=conversation_id,
        rating=rating,
        comment=comment
    )

    return jsonify(feedback_guardado), 201
