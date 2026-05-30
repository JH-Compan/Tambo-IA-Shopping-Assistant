"""
orden_controller.py
POST /api/ordenes       → registra una orden completa y descuenta stock
POST /api/chat/cerrar   → cierra la conversación activa del usuario
"""
from flask import Blueprint, jsonify, request
from config.supabase_client import supabase
from datetime import datetime
import uuid
 
orden_bp = Blueprint("orden_bp", __name__)
 
 
@orden_bp.route("/api/ordenes", methods=["POST"])
def crear_orden():
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
        # 1. Crear la orden en sales_orders
        orden_id = str(uuid.uuid4())
        supabase.table("sales_orders").insert({
            "id":              orden_id,
            "user_id":         user_id,
            "conversation_id": conversation_id,
            "total_amount":    total,
            "status":          "completed",
            "order_date":      datetime.now().isoformat(),
        }).execute()
 
        # 2. Insertar items y descontar stock
        for item in items:
            item_id   = item.get("item_id")
            item_type = item.get("item_type", "producto")
            quantity  = int(item.get("quantity", 1))
            price     = float(item.get("unit_price", 0))
 
            # Convertir a los valores que acepta Supabase
            # La tabla usa "product" y "promotion" en inglés
            item_type_db = "product" if item_type in ("producto", "product") else "promotion"
 
            supabase.table("sales_order_items").insert({
                "id":           str(uuid.uuid4()),
                "order_id":     orden_id,
                "item_type":    item_type_db,
                "product_id":   item_id if item_type_db == "product"    else None,
                "promotion_id": item_id if item_type_db == "promotion"  else None,
                "quantity":     quantity,
                "unit_price":   price,
                "subtotal":     quantity * price
            }).execute()
 
            # Descontar stock
            if item_type_db == "product":
                _descontar_stock_producto(item_id, quantity)
            else:
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
    try:
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
 
        supabase.table("cat_products").update({
            "stock":      nuevo_stock,
            "is_active":  is_active,
            "updated_at": datetime.now().isoformat()
        }).eq("id", product_id).execute()
 
        print(f"[OK] Stock actualizado: {product_id} → {nuevo_stock}")
 
    except Exception as e:
        print(f"[WARN] No se pudo descontar stock de {product_id}: {e}")
 
 
def _descontar_stock_promocion(promo_id: str, quantity: int):
    try:
        res = supabase.table("cat_promotion_items") \
            .select("product_id, quantity") \
            .eq("promotion_id", promo_id) \
            .execute()
 
        if not res.data:
            return
 
        for promo_item in res.data:
            prod_id   = promo_item.get("product_id")
            prod_qty  = int(promo_item.get("quantity", 1))
            total_qty = prod_qty * quantity
            _descontar_stock_producto(prod_id, total_qty)
 
    except Exception as e:
        print(f"[WARN] No se pudo descontar stock de promoción {promo_id}: {e}")
 
 
@orden_bp.route("/api/chat/cerrar", methods=["POST"])
def cerrar_conversacion():
    data            = request.get_json()
    conversation_id = data.get("conversation_id")
 
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
