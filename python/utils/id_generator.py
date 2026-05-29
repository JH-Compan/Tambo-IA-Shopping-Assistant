from uuid import uuid4


def generar_id(prefijo: str) -> str:
    return f"{prefijo}_{uuid4().hex[:10].upper()}"