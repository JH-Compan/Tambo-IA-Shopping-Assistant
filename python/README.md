# Backend Flask integrado

Esta rama `Test` integra el backend Flask de `main` con el frontend de la rama `frontend`.

## Requisitos

```bash
cd python
pip install -r requirements.txt
```

## Ejecución

```bash
cd python
python app.py
```

Luego abrir:

```txt
http://localhost:5000/
```

## Rutas principales

```txt
GET  /                         Interfaz web integrada
GET  /api                      Información del backend
POST /api/chat                 Procesar mensaje del chatbot por reglas
GET  /api/productos            Listar productos con stock
GET  /api/productos/buscar?q=  Buscar productos por nombre o categoría
GET  /api/productos/promociones Ver promociones vigentes
GET  /api/productos/<id>/stock Consultar stock de producto
GET  /api/metricas             Métricas para dashboard
```

## Nota

La integración funciona sin LLM. El chatbot usa reglas/palabras clave desde `services/chatbot_service.py` y los datos se leen desde los archivos Excel de la carpeta `data/`.
