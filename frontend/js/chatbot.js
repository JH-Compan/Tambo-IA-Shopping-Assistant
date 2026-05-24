function agregarMensaje(tipo, texto) {
  const contenedor = document.getElementById('chatMessages');
  if (!contenedor) return;

  const mensaje = document.createElement('article');
  mensaje.className = `message ${tipo}`;
  mensaje.innerHTML = `<p>${texto}</p>`;
  contenedor.appendChild(mensaje);
  contenedor.scrollTop = contenedor.scrollHeight;
}

function procesarMensaje(texto) {
  const mensaje = texto.toLowerCase();

  if (mensaje.includes('promo')) {
    const promociones = obtenerPromocionesDemo().map((promo) => `• ${promo}`).join('<br>');
    return `Estas son las promociones vigentes:<br>${promociones}`;
  }

  if (mensaje.includes('buscar')) {
    const termino = mensaje.replace('buscar', '').trim();
    const resultados = buscarProductosDemo(termino);

    if (resultados.length === 0) {
      return 'No encontré productos con ese criterio. Intenta con bebidas, snacks o dulces.';
    }

    const lista = resultados.map((producto) => `• ${producto.nombre} - S/ ${producto.precio.toFixed(2)}`).join('<br>');
    return `Encontré estos productos:<br>${lista}<br><br>Para agregar un producto escribe: agregar gaseosa, agregar papas, agregar chocolate o agregar agua.`;
  }

  if (mensaje.includes('recomienda') || mensaje.includes('recomendación') || mensaje.includes('recomendacion')) {
    const recomendaciones = obtenerRecomendacionesDemo()
      .map((producto) => `• ${producto.nombre} - S/ ${producto.precio.toFixed(2)}`)
      .join('<br>');
    return `Te recomiendo estos productos populares:<br>${recomendaciones}`;
  }

  if (mensaje.includes('agregar')) {
    const producto = productosDemo.find((item) => mensaje.includes(item.nombre.split(' ')[0].toLowerCase()));

    if (!producto) {
      return 'No pude identificar el producto para agregarlo al carrito.';
    }

    agregarAlCarrito(producto);
    return `${producto.nombre} fue agregado al carrito.`;
  }

  if (mensaje.includes('carrito') || mensaje.includes('resumen')) {
    if (carrito.length === 0) {
      return 'Tu carrito está vacío por ahora.';
    }

    const resumen = carrito.map((producto) => `• ${producto.nombre} - S/ ${producto.precio.toFixed(2)}`).join('<br>');
    return `Resumen del pedido:<br>${resumen}<br><br>Total: S/ ${calcularTotalCarrito().toFixed(2)}`;
  }

  return 'Puedo ayudarte con promociones, búsqueda de productos, recomendaciones y carrito simulado.';
}
