window.AG = window.AG || {};

/**
 * Pantalla completa en el celular: en horizontal la barra del navegador y la del
 * sistema se comen medio juego. Se pide con un gesto del jugador (la API lo exige).
 *
 * Por qué fallaba: el intento viejo era de un solo tiro (`pedida = true` antes de
 * saber si funcionó) y en iPhone la Fullscreen API no existe para elementos
 * genéricos, así que no hacía nada y nunca reintentaba.
 */
(function () {
  let ultimoIntento = 0;

  function soportada() {
    const raiz = document.documentElement;
    return Boolean(raiz.requestFullscreen || raiz.webkitRequestFullscreen);
  }

  function activa() {
    return Boolean(document.fullscreenElement || document.webkitFullscreenElement);
  }

  function refrescarPhaser() {
    try {
      if (window.AG && AG.juego && AG.juego.scale) AG.juego.scale.refresh();
    } catch (e) {
      // El canvas se queda como está; no es grave.
    }
  }

  /** Truco para iPhone (sin Fullscreen API): esconde lo que se pueda y estira al alto real. */
  function trucoIOS() {
    document.body.classList.add('pantalla-ios');
    try {
      window.scrollTo(0, 1);
    } catch (e) {
      // Nada que hacer.
    }
    refrescarPhaser();
  }

  function pedir() {
    const ahora = Date.now();
    if (ahora - ultimoIntento < 800 || activa()) return false;
    ultimoIntento = ahora;

    const raiz = document.documentElement;
    const pedirNativo = raiz.requestFullscreen || raiz.webkitRequestFullscreen;
    if (!pedirNativo) {
      trucoIOS();
      return false;
    }
    try {
      let promesa = null;
      if (raiz.requestFullscreen) {
        try {
          promesa = raiz.requestFullscreen({ navigationUI: 'hide' });
        } catch (e) {
          promesa = raiz.requestFullscreen();
        }
      } else {
        promesa = pedirNativo.call(raiz);
      }
      const hecha = promesa && promesa.then
        ? promesa.then(() => {
          try {
            const bloqueo = screen.orientation && screen.orientation.lock
              ? screen.orientation.lock('landscape')
              : null;
            if (bloqueo && bloqueo.catch) bloqueo.catch(() => {});
          } catch (e) {
            // El bloqueo horizontal es un extra; si falla, igual se juega.
          }
          refrescarPhaser();
          return true;
        })
        : Promise.resolve(true);
      hecha.catch(() => {
        // Lo rechazó el navegador (sin gesto válido, iframe sin permiso, etc.):
        // se reintenta en el próximo toque en vez de rendirse.
        ultimoIntento = 0;
      });
      return true;
    } catch (e) {
      ultimoIntento = 0;
      return false;
    }
  }

  function salir() {
    try {
      if (document.exitFullscreen) document.exitFullscreen();
      else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
    } catch (e) {
      // Nada que hacer.
    }
  }

  function alternar() {
    if (activa()) salir();
    else pedir();
  }

  document.addEventListener('fullscreenchange', refrescarPhaser);
  document.addEventListener('webkitfullscreenchange', refrescarPhaser);
  window.addEventListener('orientationchange', () => {
    if (!soportada()) setTimeout(() => window.scrollTo(0, 1), 240);
  });

  // En táctiles se pide sola en los primeros toques (cada intento necesita gesto).
  if (window.matchMedia('(pointer: coarse)').matches) {
    document.addEventListener('pointerdown', () => pedir());
  }

  AG.Pantalla = { soportada, activa, pedir, salir, alternar };
})();
