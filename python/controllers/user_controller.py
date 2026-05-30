"""
user_controller.py
GET  /api/usuarios        → lista todos los usuarios
GET  /api/usuarios/<id>   → valida si un usuario existe
"""
from flask import Blueprint, jsonify
from config.supabase_client import supabase
 
user_bp = Blueprint("user_bp", __name__)
 
 
@user_bp.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    """Retorna todos los usuarios para el selector de login."""
    try:
        res = supabase.table("chat_users") \
            .select("id, user_code, name_alias, segment") \
            .order("user_code") \
            .execute()
        return jsonify(res.data or []), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
 
@user_bp.route("/api/usuarios/<user_id>", methods=["GET"])
def validar_usuario(user_id):
    """Valida si un usuario existe."""
    try:
        res = supabase.table("chat_users") \
            .select("id, user_code, name_alias, segment") \
            .eq("user_code", user_id) \
            .single() \
            .execute()
 
        if res.data:
            return jsonify({"valido": True, "usuario": res.data}), 200
        else:
            return jsonify({"valido": False}), 404
 
    except Exception as e:
        return jsonify({"valido": False, "error": str(e)}), 404
