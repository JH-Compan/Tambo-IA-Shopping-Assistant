document.addEventListener('DOMContentLoaded', () => {
  const formulario = document.getElementById('chatForm');
  const entrada = document.getElementById('chatInput');

  if (!formulario || !entrada) return;

  formulario.addEventListener('submit', (evento) => {
    evento.preventDefault();

    const texto = entrada.value.trim();
    if (!texto) return;

    agregarMensaje('user', texto);
    const respuesta = procesarMensaje(texto);

    setTimeout(() => {
      agregarMensaje('bot', respuesta);
    }, 300);

    entrada.value = '';
  });
});
