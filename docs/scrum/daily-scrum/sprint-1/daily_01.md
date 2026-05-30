# **Registro de Daily Scrum – Tambo IA Shopping Assistant**

## **Fecha**

30 / 05 / 2026

## **Sprint**

Sprint 1 – Desarrollo de la Primera Versión Funcional

## **Participantes**

* Camilo Silva  
* Yojan Manosalva  
* Junior Herrera  
* Michael Gavino  
* Antony Zuñiga

---

## **Camilo**

### **Actividades realizadas**

- Organizó y distribuyó las tareas entre los integrantes del equipo.  
- Supervisó el avance general del Sprint.  
- Coordinó la integración de los distintos componentes desarrollados por el equipo.  
- Implementó la conexión entre el backend y Supabase para reemplazar el almacenamiento basado en archivos Excel.  
- Configuró la integración necesaria para que el sistema pudiera utilizar la base de datos en la nube de manera centralizada.

### **Actividades próximas**

- Continuar supervisando el avance del Sprint.  
- Coordinar la integración de nuevas funcionalidades.  
- Apoyar la resolución de problemas técnicos que puedan surgir durante el desarrollo.

### **Impedimentos**

- Problemas de acceso a la base de datos durante las pruebas de integración:  
  Durante las pruebas realizadas en la rama Test, donde se integró el frontend con el backend, las consultas a la base de datos no retornaban información debido a la falta de permisos de lectura sobre algunas tablas de Supabase. Esto dificultó la validación de la integración completa del sistema hasta que se configuraron correctamente los accesos necesarios.  
- Conflictos durante la integración mediante Pull Request (PR):  
  Al realizar la integración de cambios desde distintas ramas del proyecto, surgieron conflictos en archivos modificados por varios integrantes. Fue necesario revisar manualmente los cambios, analizar qué fragmentos de código debían mantenerse y resolver los conflictos antes de completar la fusión de ramas.

## **Yojan**

### **Actividades realizadas**

- Desarrolló la interfaz gráfica principal del sistema.  
- Implementó la simulación de una conversación tipo chat inspirada en WhatsApp.  
- Integró la interacción entre el usuario y el chatbot.  
- Configuró la visualización de mensajes enviados y recibidos.  
- Adaptó la interfaz para mostrar correctamente las respuestas generadas por el backend.

### **Actividades próximas**

- Mejorar la experiencia de usuario de la interfaz.  
- Optimizar la presentación de productos y promociones.  
- Realizar pruebas de integración con el backend.

### **Impedimentos**

- Ninguno reportado.

## **Junior**

### **Actividades realizadas**

- Diseñó la estructura de persistencia de datos del proyecto.  
- Inicialmente evaluó el uso de archivos Excel como mecanismo de almacenamiento.  
- Analizó alternativas de persistencia más escalables.  
- Migró la estrategia de almacenamiento hacia Supabase y PostgreSQL.  
- Diseñó y creó las tablas necesarias para productos, promociones, conversaciones, usuarios e interacciones.

### **Actividades próximas**

- Optimizar consultas y relaciones entre tablas.  
- Apoyar las pruebas de persistencia e integridad de datos.

### **Impedimentos**

- Ausencia inicial de un diagrama Entidad-Relación (DER) definido:  
  Durante las primeras etapas del proyecto no se contaba con un modelo de datos formalizado, lo que generó incertidumbre respecto a la estructura de la base de datos. Esto provocó múltiples iteraciones y modificaciones en el diseño de tablas, relaciones y atributos a medida que avanzaba el desarrollo.  
- Dificultad para definir los campos necesarios:  
  Fue necesario realizar varios análisis para determinar qué información debía almacenarse en cada entidad del sistema. En diferentes momentos surgieron dudas sobre qué atributos eran realmente necesarios para soportar las funcionalidades del chatbot y cuáles podían considerarse redundantes.  
- Incertidumbre durante la migración tecnológica:  
  Inicialmente se planteó utilizar archivos Excel como mecanismo de persistencia de datos. Sin embargo, posteriormente se decidió migrar a Supabase y PostgreSQL, lo que generó dudas respecto a la estrategia de implementación, estructura de tablas y adaptación del sistema a la nueva tecnología.  
- Ajustes continuos en el modelo de datos:  
  Debido a los cambios de requerimientos y a la evolución del proyecto, fue necesario modificar varias veces la estructura de la base de datos para adaptarla a las necesidades reales del sistema y garantizar la compatibilidad con el backend y el chatbot.

## **Michael**

### **Actividades realizadas**

- Implementó la estructura principal del backend en Python.  
- Desarrolló los controladores (Controllers) del sistema.  
- Implementó los repositorios (Repositories) para acceso a datos.  
- Desarrolló la lógica de negocio mediante servicios (Services).  
- Configuró los endpoints y el flujo de comunicación entre frontend y backend.  
- Participó en la integración de los módulos conversacionales del chatbot.

### **Actividades próximas**

- Continuar refinando la lógica del chatbot.  
- Realizar pruebas de integración y corrección de errores.

### **Impedimentos**

- Cambio de tecnología para la persistencia de datos:  
  El desarrollo inicial del backend se realizó considerando archivos Excel como fuente principal de datos. Posteriormente, al decidir migrar a Supabase y PostgreSQL, fue necesario adaptar parte de la lógica implementada, modificar consultas y reestructurar componentes para trabajar con la nueva arquitectura.  
- Falta de acceso oportuno a la base de datos:  
  Durante una etapa del desarrollo no se contaba con los permisos ni credenciales necesarios para acceder a la API y a los recursos de Supabase. Esto limitó la posibilidad de realizar pruebas completas de integración entre el backend y la base de datos.  
- Adaptación de la arquitectura del backend:  
  La migración hacia Supabase implicó revisar y actualizar repositorios, servicios y controladores para garantizar la correcta comunicación con la base de datos. Este proceso requirió tiempo adicional de análisis y validación.  
- Pruebas de integración entre módulos:  
  Una vez implementados los cambios en la persistencia, fue necesario realizar múltiples pruebas para verificar que la comunicación entre frontend, backend y base de datos funcionara correctamente, identificando y corrigiendo inconsistencias durante el proceso.

## **Antony**

## **Actividades realizadas**

- Elaboró la documentación técnica y funcional del proyecto.  
- Documentó la arquitectura general del sistema.  
- Elaboró diagramas y descripciones de componentes.  
- Investigó alternativas tecnológicas para la implementación del chatbot.  
- Apoyó al equipo mediante investigación técnica relacionada con la integración de código y nuevas funcionalidades.  
- Participó en la elaboración de documentación del Sprint y seguimiento del proyecto.

### **Actividades próximas**

- Continuar con la documentación del Sprint.  
- Mantener actualizada la documentación técnica del sistema.  
- Documentar nuevas funcionalidades implementadas por el equipo.

### **Impedimentos**

- Adaptación a los cambios de arquitectura del proyecto:  
  Durante el proceso de documentación fue necesario comprender y actualizar constantemente la información debido a los cambios realizados en la arquitectura del sistema. Esto implicó revisar nuevamente diagramas, componentes y flujos de trabajo para mantener la documentación alineada con la implementación real.  
- Comprensión del flujo completo del sistema:  
  Inicialmente existieron dificultades para entender completamente la interacción entre los distintos módulos del proyecto (frontend, backend, servicios, repositorios y base de datos). Por ello, fue necesario realizar sesiones de análisis e investigación para documentar correctamente el funcionamiento del sistema.  
- Migración de Excel a Supabase:  
  Parte de la documentación había sido elaborada considerando una arquitectura basada en archivos Excel como mecanismo de persistencia. Cuando el equipo decidió migrar hacia Supabase y PostgreSQL, fue necesario modificar diagramas, descripciones técnicas y documentación previamente desarrollada para reflejar la nueva solución tecnológica.  
- Apoyo al equipo mediante investigación técnica:  
  Uno de los desafíos fue encontrar información técnica que permitiera comprender mejor las herramientas utilizadas en el proyecto y apoyar a los demás integrantes en la resolución de dudas relacionadas con la arquitectura, integración de componentes y funcionamiento general del sistema.  
- Mantener la documentación sincronizada con el desarrollo:  
  Debido a la evolución constante del proyecto, se requirió actualizar frecuentemente la documentación para que reflejara fielmente el estado actual del sistema, evitando inconsistencias entre los documentos y la implementación realizada por el equipo.

## **Resumen General**

Durante el desarrollo del Sprint, el equipo logró avances significativos en la construcción del proyecto Tambo IA Shopping Assistant. Se completó el desarrollo de la interfaz web simulando un chat tipo WhatsApp, se implementó la arquitectura backend utilizando Python y Flask, y se diseñó la estructura de persistencia de datos mediante Supabase y PostgreSQL.

Así mismo se realizó la migración de la estrategia pensada en un principio en archivos Excel hacia una solución más escalable utilizando Supabase. Esto permitió mejorar la organización de los datos y facilitar la integración entre los distintos módulos del sistema.

El equipo trabajó de manera colaborativa en la integración de frontend, backend y base de datos, resolviendo problemas relacionados con permisos de acceso, conflictos de integración mediante Pull Request. Se desarrolló la documentación técnica del proyecto, incluyendo diagramas, arquitectura, flujo convencional y artefactos Scrum.

