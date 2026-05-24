# Base de datos simulada en Excel

Esta carpeta almacenará los archivos Excel usados como base de datos simulada del proyecto.

## Archivos esperados

### productos.xlsx

| Campo | Descripción |
|---|---|
| id_producto | Identificador único del producto |
| nombre | Nombre del producto |
| categoria | Categoría del producto |
| precio | Precio regular |
| descripcion | Descripción breve |
| estado | Activo o inactivo |

### promociones.xlsx

| Campo | Descripción |
|---|---|
| id_promocion | Identificador de la promoción |
| producto | Producto asociado |
| descripcion | Detalle de la promoción |
| precio_promocional | Precio con descuento |
| fecha_inicio | Fecha de inicio |
| fecha_fin | Fecha de fin |
| estado | Vigente o inactiva |

### stock.xlsx

| Campo | Descripción |
|---|---|
| id_producto | Identificador del producto |
| tienda | Tienda o sede |
| cantidad | Cantidad disponible |
| disponibilidad | Disponible o agotado |

### historial_compras.xlsx

| Campo | Descripción |
|---|---|
| id_usuario | Identificador del usuario simulado |
| producto | Producto comprado |
| cantidad | Cantidad comprada |
| fecha_compra | Fecha de compra |

### interacciones.xlsx

| Campo | Descripción |
|---|---|
| fecha | Fecha de interacción |
| usuario | Usuario simulado |
| consulta | Mensaje del usuario |
| intencion_detectada | Intención interpretada |
| respuesta | Respuesta generada por el chatbot |
