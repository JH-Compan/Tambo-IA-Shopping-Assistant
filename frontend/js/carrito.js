const carrito = [];

function agregarAlCarrito(producto) {
  carrito.push(producto);
  renderizarCarrito();
}

function calcularTotalCarrito() {
  return carrito.reduce((total, producto) => total + producto.precio, 0);
}

function renderizarCarrito() {
  const lista = document.getElementById('cartItems');
  const total = document.getElementById('cartTotal');

  if (!lista || !total) return;

  lista.innerHTML = '';

  carrito.forEach((producto) => {
    const item = document.createElement('li');
    item.innerHTML = `<span>${producto.nombre}</span><strong>S/ ${producto.precio.toFixed(2)}</strong>`;
    lista.appendChild(item);
  });

  total.textContent = calcularTotalCarrito().toFixed(2);
}
