# **Sprint 1 – Primera Versión Funcional**

## **Proyecto**

Tambo AI Shopping Assistant (Tambot)

## **Duración del Sprint**

Sprint 1

## **Objetivo del Sprint**

Desarrollar la primera versión funcional del sistema Tambot, permitiendo a los usuarios interactuar con un chatbot web para consultar promociones, buscar productos y gestionar un carrito de compras básico mediante una arquitectura integrada con Frontend, Backend y Supabase.

# **Sprint Goal**

Construir un chatbot funcional capaz de responder consultas básicas de productos y promociones, integrando la lógica de negocio con una base de datos centralizada.

# **Product Backlog Seleccionado**

| ID | Historia de Usuario | Prioridad |
| ----- | ----- | ----- |
| PB-01 | Consultar promociones vigentes | Crítica |
| PB-02 | Buscar productos por nombre o categoría | Alta |
| PB-04 | Agregar productos a un carrito | Alta |

# **Sprint Backlog**

| ID | Tarea | Estado |
| ----- | ----- | ----- |
| T-S1-01 | Crear pantalla principal del chatbot | Terminado |
| T-S1-02 | Diseñar estilos visuales del chatbot | Terminado |
| T-S1-03 | Implementar flujo básico de conversación | Terminado |
| T-S1-04 | Implementar consulta de promociones vigentes | Terminado |
| T-S1-05 | Implementar búsqueda de productos | Terminado |
| T-S1-06 | Preparar datos de productos y promociones | Terminado |
| T-S1-07 | Implementar carrito de compras básico | En proceso |
| T-S1-08 | Registrar evidencias del Sprint 1 | Terminado |

# **Actividades Realizadas**

## **Frontend**

- Desarrollo de la interfaz conversacional del chatbot.  
- Diseño visual utilizando HTML, CSS y JavaScript.  
- Implementación de componentes interactivos para la conversación.  
- Integración con el backend Flask.

## **Backend**

- Desarrollo de controladores y servicios del chatbot.  
- Implementación de reglas de conversación.  
- Desarrollo de consultas de productos.  
- Desarrollo de consultas de promociones.  
- Integración con Supabase.

## **Base de Datos**

- Diseño inicial de la estructura de datos.  
- Migración de archivos Excel hacia Supabase.  
- Creación de tablas para productos, categorías, promociones, conversaciones e interacciones.  
- Configuración de acceso mediante API.

## **Documentación**

- Elaboración del Product Backlog.  
- Elaboración del Sprint Backlog.  
- Elaboración de Historias de Usuario.  
- Registro de Daily Scrum.  
- Elaboración de documentación técnica y funcional.

# **Arquitectura Implementada**

El sistema quedó compuesto por:

- Frontend Web (HTML, CSS y JavaScript).  
- Backend Flask desarrollado en Python.  
- Base de datos Supabase (PostgreSQL).  
- Repositorio GitHub para control de versiones.  
- Metodología Scrum para la gestión del proyecto.

Flujo general:

Usuario → Interfaz Conversacional → Backend Flask → Supabase → Respuesta al Usuario

# **Incremento Entregado**

Al finalizar el Sprint 1 se dispone de:

- Interfaz conversacional funcional.  
- Consulta de promociones activas.  
- Consulta de productos por nombre o categoría.  
- Integración Frontend-Backend.  
- Integración Backend-Supabase.  
- Flujo inicial de carrito de compras.  
- Sistema de autenticación básico.  
- Persistencia de información en la base de datos.

# **Problemas Encontrados**

- Cambios de arquitectura debido a la migración de Excel hacia Supabase.  
- Dificultades para definir correctamente las entidades y relaciones de la base de datos.  
- Problemas iniciales de permisos para acceder a la API de Supabase.  
- Conflictos durante la integración de ramas mediante Pull Request.  
- Ajustes necesarios para la integración entre Frontend y Backend.

# **Resultados del Sprint**

El Sprint 1 logró cumplir satisfactoriamente los objetivos planteados. Se construyó una versión funcional del chatbot capaz de interactuar con los usuarios y consultar información almacenada en Supabase. La arquitectura quedó preparada para implementar funcionalidades más avanzadas durante el Sprint 2\.

# **Trabajos Pendientes**

1. Completar el carrito de compras.  
2. Implementar recomendaciones personalizadas.  
3. Validar stock en tiempo real.  
4. Registrar interacciones de usuarios.  
5. Implementar Dashboard de Gestión.  
6. Generar métricas y reportes administrativos.  
7. Completar pruebas integrales.  
8. Preparar la demostración final del sistema.

# **Conclusión**

Durante el Sprint 1 se logró desarrollar una primera versión funcional de Tambot, cumpliendo los objetivos definidos al inicio del sprint. El equipo implementó exitosamente la interfaz conversacional, la consulta de promociones, la búsqueda de productos y el flujo inicial del carrito de compras, además de integrar el frontend, el backend desarrollado en Flask y la base de datos en Supabase.

A pesar de los desafíos presentados durante el desarrollo, como la migración de Excel a Supabase, la definición de la estructura de datos y la integración de los distintos componentes del sistema, el equipo logró adaptarse y colaborar de manera efectiva para alcanzar los resultados esperados. Estas dificultades permitieron identificar oportunidades de mejora en la planificación técnica y en la coordinación de tareas.

Asimismo, el Sprint 1 permitió validar la arquitectura propuesta para el proyecto y establecer una base sólida para la incorporación de funcionalidades más avanzadas en los siguientes sprints. Gracias a este incremento, el proyecto cuenta con un producto funcional que demuestra la viabilidad de la solución planteada y facilita la continuación del desarrollo.
