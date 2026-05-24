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
Tambo-IA-Shopping-Assistant/
│
├── docs/                              # Documentación del proyecto
│   │
│   ├── scrum/                         # Documentos Scrum del proyecto
│   │   ├── sprint-0.md                # Documento del Sprint 0
│   │   ├── sprint-1.md                # Documento del Sprint 1
│   │   ├── sprint-2.md                # Documento del Sprint 2
│   │   │
│   │   └── daily-scrum/               # Registro de reuniones Daily Scrum
│   │       ├── sprint-1/
│   │       │   ├── daily-01.md
│   │       │   ├── daily-02.md
│   │       │   └── daily-03.md
│   │       │
│   │       └── sprint-2/
│   │           ├── daily-01.md
│   │           ├── daily-02.md
│   │           └── daily-03.md
│   │
│   ├── backlog/                       # Historias de usuario y backlogs
│   │   ├── historias-usuario.md       # Historias de usuario del sistema
│   │   ├── product-backlog.md         # Product Backlog priorizado
│   │   └── sprint-backlog.md          # Tareas seleccionadas por sprint
│   │
│   ├── arquitectura/                  # Documentación técnica
│   │   ├── arquitectura-base.md       # Arquitectura general del sistema
│   │   ├── decisiones-tecnicas.md     # Decisiones técnicas del proyecto
│   │   └── diagramas.md               # Diagramas del sistema
│   │
│   └── evidencias/                    # Evidencias por sprint
│       ├── sprint-0/
│       ├── sprint-1/
│       └── sprint-2/
│
├── frontend/                          # Interfaz web del chatbot
│   ├── index.html                     # Página principal
│   │
│   ├── css/
│   │   └── styles.css                 # Estilos visuales
│   │
│   ├── js/                            # Lógica del frontend
│   │   ├── app.js                     # Inicialización general
│   │   ├── chatbot.js                 # Flujo del chatbot
│   │   ├── carrito.js                 # Carrito de compras
│   │   ├── recomendaciones.js         # Recomendaciones
│   │   └── productos.js               # Productos y búsqueda
│   │
│   └── assets/                        # Imágenes, logos e íconos
│
├── data/                              # Archivos Excel usados como base de datos
│   ├── productos.xlsx                 # Catálogo de productos
│   ├── promociones.xlsx               # Promociones vigentes
│   ├── stock.xlsx                     # Disponibilidad de productos
│   ├── historial_compras.xlsx         # Historial simulado de clientes
│   └── interacciones.xlsx             # Registro de interacciones del chatbot
│
├── python/                            # Backend opcional
│   ├── app.py                         # Aplicación Flask
│   ├── requirements.txt               # Dependencias Python
│   └── README.md                      # Guía del backend
│
├── tests/                             # Pruebas del sistema
│   ├── pruebas-promociones.md
│   ├── pruebas-busqueda.md
│   ├── pruebas-carrito.md
│   └── pruebas-recomendaciones.md
│
├── README.md                          # Presentación principal del proyecto
├── .gitignore                         # Archivos ignorados por Git
└── Dockerfile                         # Configuración opcional para Docker
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
