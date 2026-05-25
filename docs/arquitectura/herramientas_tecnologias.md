## Herramientas y Tecnologías del Proyecto

Para la construcción del prototipo y la simulación del ecosistema de recomendación automatizada de Tambo+, se ha seleccionado un stack tecnológico optimizado para entornos de desarrollo ágiles. Los componentes han sido elegidos para garantizar la viabilidad del desarrollo y un flujo de datos limpio durante la simulación.

### Stack Tecnológico Seleccionado

| Herramienta / Tecnología | Especificación Técnica | Rol / Función en la Simulación |
| :--- | :--- | :--- |
| ![](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) | Estándar W3C | Maquetación de la interfaz del catálogo y simulación del entorno de chat de WhatsApp. |
| ![](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) | Diseño Plano / Moderno | Estilos, tipografías y estructura visual del simulador interactivo. |
| ![](https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white) | Entorno de Ejecución Backend | Orquestador principal: procesamiento de cadenas, lógica del bot y motor de reglas de recomendación. |
| ![](https://img.shields.io/badge/MS_Excel_/.XLSX-217346?style=flat-square&logo=microsoft-excel&logoColor=white) | Base de Datos Plana (Tabular) | Almacenamiento y persistencia de datos (Dataset de inventario y dataset del historial CRM de clientes). |
| ![](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white) | Control de Versiones Local | Gestión de cambios, confirmaciones (commits) e historial de desarrollo del código. |
| ![](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white) | Repositorio Remoto | Alojar el código fuente del proyecto, realizar el trabajo colaborativo del equipo y publicar la documentación. |
| Campaña / API (Simulación) | WhatsApp Business Platform | Emulación del comportamiento del Webhook receptor de mensajes de los usuarios. |
| ![](https://img.shields.io/badge/VS_Code-007ACC?style=flat-square&logo=visual-studio-code&logoColor=white) | IDE de Desarrollo | Entorno unificado para la escritura, depuración y ejecución de los scripts y archivos del proyecto. |

---

### Diagrama de Arquitectura de la Simulación

El siguiente diagrama detalla el flujo de información y la interacción entre las herramientas seleccionadas para simular el comportamiento del sistema:

```mermaid
graph LR
    subgraph Capa_Usuario [Interfaz y Canal]
        A[Cliente / WhatsApp] -->|Mensaje / Petición| B[Simulador Web HTML/CSS]
    end

    subgraph Capa_Logica [Backend & Inteligencia]
        B -->|HTTP Request / Payload| C[Servidor Core Python .py]
        C -->|Procesamiento de Lenguaje y Reglas| C
    end

    subgraph Capa_Datos [Persistencia de Datos]
        C -->|Lectura de Historial CRM| D[Dataset Excel: Clientes.xlsx]
        C -->|Validación de Stock| E[Dataset Excel: Inventario.xlsx]
    end

    style Capa_Usuario fill:#f9f9f9,stroke:#333,stroke-width:1px
    style Capa_Logica fill:#f5f5f5,stroke:#333,stroke-width:1px
    style Capa_Datos fill:#f0f0f0,stroke:#333,stroke-width:1px
