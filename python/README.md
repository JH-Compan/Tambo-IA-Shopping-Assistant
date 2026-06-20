# Backend Flask integrado

Esta rama integra el backend Flask con el frontend del asistente de compras.

## Requisitos

```bash
cd python
pip install -r requirements.txt
```

## Ejecuci?n

```bash
cd python
python app.py
```

Luego abrir:

```txt
http://localhost:5000/
```

## Rutas principales

```txt
GET  /                         Interfaz web integrada
GET  /api                      Informaci?n del backend
POST /api/chat                 Procesar mensaje del chatbot por reglas
POST /api/ordenes              Registrar una orden transaccional
POST /api/chat/cerrar          Cerrar la conversaci?n activa
GET  /api/productos            Listar productos con stock
GET  /api/productos/buscar?q=  Buscar productos por nombre o categor?a
GET  /api/promociones          Ver promociones vigentes
GET  /api/metricas             M?tricas para dashboard
```

## ?rdenes transaccionales

`POST /api/ordenes` registra una orden transaccional usando `public.create_order_transaction` en Supabase.

- Valida el carrito y el usuario antes de invocar el RPC.
- Valida stock y vigencia de promociones dentro de Supabase.
- Calcula precios, subtotales y total solo con datos de la base.
- Descuenta stock en la misma transacci?n.
- Registra la interacci?n `purchased` por cada ?tem comprado.

## Nota

La integraci?n mantiene la arquitectura Flask actual. El flujo de compra usa Supabase para confirmar la orden, calcular los importes y descontar stock de manera at?mica.
