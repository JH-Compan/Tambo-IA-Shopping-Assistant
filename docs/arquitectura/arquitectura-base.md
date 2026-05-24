# Arquitectura base

## Tipo de solución

Simulación web de chatbot para Tambo+ con datos almacenados en archivos Excel.

## Capas propuestas

1. **Frontend**
   - Interfaz web tipo chat.
   - Manejo visual del carrito.
   - Comunicación simulada con la lógica del chatbot.

2. **Lógica del sistema**
   - Flujo conversacional.
   - Búsqueda de productos.
   - Consulta de promociones.
   - Recomendaciones básicas.
   - Manejo del carrito.

3. **Datos simulados**
   - Productos.
   - Promociones.
   - Stock.
   - Historial de compras.
   - Interacciones del chatbot.

4. **Backend opcional**
   - Python con Flask para leer Excel o centralizar reglas del chatbot.

## Decisiones técnicas iniciales

- El proyecto será una simulación académica.
- No se conectará a WhatsApp real.
- No se usará pasarela de pago real.
- Excel funcionará como base de datos simulada.
- El frontend podrá funcionar inicialmente con JavaScript puro.
