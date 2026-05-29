import os
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from controllers.producto_controller import producto_bp
from controllers.chat_controller import chat_bp
from controllers.admin_controller import admin_bp


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def crear_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(producto_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    @app.route("/", methods=["GET"])
    def home():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/api", methods=["GET"])
    def api_info():
        return jsonify({
            "message": "Backend de TamboBot activo",
            "rutas_disponibles": {
                "health": "/api/health",
                "productos": "/api/productos",
                "categorias": "/api/categorias",
                "promociones": "/api/promociones",
                "resumen_admin": "/api/admin/resumen",
                "chat": "/api/chat"
            }
        }), 200

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "message": "Backend de TamboBot funcionando correctamente"
        }), 200

    return app


app = crear_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
