"""
user_controller.py
GET  /api/usuarios           → lista todos los usuarios
POST /api/usuarios/registro  → registra un nuevo usuario
POST /api/usuarios/login     → valida las credenciales
"""
from flask import Blueprint, jsonify, request
from config.supabase_client import supabase
from datetime import datetime

user_bp = Blueprint("user_bp", __name__)

SEGMENTOS = ["estudiante", "trabajador", "hogar", "oficina", "ahorrador",
             "snack_lovers", "comprador_rapido", "familia"]


@user_bp.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    """Lista todos los usuarios activos."""
    try:
        res = supabase.table("chat_users").select("*").order("user_code").execute()
        return jsonify(res.data or []), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/api/usuarios/registro", methods=["POST"])
def registro():
    """
    Registra un nuevo usuario.
    Body: { "name_alias": "Maria", "segment": "estudiante" }
    El user_code se genera automáticamente (USR001, USR002...)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se esperaba JSON"}), 400

    name_alias = data.get("name_alias", "").strip()
    segment    = data.get("segment", "").strip()

    if not name_alias:
        return jsonify({"error": "El nombre de usuario es obligatorio"}), 400
    if not segment:
        return jsonify({"error": "El segmento es obligatorio"}), 400
    if segment not in SEGMENTOS:
        return jsonify({"error": f"Segmento inválido. Opciones: {', '.join(SEGMENTOS)}"}), 400

    try:
        # Verificar que el name_alias no exista ya
        existe = supabase.table("chat_users") \
            .select("id") \
            .eq("name_alias", name_alias) \
            .execute()
        if existe.data:
            return jsonify({"error": "Ese nombre de usuario ya existe"}), 409

        # Generar el próximo user_code (USR001, USR002...)
        todos = supabase.table("chat_users").select("user_code").order("user_code", desc=True).limit(1).execute()
        if todos.data:
            ultimo = todos.data[0]["user_code"]  # ej: USR029
            numero = int(ultimo.replace("USR", "")) + 1
        else:
            numero = 1
        nuevo_code = f"USR{numero:03d}"

        # Insertar en Supabase
        nuevo_usuario = {
            "id":         nuevo_code,
            "user_code":  nuevo_code,
            "name_alias": name_alias,
            "segment":    segment,
            "is_active":  True,
            "created_at": datetime.now().isoformat()
        }
        res = supabase.table("chat_users").insert(nuevo_usuario).execute()

        return jsonify({
            "success":  True,
            "mensaje":  "Usuario registrado correctamente",
            "usuario":  res.data[0] if res.data else nuevo_usuario
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route("/api/usuarios/login", methods=["POST"])
def login():
    """
    Valida credenciales.
    Body: { "name_alias": "Maria", "password": "USR031" }
    La contraseña es el user_code.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Se esperaba JSON"}), 400

    name_alias = data.get("name_alias", "").strip()
    password   = data.get("password", "").strip()

    if not name_alias or not password:
        return jsonify({"error": "Usuario y contraseña son obligatorios"}), 400

    try:
        res = supabase.table("chat_users") \
            .select("*") \
            .eq("name_alias", name_alias) \
            .eq("user_code", password) \
            .eq("is_active", True) \
            .execute()

        if not res.data:
            return jsonify({"valido": False, "error": "Usuario o contraseña incorrectos"}), 401

        return jsonify({"valido": True, "usuario": res.data[0]}), 200

    except Exception as e:
        return jsonify({"valido": False, "error": str(e)}), 500


@user_bp.route("/api/usuarios/segmentos", methods=["GET"])
def listar_segmentos():
    """Retorna los segmentos disponibles para el formulario de registro."""
    return jsonify(SEGMENTOS), 200
