# Tambo AI Shopping Assistant / Tambot

<p align="center">
  <strong>Simulación web de un asistente de compras inteligente para Tambo+</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Estado-En%20desarrollo-yellow" />
  <img src="https://img.shields.io/badge/Scrum-Sprint%200-blue" />
  <img src="https://img.shields.io/badge/Frontend-HTML%20%7C%20CSS%20%7C%20JS-orange" />
  <img src="https://img.shields.io/badge/Base%20de%20datos-Excel-green" />
</p>

---

## Descripción

**Tambot** es una simulación web de un asistente de compras para **Tambo+**. El sistema permite consultar promociones, buscar productos, recibir recomendaciones básicas, agregar productos a un carrito y visualizar un resumen de pedido usando archivos Excel como base de datos simulada.

Este repositorio corresponde al proyecto del curso de **Ingeniería de Software** y se desarrolla bajo la metodología **Scrum**, iniciando con Sprint 0 como etapa de preparación.

---

## Tabla de contenidos

- [Objetivo del producto](#objetivo-del-producto)
- [Funcionalidades](#funcionalidades)
- [MVP delimitado](#mvp-delimitado)
- [Tecnologías](#tecnologías)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Ejecución local](#ejecución-local)
- [Documentación Scrum](#documentación-scrum)
- [Planificación Scrum](#planificación-scrum)
- [Equipo](#equipo)
- [Estado del proyecto](#estado-del-proyecto)

---

## Objetivo del producto

Construir una simulación web de un asistente de compras para Tambo+ que permita a los clientes consultar promociones, buscar productos, recibir recomendaciones básicas y armar un pedido simulado usando Excel como base de datos.

---

## Funcionalidades

- Consulta de promociones vigentes.
- Búsqueda de productos por nombre o categoría.
- Recomendaciones básicas de productos.
- Validación básica de disponibilidad.
- Carrito de compras simulado.
- Resumen de pedido.
- Registro de interacciones básicas.

---

## MVP delimitado

### Incluye

- Interfaz web tipo chat.
- Consulta de promociones vigentes.
- Búsqueda de productos por nombre o categoría.
- Lectura de datos desde Excel.
- Validación básica de disponibilidad.
- Carrito de compras simulado.
- Resumen de pedido.
- Registro o consulta de interacciones básicas.

### No incluye

- Integración real con WhatsApp Business API.
- Inteligencia artificial real conectada a una API externa.
- Pago real o pasarela de pagos.
- Delivery real.
- CRM real.
- Despliegue productivo en nube.

---

## Tecnologías

### Principales

| Área | Tecnología | Uso |
|---|---|---|
| Frontend | HTML | Estructura de la interfaz web |
| Frontend | CSS | Diseño visual del chatbot |
| Frontend | JavaScript | Interacción, flujo del chatbot, carrito y recomendaciones |
| Datos | Excel | Base de datos simulada |
| Control de versiones | Git | Registro de cambios del proyecto |
| Repositorio | GitHub | Código, issues, backlog y documentación |
| Documentación | Google Drive / Google Docs | Documentos Scrum y evidencias |

### Opcionales

| Área | Tecnología | Uso |
|---|---|---|
| Backend | Python + Flask | Lectura de Excel y lógica opcional del sistema |
| Librería | openpyxl | Manejo de archivos Excel desde Python |
| Contenedores | Docker | Ejecución opcional del proyecto en contenedor |

---

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
│   │       └── sprint-2/
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
│   ├── css/
│   │   └── styles.css                 # Estilos visuales
│   ├── js/                            # Lógica del frontend
│   │   ├── app.js                     # Inicialización general
│   │   ├── chatbot.js                 # Flujo del chatbot
│   │   ├── carrito.js                 # Carrito de compras
│   │   ├── recomendaciones.js         # Recomendaciones
│   │   └── productos.js               # Productos y búsqueda
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

---

## Ejecución local

### Opción 1: ejecutar solo frontend

Abrir el archivo en el navegador:

```bash
frontend/index.html
```

### Opción 2: ejecutar backend opcional con Flask

```bash
cd python
pip install -r requirements.txt
python app.py
```

---

## Documentación Scrum

- [Sprint 0](docs/scrum/sprint-0.md)
- [Sprint 1](docs/scrum/sprint-1.md)
- [Sprint 2](docs/scrum/sprint-2.md)
- [Historias de usuario](docs/backlog/historias-usuario.md)
- [Product Backlog](docs/backlog/product-backlog.md)
- [Sprint Backlog](docs/backlog/sprint-backlog.md)
- [Arquitectura base](docs/arquitectura/arquitectura-base.md)

---

## Planificación Scrum

| Sprint | Objetivo |
|---|---|
| Sprint 0 | Preparar documentación, backlog, repositorio, herramientas y planificación inicial. |
| Sprint 1 | Crear la primera versión funcional con interfaz, promociones, búsqueda y carrito básico. |
| Sprint 2 | Completar recomendaciones, stock, resumen de pedido, pruebas y evidencias finales. |

---

## Equipo

| Rol | Responsable |
|---|---|
| Product Owner | Anthony |
| Scrum Master | Camilo S. Silva |
| Backend | Michael Gavino |
| Frontend | Alexander Manosalva |
| IA / Datos | Jhunior F. Herrera |

---

## Estado del proyecto

El proyecto se encuentra en etapa de preparación y desarrollo inicial bajo Scrum. Actualmente se está trabajando en la organización del Sprint 0, estructura del repositorio, documentación base y planificación de los próximos sprints.

---

## Licencia

Proyecto académico desarrollado para el curso de Ingeniería de Software.
