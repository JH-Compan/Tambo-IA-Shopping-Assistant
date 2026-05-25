<p align="center">
  <strong>Portada</strong>
</p>
<p align="center">
  <strong>Proyecto:</strong> Tambo AI Shopping Assistant / Tambot
</p>
<p align="center">
  <strong>Integrantes:</strong>
</p>

<p align="center">
  1. HERRERA VALERIANO JHUNIOR FERNANDO
</p>
<p align="center">
  2. MANOSALVA PERALTA YOJAN ALEXANDER
</p>
<p align="center">
  3. ZUÑIGA VASQUEZ ANTONY GEAMPIER
</p>
<p align="center">
  4. GAVINO ISIDRO MICHAEL RICHARD
</p>
<p align="center">
  5. SILVA CUZQUI CAMILO SEBASTIAN
</p>
<p align="center">
  <strong>Curso:</strong> Ingeniería de Software
</p>
<p align="center">
  <strong>Docente:</strong> HUAPALLA GARCIA JUAN MANUEL
</p>
<p align="center">
  <strong>Fecha:</strong> 24 DE MAYO DEL 2026
</p>


## 1. Introducción
- En este documento se explicará la preparación inicial del proyecto Tambo AI Shopping Assistant / Tambot. El Sprint 0 tiene como finalidad establecer buenas bases para el desarrollo, definiendo los artefactos principales del proyecto, como el alcance, las herramientas y tecnologías, la estructura del repositorio, las historias de usuario, el Product Backlog y la planificación de los Sprint 1 y Sprint 2.

## 2. Alcance

### Incluye

- Organización general del proyecto.
- Definición del alcance inicial del sistema.
- Organización de las historias de usuario.
- Elaboración del Product Backlog.
- Definición de herramientas y tecnologías.
- Estructuración del repositorio en GitHub.
- Preparación de la documentación inicial.
- Planificación general del Sprint 1 y Sprint 2.
- Definición de roles del equipo.
- Registro inicial de issues en GitHub.

### No incluye

- Integración real con WhatsApp Business.
- Uso de inteligencia artificial real conectada a una API externa.
- Pago real o pasarela de pagos.
- Delivery real.
- Conexión con CRM o inventario real de Tambo+.
- Despliegue productivo en la nube.

## 3. Visión resumida
- Una simulación web de chatbot para Tambo+ que permite consultar promociones, buscar productos, recibir recomendaciones básicas, agregar productos al carrito y visualizar un resumen de pedido usando Excel como base de datos simulada.
## 4. Historias de usuario
- [Ver historias de usuario](../backlog/historias-usuario.md)
## 5. Product Backlog
- [Ver Product Backlog](../backlog/product-backlog.md)
## 6. Herramientas y tecnologías
- [Ver herramientas y tecnologías](../arquitectura/herramientas_tecnologias.md)
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


## 7. Estructura base del repositorio

    Tambo-IA-Shopping-Assistant/
    │
    ├── docs/
    │   │
    │   ├── scrum/
    │   │   ├── sprint-0.md
    │   │   ├── sprint-1.md
    │   │   ├── sprint-2.md
    │   │   │
    │   │   └── daily-scrum/
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
    │   ├── backlog/
    │   │   ├── historias-usuario.md
    │   │   ├── product-backlog.md
    │   │   └── sprint-backlog.md
    │   │
    │   ├── arquitectura/
    │   │   ├── arquitectura-base.md
    │   │   ├── decisiones-tecnicas.md
    │   │   └── diagramas.md
    │   │
    │   └── evidencias/
    │       ├── sprint-0/
    │       │   └── README.md
    │       ├── sprint-1/
    │       │   └── README.md
    │       └── sprint-2/
    │           └── README.md
    │
    ├── frontend/
    │   ├── index.html
    │   │
    │   ├── css/
    │   │   └── styles.css
    │   │
    │   ├── js/
    │   │   ├── app.js
    │   │   ├── chatbot.js
    │   │   ├── carrito.js
    │   │   ├── recomendaciones.js
    │   │   └── productos.js
    │   │
    │   └── assets/
    │       └── README.md
    │
    ├── data/
    │   ├── README.md
    │   ├── productos.xlsx
    │   ├── promociones.xlsx
    │   ├── stock.xlsx
    │   ├── historial_compras.xlsx
    │   └── interacciones.xlsx
    │
    ├── python/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── README.md
    │
    ├── tests/
    │   ├── README.md
    │   ├── pruebas-promociones.md
    │   ├── pruebas-busqueda.md
    │   ├── pruebas-carrito.md
    │   └── pruebas-recomendaciones.md
    │
    ├── README.md
    ├── .gitignore
    └── Dockerfile
## 8. Planificación sprint 1 y 2
- [Ver planificaciones](../backlog/sprint-backlog.md)
## 9. Roles
- Product Owner: Anthony
- Scrum Master: Camilo S. Silva
- Backend: Michael Gavino
- Frontend: Alexander Manosalva
- IA / Datos: Jhunior F. Herrera
