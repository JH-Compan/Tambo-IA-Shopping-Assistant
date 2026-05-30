"""
orden_controller.py
POST /api/ordenes           → registra una orden completa y descuenta stock
POST /api/chat/cerrar       → cierra la conversación activa del usuario
"""
from flask import Blueprint, jsonify, request
from config.supabase_client import supabase
from datetime import datetime
import uuid

orden_bp = Blueprint("orden_bp", __name__)


@orden_bp.route("/api/ordenes", methods=["POST"])
def crear_orden():
    """
    Registra una orden en SALES_orders y sus items en SALES_order_items.
    Descuenta el stock de cada producto en CAT_products.

    Body esperado:
    {
        "user_id": "USR001",
        "conversation_id": "uuid...",
        "items": [
            {"item_id": "PROD_INCA_1L", "item_type": "producto", "quantity": 2, "unit_price": 5.20},
            {"item_id": "PROMO001",     "item_type": "promocion", "quantity": 1, "unit_price": 4.90}
        ],
        "total": 15.30
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se esperaba un cuerpo JSON"}), 400

    user_id         = data.get("user_id")
    conversation_id = data.get("conversation_id")
    items           = data.get("items", [])
    total           = data.get("total", 0)

    if not user_id:
        return jsonify({"error": "El campo 'user_id' es obligatorio"}), 400
    if not items:
        return jsonify({"error": "El carrito está vacío"}), 400

    try:
        # 1. Crear la orden principal en SALES_orders
        orden_id = str(uuid.uuid4())
        supabase.table("sales_orders").insert({
            "id":              orden_id,
            "user_id":         user_id,
            "conversation_id": conversation_id,
            "total_amount":    total,
            "status":          "completed",
            "order_date":      datetime.now().isoformat(),
        }).execute()

        # 2. Insertar cada item en SALES_order_items y descontar stock
        for item in items:
            item_id   = item.get("item_id")
            item_type = item.get("item_type", "producto")
            quantity  = int(item.get("quantity", 1))
            price     = float(item.get("unit_price", 0))

            # Insertar en SALES_order_items
            supabase.table("sales_order_items").insert({
                "id":        str(uuid.uuid4()),
                "order_id":  orden_id,
                "item_id":   item_id,
                "item_type": item_type,
                "quantity":  quantity,
                "unit_price": price,
                "subtotal":  quantity * price
            }).execute()

            # Descontar stock en CAT_products si es producto
            if item_type == "producto":
                _descontar_stock_producto(item_id, quantity)

            # Si es promoción, descontar stock de sus productos relacionados
            elif item_type == "promocion":
                _descontar_stock_promocion(item_id, quantity)

        return jsonify({
            "success":  True,
            "orden_id": orden_id,
            "mensaje":  "Orden registrada correctamente"
        }), 201

    except Exception as e:
        print(f"[ERROR] crear_orden: {e}")
        return jsonify({"error": str(e)}), 500


def _descontar_stock_producto(product_id: str, quantity: int):
    """Descuenta el stock de un producto en CAT_products."""
    try:
        # Obtener stock actual
        res = supabase.table("cat_products") \
            .select("stock") \
            .eq("id", product_id) \
            .single() \
            .execute()

        if not res.data:
            return

        stock_actual = int(res.data.get("stock", 0))
        nuevo_stock  = max(0, stock_actual - quantity)
        is_active    = nuevo_stock > 0

        # Actualizar stock e is_active
        supabase.table("cat_products").update({
            "stock":      nuevo_stock,
            "is_active":  is_active,
            "updated_at": datetime.now().isoformat()
        }).eq("id", product_id).execute()

    except Exception as e:
        print(f"[WARN] No se pudo descontar stock de {product_id}: {e}")


def _descontar_stock_promocion(promo_id: str, quantity: int):
    """
    Descuenta el stock de los productos que forman parte de una promoción
    consultando CAT_promotion_items.
    También actualiza max_per_customer si aplica.
    """
    try:
        # Obtener los productos de la promoción
        res = supabase.table("cat_promotion_items") \
            .select("product_id, quantity") \
            .eq("promotion_id", promo_id) \
            .execute()

        if not res.data:
            return

        for promo_item in res.data:
            prod_id       = promo_item.get("product_id")
            prod_qty      = int(promo_item.get("quantity", 1))
            total_qty     = prod_qty * quantity
            _descontar_stock_producto(prod_id, total_qty)

    except Exception as e:
        print(f"[WARN] No se pudo descontar stock de promoción {promo_id}: {e}")


@orden_bp.route("/api/chat/cerrar", methods=["POST"])
def cerrar_conversacion():
    """
    Cierra la conversación activa del usuario cuando hace logout.
    Body: { "conversation_id": "uuid...", "user_id": "USR001" }
    """
    data = request.get_json()
    conversation_id = data.get("conversation_id")
    user_id         = data.get("user_id")

    if not conversation_id:
        return jsonify({"error": "conversation_id es obligatorio"}), 400

    try:
        supabase.table("chat_conversations").update({
            "status":   "closed",
            "ended_at": datetime.now().isoformat()
        }).eq("id", conversation_id).execute()

        return jsonify({"success": True, "mensaje": "Conversación cerrada"}), 200

    except Exception as e:
        print(f"[WARN] No se pudo cerrar conversación {conversation_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
