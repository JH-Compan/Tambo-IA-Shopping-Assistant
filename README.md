# Tambo AI Shopping Assistant / Tambot

Simulación web de un asistente de compras para Tambo+. El proyecto permite consultar promociones, buscar productos, recibir recomendaciones básicas, agregar productos a un carrito y visualizar un resumen de pedido usando archivos Excel como base de datos simulada.

## Contexto académico

Este repositorio corresponde al proyecto del curso de Ingeniería de Software. El desarrollo se organiza con Scrum, iniciando con Sprint 0 como etapa de preparación y continuando con Sprint 1 y Sprint 2 para el desarrollo funcional.

## Product Goal

Construir una simulación web de un asistente de compras para Tambo+ que permita a los clientes consultar promociones, buscar productos, recibir recomendaciones básicas y armar un pedido simulado usando Excel como base de datos.

## MVP delimitado

El MVP incluye:

- Interfaz web tipo chat.
- Consulta de promociones vigentes.
- Búsqueda de productos por nombre o categoría.
- Lectura de datos desde Excel.
- Validación básica de disponibilidad.
- Carrito de compras simulado.
- Resumen de pedido.
- Registro o consulta de interacciones básicas.

El MVP no incluye:

- Integración real con WhatsApp Business API.
- Inteligencia artificial real conectada a una API externa.
- Pago real.
- Delivery real.
- CRM real.
- Despliegue productivo en nube.

## Estructura del proyecto

```bash
tambo-ai-shopping-assistant/
│
├── docs/                         # Documentación del proyecto y evidencias de Scrum
│   ├── scrum/                    # Documentos de Sprint 0, Sprint 1 y Sprint 2
│   ├── backlog/                  # Historias de usuario, backlog e issues
│   ├── arquitectura/             # Arquitectura, diagramas y decisiones técnicas
│   └── evidencias/               # Capturas, pruebas, commits y demostraciones
│
├── frontend/                     # Interfaz web del chatbot
│   ├── index.html                # Pantalla principal de la simulación
│   ├── css/
│   │   └── styles.css            # Estilos visuales del chatbot
│   └── js/
│       ├── app.js                # Inicialización general
│       ├── chatbot.js            # Flujo conversacional
│       ├── carrito.js            # Manejo del carrito
│       └── recomendaciones.js    # Lógica de recomendaciones
│
├── data/                         # Archivos Excel usados como base de datos simulada
│   └── README.md                 # Estructura esperada de los Excel
│
├── python/                       # Backend opcional en Python
│   └── app.py                    # Aplicación Flask opcional
│
├── tests/                        # Pruebas básicas del sistema
│
├── README.md                     # Descripción, instalación y ejecución del proyecto
├── .gitignore                    # Archivos que no se subirán al repositorio
└── Dockerfile                    # Configuración opcional para contenedores
```

## Tecnologías principales

- HTML para la estructura de la interfaz web.
- CSS para el diseño visual del chatbot.
- JavaScript para la interacción del usuario y lógica básica del frontend.
- Excel como base de datos simulada.
- Git y GitHub para control de versiones.
- Google Drive para documentación y evidencias.

## Tecnologías opcionales

- Python con Flask para manejar lógica del chatbot o lectura de Excel desde backend.
- Docker para ejecutar el proyecto en un contenedor si el tiempo lo permite.

## Ejecución local

### Opción 1: solo frontend

Abrir el archivo:

```bash
frontend/index.html
```

### Opción 2: backend opcional con Flask

```bash
cd python
python app.py
```

## Planificación Scrum

- Sprint 0: preparación del proyecto, estructura, herramientas, backlog y planificación.
- Sprint 1: interfaz, promociones, búsqueda de productos y carrito básico.
- Sprint 2: recomendaciones, stock, resumen de pedido, registro de interacciones, pruebas y documentación final.

## Equipo

- Product Owner: Anthony
- Scrum Master: Camilo S. Silva
- Backend: Michael Gavino
- Frontend: Alexander Manosalva
- IA / Datos: Jhunior F. Herrera
