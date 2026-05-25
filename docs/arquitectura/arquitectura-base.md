# Arquitectura Base del Sistema

## 1. Tipo de Solución
Simulación web de un chatbot de recomendaciones para Tambo+ con datos almacenados y persistidos en archivos locales de Microsoft Excel. La solución emula de forma exclusiva la interfaz conversacional de la plataforma WhatsApp Business, procesando texto, flujos de opciones y respuestas dinámicas sin depender de interfaces de comercio electrónico tradicionales.

---

## 2. Capas Propuestas

El sistema se organiza bajo una arquitectura desacoplada de tres capas principales y un componente de backend opcional para la exposición de servicios.

```mermaid
graph TD
    subgraph Capa_Presentacion [1. Capa de Frontend / Presentación]
        A[Interfaz Web Tipo Chat WhatsApp] --> B[Simulación de Mensajes Interactivos]
        B --> C[Captura de Inputs de Usuario]
    end

    subgraph Capa_Logica [2. Capa de Lógica del Sistema / Backend]
        D[Controlador de Flujo Conversacional .py] --> E[Motor de Búsqueda de Productos]
        D --> F[Módulo de Consulta de Promociones]
        D --> G[Algoritmo de Recomendaciones según Historial]
    end

    subgraph Capa_Datos [3. Capa de Datos Simulados / Persistencia]
        H[(Productos.xlsx)]
        I[(Promociones.xlsx)]
        J[(Stock.xlsx)]
        K[(Historial_Compras.xlsx)]
        L[(Interacciones_Chatbot.xlsx)]
    end

    %% Conexiones e intercambio de información
    A <-->|Mensajes de Texto / Eventos JSON| D
    E <--->|Lectura de registros| H
    F <--->|Filtro de ofertas vigentes| I
    G <--->|Cruce de DNI / Celular| K
    G <--->|Validación de disponibilidad| J
    D --->|Log de auditoría| L

    %% Estilos de las cajas
    style Capa_Presentacion fill:#ffffff,stroke:#25D366,stroke-width:2px
    style Capa_Logica fill:#ffffff,stroke:#333333,stroke-width:1px
    style Capa_Datos fill:#ffffff,stroke:#217346,stroke-width:2px
```
sequenceDiagram
    autonumber
    actor Cliente as Cliente (Interfaz Web Chat)
    participant Interfaz as Simulador WhatsApp (HTML/CSS/JS)
    participant Backend as Servidor Chatbot (Python/Flask)
    participant Persistencia as Base de Datos (Excel .xlsx)

    Cliente->>Interfaz: Ingresa número de celular o escribe mensaje inicial
    activate Interfaz
    Interfaz->>Backend: Enviar Petición HTTP POST (Payload JSON con mensaje)
    activate Backend
    
    Backend->>Persistencia: Consulta registro de cliente en 'Historial_Compras.xlsx'
    activate Persistencia
    Persistencia-->>Backend: Retorna datos del usuario y perfil de compras
    deactivate Persistencia

    Backend->>Backend: Procesa algoritmo de recomendación (Cruza historial con ofertas)

    Backend->>Persistencia: Verifica disponibilidad en 'Stock.xlsx'
    activate Persistencia
    Persistencia-->>Backend: Confirma existencias del producto sugerido
    deactivate Persistencia

    Backend-->>Interfaz: Retorna estructura de mensaje de WhatsApp con la recomendación
    deactivate Backend
    
    Interfaz-->>Cliente: Muestra globos de diálogo interactivos con la sugerencia de compra
    deactivate Interfaz
