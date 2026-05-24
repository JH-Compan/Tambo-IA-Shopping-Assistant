# Documento Sprint 0 - Tambot

## Portada
- Proyecto: Tambo AI Shopping Assistant / Tambot
- Curso: Ingeniería de Software
- Fecha
- Integrantes
- Docente

## 1. Introducción
Explica brevemente de qué trata el proyecto y que Sprint 0 será la etapa de preparación inicial.

## 2. Propósito del Sprint 0
Describe para qué sirve Sprint 0:
- Organizar el proyecto.
- Definir herramientas.
- Preparar el repositorio.
- Organizar historias de usuario.
- Reducir incertidumbre antes de Sprint 1.

## 3. Objetivo del Sprint 0
Redacta el objetivo general, por ejemplo:

> Definir la organización inicial del proyecto Tambot, estableciendo el alcance simulado, Product Goal, MVP, estructura del repositorio, arquitectura base, archivos Excel, backlog inicial y planificación de los sprints.

## 4. Alcance del Sprint 0

### Incluye
- Definir Product Goal.
- Definir MVP.
- Crear estructura del repositorio.
- Definir arquitectura base.
- Definir herramientas.
- Organizar historias de usuario.
- Planificar Sprint 1 y Sprint 2.

### No incluye
- WhatsApp real.
- Pago real.
- Delivery real.
- CRM real.
- LLM externo real.
- Despliegue productivo.

## 5. Visión resumida del proyecto
Explica qué será Tambot:

> Una simulación web de chatbot para Tambo+ que permite consultar promociones, buscar productos, recibir recomendaciones básicas, agregar productos al carrito y visualizar un resumen de pedido usando Excel como base de datos simulada.

## 6. Product Goal
Coloca el objetivo del producto:

> Construir una simulación web de un asistente de compras para Tambo+ que permita consultar promociones, buscar productos, recibir recomendaciones básicas y armar un pedido simulado usando Excel como base de datos.

## 7. MVP delimitado

### El MVP incluye
- Interfaz web tipo chat.
- Consulta de promociones.
- Búsqueda de productos.
- Lectura de datos desde Excel.
- Validación básica de stock.
- Carrito simulado.
- Resumen de pedido.
- Registro de interacciones básicas.

### El MVP no incluye
- WhatsApp real.
- IA real conectada a API externa.
- Pago real.
- Delivery.
- CRM real.
- Seguridad avanzada.

## 8. Herramientas y tecnologías

### Principales
- HTML
- CSS
- JavaScript
- Excel
- Git y GitHub
- Google Drive

### Opcionales
- Python con Flask
- Docker

## 9. Estructura base del repositorio
Aquí colocas el árbol del proyecto:

```bash
tambo-ai-shopping-assistant/
│
├── docs/
│   ├── scrum/
│   ├── backlog/
│   ├── arquitectura/
│   └── evidencias/
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       ├── chatbot.js
│       ├── carrito.js
│       └── recomendaciones.js
│
├── data/
│   ├── productos.xlsx
│   ├── promociones.xlsx
│   ├── stock.xlsx
│   ├── historial_compras.xlsx
│   └── interacciones.xlsx
│
├── python/
│   └── app.py
│
├── tests/
├── README.md
├── .gitignore
└── Dockerfile
