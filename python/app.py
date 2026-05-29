import sys
import os

# Asegurar que Python encuentre los módulos internos (controllers, services, repositories)
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS

from controllers.chat_controller     import chat_bp
from controllers.producto_controller import producto_bp
from controllers.admin_controller    import admin_bp

# ─────────────────────────────────────────────
# Crear la aplicación Flask
# ─────────────────────────────────────────────
app = Flask(__name__)

# Habilitar CORS para que el frontend (HTML/JS) pueda llamar al backend
CORS(app)

# ─────────────────────────────────────────────
# Registrar los Blueprints (controladores)
# ─────────────────────────────────────────────
app.register_blueprint(chat_bp)
app.register_blueprint(producto_bp)
app.register_blueprint(admin_bp)


# ─────────────────────────────────────────────
# Ruta raíz — confirma que el servidor está activo
# ─────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "sistema": "Tambot - Tambo+ Shopping Assistant",
        "estado": "activo",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/chat":                    "Enviar mensaje al chatbot",
            "GET  /api/productos":               "Listar todos los productos",
            "GET  /api/productos/buscar?q=":     "Buscar producto por nombre o categoría",
            "GET  /api/productos/promociones":   "Ver promociones vigentes",
            "GET  /api/productos/<id>/stock":    "Verificar stock de un producto",
            "GET  /api/metricas":                "Ver métricas del sistema",
        }
    }), 200


# ─────────────────────────────────────────────
# Manejo de errores globales
# ─────────────────────────────────────────────
@app.errorhandler(404)
def no_encontrado(e):
    return jsonify({"error": "Ruta no encontrada"}), 404


@app.errorhandler(500)
def error_interno(e):
    return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500


# ─────────────────────────────────────────────
# Iniciar servidor
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  🛒  Tambot Backend iniciando...")
    print("  📡  URL: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
