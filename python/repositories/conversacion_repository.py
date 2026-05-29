"""
ConversacionRepository
Lee el historial de compras y guarda las interacciones del chatbot en Excel.
"""
import pandas as pd
import openpyxl
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _ruta(nombre):
    return os.path.join(DATA_DIR, nombre)


def obtener_historial_cliente(telefono: str):
    """Retorna el historial de compras de un cliente por su número de teléfono."""
    df = pd.read_excel(_ruta("historial_compras.xlsx"))
    historial = df[df["telefono_cliente"].astype(str) == str(telefono)]
    return historial.to_dict(orient="records")


def obtener_productos_frecuentes(telefono: str, top: int = 3):
    """Retorna los productos más comprados por un cliente (top N)."""
    historial = obtener_historial_cliente(telefono)
    if not historial:
        return []
    df = pd.DataFrame(historial)
    frecuentes = (
        df.groupby(["id_producto", "nombre_producto"])["cantidad"]
        .sum()
        .reset_index()
        .sort_values("cantidad", ascending=False)
        .head(top)
    )
    return frecuentes.to_dict(orient="records")


def guardar_interaccion(telefono: str, mensaje_usuario: str, respuesta_bot: str):
    """Agrega una nueva fila al archivo de interacciones del chatbot."""
    ruta = _ruta("interacciones.xlsx")
    wb = openpyxl.load_workbook(ruta)
    ws = wb.active

    # Obtener el siguiente ID
    ultimo_id = ws.max_row  # fila 1 es encabezado, así que max_row-1 filas de datos
    nuevo_id = ultimo_id  # el próximo es max_row (ya contaba el header)

    ws.append([
        nuevo_id,
        telefono,
        mensaje_usuario,
        respuesta_bot,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])
    wb.save(ruta)


def obtener_metricas_interacciones():
    """Retorna estadísticas básicas de las interacciones del chatbot."""
    df = pd.read_excel(_ruta("interacciones.xlsx"))
    if df.empty:
        return {"total_interacciones": 0, "clientes_unicos": 0}
    return {
        "total_interacciones": len(df),
        "clientes_unicos": df["telefono_cliente"].nunique(),
    }
