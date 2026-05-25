## Arquitectura Base del Sistema

El sistema se ha diseñado bajo un patrón de arquitectura desacoplada por capas para la simulación académica de **TamboBot**. Al tratarse de un prototipo controlado, los componentes garantizan el aislamiento entre la presentación visual, la ejecución de la lógica del chatbot y el almacenamiento de datos tabulares.

### Diagrama de Arquitectura de Capas

El siguiente diagrama de bloques representa la organización modular del sistema y el flujo bidireccional de la información desde la interfaz de usuario hasta los archivos de persistencia:

```mermaid
graph TD
    subgraph Capa_Presentacion [1. Capa de Frontend / Presentación]
        A[Interfaz Web Tipo Chat HTML5/CSS3] --> B[Manejo Visual del Carrito]
    end

    subgraph Capa_Logica [2. Capa de Lógica del Sistema / Backend]
        C[Controlador de Flujo Conversacional] --> D[Motor de Búsqueda de Productos]
        C --> E[Módulo de Consulta de Promociones]
        C --> F[Motor de Recomendaciones Básicas LLM/Reglas]
        C --> G[Gestor Lógico del Carrito]
    end

    subgraph Capa_Datos [3. Capa de Datos Simulados / Persistencia]
        H[(Dataset: Productos.xlsx)]
        I[(Dataset: Promociones.xlsx)]
        J[(Dataset: Stock.xlsx)]
        K[(Dataset: Historial_Compras.xlsx)]
        L[(Dataset: Interacciones_Chatbot.xlsx)]
    end

    %% Flujos e Interconexiones Técnicas
    A <-->|Peticiones Asíncronas HTTP JSON| C
    D <-->|Lectura/Filtro de Datos| H
    E <-->|Lectura/Filtro de Datos| I
    F <-->|Cruza Historial e Inventario| K
    F <-->|Valida Disponibilidad| J
    C --->|Log de Sesiones| L

    %% Estilos del Diagrama (Diseño Brutalismo / Minimalista)
    style Capa_Presentacion fill:#ffffff,stroke:#333333,stroke-width:1px
    style Capa_Logica fill:#ffffff,stroke:#333333,stroke-width:1px
    style Capa_Datos fill:#ffffff,stroke:#333333,stroke-width:1px
