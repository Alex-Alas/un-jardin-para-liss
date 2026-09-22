window.AG = window.AG || {};

/**
 * La capa de fotos: los polaroids se dibujan afuera del canvas.
 *
 * El canvas del juego mide 480 × 270 y se agranda con nearest neighbor (`image-rendering:
 * pixelated`), así que una foto dibujada adentro se ve en bloques por más resolución que traiga el
 * archivo. Acá se pone una capa HTML por encima del canvas y cada foto se pega a la posición que le
 * toca, en píxeles de pantalla: la foto usa su resolución completa y el marco, la cinta y los
 * textos siguen siendo pixel art del juego.
 */
(function () {
  const capa = () => document.getElementById('fotos');
  let capas = [];
  let nodos = [];
  let pegadas = [];
  let siguiendo = false;

  function medida() {
    const rect = AG.juego.canvas.getBoundingClientRect();
    return { rect, escala: rect.width / AG.CFG.VIEW_W };
  }

  function recolocar() {
    if (!capas.length || !AG.juego || !AG.juego.canvas) return;
    const { rect, escala } = medida();
    if (!rect.width) return;
    capas.forEach((c, i) => {
      const nodo = nodos[i];
      if (!nodo) return;
      const caja = {
        izquierda: rect.left + c.x * escala,
        arriba: rect.top + c.y * escala,
        ancho: c.ancho * escala,
        alto: c.alto * escala
      };
      const antes = pegadas[i];
      if (antes && antes.izquierda === caja.izquierda && antes.arriba === caja.arriba &&
          antes.ancho === caja.ancho && antes.alto === caja.alto) {
        return;
      }
      nodo.style.left = `${caja.izquierda}px`;
      nodo.style.top = `${caja.arriba}px`;
      nodo.style.width = `${caja.ancho}px`;
      nodo.style.height = `${caja.alto}px`;
      pegadas[i] = caja;
    });
  }

  /**
   * Mientras hay fotos a la vista se las vuelve a pegar en cada frame: el canvas cambia de tamaño
   * cuando Phaser acomoda la escala (y no siempre con un `resize` de la ventana que se pueda
   * escuchar). Es un puñado de elementos y solo se escribe el estilo si la caja cambió.
   */
  function seguir() {
    if (!capas.length) {
      siguiendo = false;
      return;
    }
    recolocar();
    requestAnimationFrame(seguir);
  }

  AG.Fotos = {
    /** Muestra las fotos indicadas. `capas`: [{ id, x, y, ancho, alto }] en píxeles del juego. */
    mostrar(lista) {
      this.ocultar();
      const contenedor = capa();
      if (!contenedor) return;
      capas = lista.slice();
      nodos = capas.map((c) => {
        const imagen = document.createElement('img');
        imagen.src = AG.ASSETS.foto(c.id);
        imagen.alt = '';
        imagen.draggable = false;
        contenedor.appendChild(imagen);
        return imagen;
      });
      recolocar();
      if (!siguiendo) {
        siguiendo = true;
        requestAnimationFrame(seguir);
      }
    },

    ocultar() {
      nodos.forEach((nodo) => nodo.remove());
      nodos = [];
      capas = [];
      pegadas = [];
    },

    recolocar
  };
})();
