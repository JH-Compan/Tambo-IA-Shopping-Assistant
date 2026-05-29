"""
ProductoRepository
Lee y consulta datos de productos, stock y promociones desde archivos Excel.
"""
import pandas as pd
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _ruta(nombre):
    return os.path.join(DATA_DIR, nombre)


def obtener_todos_los_productos():
    """Retorna lista de todos los productos del catálogo."""
    df = pd.read_excel(_ruta("productos.xlsx"))
    return df.to_dict(orient="records")


def buscar_productos(termino: str):
    """Busca productos por nombre o categoría (búsqueda parcial, sin distinguir mayúsculas)."""
    df = pd.read_excel(_ruta("productos.xlsx"))
    termino = termino.lower()
    resultado = df[
        df["nombre"].str.lower().str.contains(termino, na=False) |
        df["categoria"].str.lower().str.contains(termino, na=False)
    ]
    return resultado.to_dict(orient="records")


def obtener_stock(id_producto: int):
    """Retorna el stock disponible de un producto por su ID."""
    df = pd.read_excel(_ruta("stock.xlsx"))
    fila = df[df["id_producto"] == id_producto]
    if fila.empty:
        return 0
    return int(fila.iloc[0]["stock_disponible"])


def obtener_stock_todos():
    """Retorna stock de todos los productos."""
    df = pd.read_excel(_ruta("stock.xlsx"))
    return df.to_dict(orient="records")


def obtener_promociones_vigentes():
    """Retorna promociones cuya fecha de vigencia incluye el día de hoy."""
    df = pd.read_excel(_ruta("promociones.xlsx"))
    hoy = str(date.today())
    vigentes = df[
        (df["fecha_inicio"] <= hoy) &
        (df["fecha_fin"] >= hoy)
    ]
    return vigentes.to_dict(orient="records")


def obtener_productos_con_stock():
    """Retorna solo los productos que tienen stock > 0."""
    productos = pd.read_excel(_ruta("productos.xlsx"))
    stock = pd.read_excel(_ruta("stock.xlsx"))
    merged = pd.merge(productos, stock[["id_producto", "stock_disponible"]], on="id_producto")
    disponibles = merged[merged["stock_disponible"] > 0]
    return disponibles.to_dict(orient="records")
