const productosDemo = [
  { nombre: 'Gaseosa personal', categoria: 'Bebidas', precio: 3.50, stock: true },
  { nombre: 'Papas clásicas', categoria: 'Snacks', precio: 2.80, stock: true },
  { nombre: 'Chocolate', categoria: 'Dulces', precio: 2.50, stock: true },
  { nombre: 'Agua mineral', categoria: 'Bebidas', precio: 2.00, stock: true }
];

function obtenerPromocionesDemo() {
  return [
    'Combo gaseosa + papas por S/ 5.90',
    '2 chocolates por S/ 4.50',
    'Agua mineral con descuento a S/ 2.00'
  ];
}

function buscarProductosDemo(texto) {
  const busqueda = texto.toLowerCase();
  return productosDemo.filter((producto) =>
    producto.nombre.toLowerCase().includes(busqueda) ||
    producto.categoria.toLowerCase().includes(busqueda)
  );
}

function obtenerRecomendacionesDemo() {
  return productosDemo.slice(0, 3);
}
