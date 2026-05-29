"""
ChatbotService
Procesa el mensaje del usuario, detecta la intención y genera la respuesta.
"""
from repositories import conversacion_repository
from services import producto_service, recomendacion_service

# ─────────────────────────────────────────────────────────
# Palabras clave por intención
# ─────────────────────────────────────────────────────────
INTENCIONES = {
    "saludo":         ["hola", "buenas", "buenos", "hey", "inicio", "empezar", "comenzar"],
    "promociones":    ["promo", "promocion", "oferta", "descuento", "combo", "especial", "barato"],
    "busqueda":       ["buscar", "busco", "tienen", "hay", "quiero", "necesito", "ver", "mostrar"],
    "recomendacion":  ["recomienda", "recomendar", "suger", "que me das", "que compro", "que llevar"],
    "carrito":        ["carrito", "agregar", "añadir", "pedido", "comprar", "llevar"],
    "stock":          ["stock", "disponible", "hay stock", "agotado", "existe"],
    "resumen":        ["resumen", "total", "cuanto", "precio total", "mi pedido", "confirmar"],
    "ayuda":          ["ayuda", "help", "que puedes", "opciones", "menu", "menú"],
    "despedida":      ["adios", "chao", "bye", "gracias", "hasta luego"],
}


def detectar_intencion(mensaje: str) -> str:
    """Detecta la intención principal del mensaje del usuario."""
    mensaje_lower = mensaje.lower()
    for intencion, palabras in INTENCIONES.items():
        if any(p in mensaje_lower for p in palabras):
            return intencion
    return "desconocido"


def procesar_mensaje(telefono: str, mensaje: str) -> dict:
    """
    Recibe el teléfono y el mensaje del usuario.
    Retorna un dict con la respuesta estructurada del chatbot.
    """
    intencion = detectar_intencion(mensaje)
    respuesta = _generar_respuesta(telefono, mensaje, intencion)

    # Guardar la interacción en Excel
    try:
        conversacion_repository.guardar_interaccion(
            telefono=telefono,
            mensaje_usuario=mensaje,
            respuesta_bot=str(respuesta.get("body_text", ""))
        )
    except Exception as e:
        print(f"[WARN] No se pudo guardar la interacción: {e}")

    return respuesta


def _generar_respuesta(telefono: str, mensaje: str, intencion: str) -> dict:
    """Genera la respuesta según la intención detectada."""

    # ── Saludo ──────────────────────────────────────────
    if intencion == "saludo":
        return {
            "message_type": "interactive_list",
            "body_text": (
                "¡Hola! Bienvenido al asistente de Tambo+ 🛒\n"
                "¿En qué te puedo ayudar hoy?"
            ),
            "options": [
                {"id": "promociones",   "title": "🎁 Ver promociones"},
                {"id": "busqueda",      "title": "🔍 Buscar un producto"},
                {"id": "recomendacion", "title": "⭐ Recomendaciones para mí"},
                {"id": "ayuda",         "title": "❓ Ayuda"},
            ]
        }

    # ── Promociones ──────────────────────────────────────
    elif intencion == "promociones":
        promos = producto_service.obtener_promociones()
        if not promos:
            return {
                "message_type": "text",
                "body_text": "Por el momento no hay promociones vigentes. ¡Vuelve pronto! 😊",
                "options": []
            }
        opciones = [
            {"id": f"promo_{p['id_promo']}", "title": f"{p['nombre']} - S/{p['precio_promo']:.2f}"}
            for p in promos
        ]
        detalle = "\n".join(
            f"• *{p['nombre']}*: {p['descripcion']} → S/{p['precio_promo']:.2f} (hasta {p['fecha_fin']})"
            for p in promos
        )
        return {
            "message_type": "interactive_list",
            "body_text": f"🎁 *Promociones vigentes:*\n\n{detalle}",
            "options": opciones + [{"id": "menu", "title": "🏠 Volver al menú"}]
        }

    # ── Búsqueda ─────────────────────────────────────────
    elif intencion == "busqueda":
        # Extraer el término de búsqueda (quitar palabras clave)
        palabras_clave = ["buscar", "busco", "tienen", "hay", "quiero", "necesito", "ver", "mostrar", "un", "una", "el", "la"]
        termino = mensaje.lower()
        for p in palabras_clave:
            termino = termino.replace(p, "").strip()

        if len(termino) < 2:
            return {
                "message_type": "text",
                "body_text": "¿Qué producto estás buscando? Escríbeme el nombre o categoría (ej: 'gaseosa', 'snacks', 'arroz').",
                "options": []
            }

        productos = producto_service.buscar_productos(termino)
        if not productos:
            return {
                "message_type": "text",
                "body_text": f"No encontré productos con '{termino}'. Intenta con otra palabra 🔍",
                "options": [{"id": "menu", "title": "🏠 Volver al menú"}]
            }

        detalle = "\n".join(
            f"• *{p['nombre']}* — S/{p['precio']:.2f} | "
            f"{'✅ Disponible' if p['stock'] > 0 else '❌ Agotado'}"
            for p in productos[:5]
        )
        opciones = [
            {"id": f"prod_{p['id_producto']}", "title": f"Agregar {p['nombre']}"}
            for p in productos[:5] if p["stock"] > 0
        ]
        return {
            "message_type": "interactive_list",
            "body_text": f"🔍 Resultados para '{termino}':\n\n{detalle}",
            "options": opciones + [{"id": "menu", "title": "🏠 Volver al menú"}]
        }

    # ── Recomendaciones ───────────────────────────────────
    elif intencion == "recomendacion":
        resultado = recomendacion_service.recomendar(telefono)
        productos = resultado.get("productos", [])
        if not productos:
            return {
                "message_type": "text",
                "body_text": "No encontré recomendaciones en este momento. ¡Explora nuestras promociones! 🎁",
                "options": [{"id": "promociones", "title": "Ver promociones"}]
            }
        detalle = "\n".join(
            f"• *{p['nombre']}* — S/{p['precio']:.2f} | {p.get('razon', '')}"
            for p in productos
        )
        opciones = [
            {"id": f"prod_{p['id_producto']}", "title": f"Agregar {p['nombre']}"}
            for p in productos
        ]
        return {
            "message_type": "interactive_list",
            "body_text": f"⭐ {resultado['mensaje']}\n\n{detalle}",
            "options": opciones + [{"id": "menu", "title": "🏠 Volver al menú"}]
        }

    # ── Stock ─────────────────────────────────────────────
    elif intencion == "stock":
        return {
            "message_type": "text",
            "body_text": "¿De qué producto quieres saber el stock? Escríbeme el nombre y te confirmo la disponibilidad.",
            "options": []
        }

    # ── Ayuda ─────────────────────────────────────────────
    elif intencion == "ayuda":
        return {
            "message_type": "interactive_list",
            "body_text": (
                "🤖 *Soy Tambot, tu asistente de Tambo+*\n\n"
                "Puedo ayudarte con:\n"
                "• Ver promociones del día\n"
                "• Buscar productos por nombre o categoría\n"
                "• Darte recomendaciones personalizadas\n"
                "• Verificar si un producto está disponible\n\n"
                "¿Qué deseas hacer?"
            ),
            "options": [
                {"id": "promociones",   "title": "🎁 Ver promociones"},
                {"id": "busqueda",      "title": "🔍 Buscar producto"},
                {"id": "recomendacion", "title": "⭐ Recomendaciones"},
            ]
        }

    # ── Despedida ─────────────────────────────────────────
    elif intencion == "despedida":
        return {
            "message_type": "text",
            "body_text": "¡Hasta luego! Gracias por usar Tambot 🛒 ¡Vuelve pronto!",
            "options": []
        }

    # ── Intención desconocida ─────────────────────────────
    else:
        return {
            "message_type": "interactive_list",
            "body_text": (
                "No entendí bien tu mensaje 😅\n"
                "Prueba escribiendo: 'promociones', 'buscar [producto]', o 'recomendaciones'."
            ),
            "options": [
                {"id": "promociones",   "title": "🎁 Ver promociones"},
                {"id": "busqueda",      "title": "🔍 Buscar producto"},
                {"id": "recomendacion", "title": "⭐ Recomendaciones"},
                {"id": "ayuda",         "title": "❓ Ayuda"},
            ]
        }
