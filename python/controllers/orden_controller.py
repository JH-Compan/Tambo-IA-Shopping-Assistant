"""
orden_controller.py
POST /api/ordenes       -> registra una orden transaccional en Supabase
POST /api/chat/cerrar   -> cierra la conversación activa del usuario
"""
from datetime import datetime

from flask import Blueprint, jsonify, request

from config.supabase_client import supabase
from services.availability_service import AvailabilityService


orden_bp = Blueprint("orden_bp", __name__)
availability_service = AvailabilityService()

VALID_ITEM_TYPES = {
    "product": "product",
    "promotion": "promotion",
    "producto": "product",
    "promocion": "promotion",
    "promoción": "promotion",
}


def _build_error_response(message, status_code):
    return jsonify({"success": False, "error": message}), status_code


def _normalize_item_type(value):
    return VALID_ITEM_TYPES.get(str(value or "").strip().lower())


def _parse_rpc_error(exc):
    if hasattr(exc, "message") and exc.message:
        raw_message = str(exc.message)
    elif getattr(exc, "args", None):
        raw_message = str(exc.args[0])
    else:
        raw_message = str(exc)

    normalized = raw_message.lower()

    if "stock:" in normalized or "stock insuficiente" in normalized:
        if "STOCK:" in raw_message:
            return raw_message.split("STOCK:", 1)[-1].strip(), 409
        return "No hay stock suficiente para completar la compra", 409

    if "validation:" in normalized:
        if "VALIDATION:" in raw_message:
            return raw_message.split("VALIDATION:", 1)[-1].strip(), 400
        return "No se pudo validar la orden", 400

    return "No se pudo registrar la compra en este momento", 500


@orden_bp.route("/api/ordenes", methods=["POST"])
def crear_orden():
    data = request.get_json(silent=True)
    if not data:
        return _build_error_response("Se esperaba un cuerpo JSON válido", 400)

    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")
    items = data.get("items")

    if not user_id:
        return _build_error_response("El campo 'user_id' es obligatorio", 400)
    if not isinstance(items, list) or not items:
        return _build_error_response("El carrito está vacío", 400)
    if len(items) > 50:
        return _build_error_response("La orden no puede contener más de 50 ítems", 400)

    normalized_items = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            return _build_error_response(f"El ítem #{index} no tiene un formato válido", 400)

        item_id = str(item.get("item_id") or "").strip()
        item_type = _normalize_item_type(item.get("item_type"))
        quantity = item.get("quantity")

        if not item_id:
            return _build_error_response(f"El ítem #{index} debe incluir item_id", 400)
        if not item_type:
            return _build_error_response(f"El ítem #{index} tiene un item_type inválido", 400)
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            return _build_error_response(f"El ítem #{index} debe incluir quantity como entero", 400)
        if quantity < 1 or quantity > 100:
            return _build_error_response(f"El ítem #{index} debe incluir quantity entre 1 y 100", 400)

        normalized_items.append({
            "item_id": item_id,
            "item_type": item_type,
            "quantity": quantity,
        })

    try:
        result = supabase.rpc(
            "create_order_transaction",
            {
                "p_user_id": user_id,
                "p_conversation_id": conversation_id,
                "p_items": normalized_items,
            }
        ).execute()

        payload = result.data or {}
        if isinstance(payload, list):
            payload = payload[0] if payload else {}

        if payload.get("success") is not True:
            return _build_error_response("No se pudo registrar la compra", 500)

        return jsonify({
            "success": True,
            "order_id": payload.get("order_id"),
            "total_amount": payload.get("total_amount", 0),
            "items_count": payload.get("items_count", len(normalized_items)),
            "message": "Orden registrada correctamente",
        }), 201

    except Exception as exc:
        message, status_code = _parse_rpc_error(exc)
        return _build_error_response(message, status_code)


@orden_bp.route("/api/carrito/validar-item", methods=["POST"])
def validar_item_carrito():
    data = request.get_json(silent=True)
    if not data:
        return _build_error_response("Se esperaba un cuerpo JSON valido", 400)

    user_id = data.get("user_id")
    item_id = str(data.get("item_id") or "").strip()
    item_type = _normalize_item_type(data.get("item_type"))
    quantity = data.get("quantity", 1)

    if not item_id:
        return _build_error_response("El campo 'item_id' es obligatorio", 400)
    if not item_type:
        return _build_error_response("El campo 'item_type' es invalido", 400)
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        return _build_error_response("El campo 'quantity' debe ser un entero mayor o igual a 1", 400)

    availability = availability_service.evaluate_item(
        item_type=item_type,
        item_id=item_id,
        requested_quantity=quantity,
        user_id=user_id
    )
    response = {
        "success": True,
        "available": availability["available"],
        "item_id": item_id,
        "quantity": quantity,
    }
    if availability["available"]:
        return jsonify(response), 200

    response["reason_code"] = availability.get("reason_code")
    response["message"] = availability.get("reason")
    response["details"] = availability.get("details")
    return jsonify(response), 200


@orden_bp.route("/api/chat/cerrar", methods=["POST"])
def cerrar_conversacion():
    data = request.get_json(silent=True)
    if not data:
        return _build_error_response("Se esperaba un cuerpo JSON válido", 400)

    conversation_id = str(data.get("conversation_id") or "").strip()

    if not conversation_id:
        return _build_error_response("conversation_id es obligatorio", 400)

    try:
        supabase.table("chat_conversations").update({
            "status": "closed",
            "ended_at": datetime.now().isoformat()
        }).eq("id", conversation_id).execute()

        return jsonify({"success": True, "mensaje": "Conversación cerrada"}), 200

    except Exception:
        return _build_error_response("No se pudo cerrar la conversación", 500)
