// Contador de caracteres para las áreas de texto con límites.
// Es solo una ayuda visual: el servidor valida siempre, después de retirar espacios externos.
document.querySelectorAll("textarea[data-min][data-max]").forEach((area) => {
  const contador = document.createElement("p");
  contador.className = "contador";
  contador.setAttribute("aria-live", "polite");
  area.insertAdjacentElement("afterend", contador);

  const actualizar = () => {
    const largo = area.value.trim().length;
    contador.textContent = `${largo} caracteres (entre ${area.dataset.min} y ${area.dataset.max})`;
  };
  area.addEventListener("input", actualizar);
  actualizar();
});
