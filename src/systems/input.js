window.AG = window.AG || {};

(function () {
  const c = (v) => AG.UI.color(v);

  AG.Entrada = class Entrada {
    /**
     * `controles: false` deja la escena sin D-pad ni botón A (los créditos, el álbum del título):
     * ahí no hay nada que caminar y la escena escucha sus propios toques.
     */
    constructor(scene, opciones = {}) {
      this.scene = scene;
      this.teclas = scene.input.keyboard.addKeys({
        arriba: 'UP',
        abajo: 'DOWN',
        izquierda: 'LEFT',
        derecha: 'RIGHT',
        w: 'W',
        a: 'A',
        s: 'S',
        d: 'D',
        accion: 'Z',
        accion2: 'ENTER',
        pausa: 'ESC'
      });
      this.botonA = false;
      this.botonAPulsado = false;
      this.toqueLibre = false;
      this.silencioHasta = 0;
      this.ejeTactil = { x: 0, y: 0 };
      this.controles = [];
      this.ocultosPor = new Set();
      if (opciones.controles !== false) this.crearControles();
    }

    crearControles() {
      if (!this.hayTactil()) return;
      const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
      const centro = { x: 54, y: VIEW_H - 46 };
      const radioZona = 34;

      this.zonaDpad = this.scene.add
        .circle(centro.x, centro.y, radioZona, c(COLORES.blanco), 0.12)
        .setScrollFactor(0)
        .setDepth(1000)
        .setInteractive();
      this.zonaDpad.setStrokeStyle(2, c(COLORES.blanco), 0.25);

      // Flechas de verdad (triángulos con borde oscuro): sobre los fondos pintados, los cuadraditos
      // blancos de antes se perdían entre las nubes y las flores.
      [['izquierda', -17, 0, 180], ['derecha', 17, 0, 0], ['arriba', 0, -17, 270], ['abajo', 0, 17, 90]].forEach(([nombre, dx, dy, angulo]) => {
        const flecha = this.scene.add
          .triangle(centro.x + dx, centro.y + dy, 0, 0, 0, 10, 8, 5, c(COLORES.blanco), 0.8)
          .setStrokeStyle(1, c(COLORES.tinta), 0.7)
          .setAngle(angulo)
          .setScrollFactor(0)
          .setDepth(1001);
        flecha.nombre = nombre;
        this.controles.push(flecha);
      });

      const boton = this.scene.add
        .circle(VIEW_W - 52, VIEW_H - 46, 24, c(COLORES.amarillo), 0.22)
        .setScrollFactor(0)
        .setDepth(1000)
        .setInteractive();
      boton.setStrokeStyle(2, c(COLORES.amarillo), 0.7);
      this.textoBoton = AG.UI.texto(this.scene, VIEW_W - 52, VIEW_H - 52, 'A', { color: COLORES.amarillo })
        .setOrigin(0.5)
        .setScrollFactor(0)
        .setDepth(1001);
      this.controles.push(boton, this.textoBoton);

      this.scene.input.on('pointerdown', (p) => this.pointerAbajo(p, centro));
      // Arrastrar solo mueve el D-pad, y solo si el dedo empezó en él. Antes cada `pointermove`
      // contaba como un toque nuevo: el pulgar que se corría del D-pad abría el diálogo de lo
      // que hubiera cerca, y un dedo apoyado (que siempre tiembla un poco) lo pasaba volando.
      this.scene.input.on('pointermove', (p) => {
        if (p.isDown && p.id === this.punteroDpad) this.apuntarDpad(p, centro);
      });
      this.scene.input.on('pointerup', (p) => this.pointerArriba(p));
      this.scene.input.on('pointerupoutside', (p) => this.pointerArriba(p));
    }

    hayTactil() {
      return (navigator.maxTouchPoints || 0) > 0 || 'ontouchstart' in window;
    }

    /** Un dedo que se apoya: es del D-pad, del botón A o, en cualquier otra parte, un toque. */
    pointerAbajo(pointer, centro) {
      const distancia = Phaser.Math.Distance.Between(pointer.x, pointer.y, centro.x, centro.y);
      if (distancia < 40) {
        this.punteroDpad = pointer.id;
        this.apuntarDpad(pointer, centro);
        return;
      }
      const centroA = { x: AG.CFG.VIEW_W - 52, y: AG.CFG.VIEW_H - 46 };
      if (Phaser.Math.Distance.Between(pointer.x, pointer.y, centroA.x, centroA.y) < 34) {
        this.punteroA = pointer.id;
        this.botonA = true;
        this.botonAPulsado = true;
        return;
      }
      // Con los controles a la vista, la acción es solo del botón A: tocar el resto de la
      // pantalla no hace nada. Ocultos (diálogo, polaroid), cualquier toque avanza.
      if (!this.controlesVisibles()) this.toqueLibre = true;
    }

    /** El eje según dónde está el dedo del D-pad; si se corre un poco afuera, sigue mandando. */
    apuntarDpad(pointer, centro) {
      const dx = pointer.x - centro.x;
      const dy = pointer.y - centro.y;
      if (Math.abs(dx) < 6 && Math.abs(dy) < 6) {
        this.ejeTactil = { x: 0, y: 0 };
        return;
      }
      // Ocho sectores: los diagonales se toman cuando ningún eje manda con claridad.
      const ejeX = Math.abs(dx) > Math.abs(dy) * 0.45 ? Math.sign(dx) : 0;
      const ejeY = Math.abs(dy) > Math.abs(dx) * 0.45 ? Math.sign(dy) : 0;
      this.ejeTactil = { x: ejeX, y: ejeY };
    }

    pointerArriba(pointer) {
      if (pointer.id === this.punteroDpad) {
        this.punteroDpad = null;
        this.ejeTactil = { x: 0, y: 0 };
      }
      if (pointer.id === this.punteroA) {
        this.punteroA = null;
        this.botonA = false;
      }
    }

    /**
     * Esconde los controles mientras `motivo` (el diálogo, un recuerdo) esté en pantalla; vuelven
     * solo cuando ya nadie los esconde. Con un simple mostrar/ocultar, el diálogo que terminaba
     * con la foto todavía abierta los volvía a pintar encima de ella.
     */
    ocultarControles(motivo, ocultar = true) {
      if (ocultar) this.ocultosPor.add(motivo);
      else this.ocultosPor.delete(motivo);
      const visible = this.ocultosPor.size === 0;
      this.controles.forEach((control) => control.setVisible(visible));
      if (this.zonaDpad) this.zonaDpad.setVisible(visible);
      if (!visible) this.soltarTodo();
    }

    controlesVisibles() {
      return Boolean(this.zonaDpad && this.zonaDpad.visible);
    }

    soltarTodo() {
      this.ejeTactil = { x: 0, y: 0 };
      this.botonA = false;
      this.punteroDpad = null;
      this.punteroA = null;
    }

    /** Dirección de movimiento en 8 sentidos, ya combinando teclado y táctil. */
    direccion() {
      const t = this.teclas;
      let x = 0;
      let y = 0;
      if (t.izquierda.isDown || t.a.isDown) x -= 1;
      if (t.derecha.isDown || t.d.isDown) x += 1;
      if (t.arriba.isDown || t.w.isDown) y -= 1;
      if (t.abajo.isDown || t.s.isDown) y += 1;
      if (!x && !y) {
        x = this.ejeTactil.x;
        y = this.ejeTactil.y;
      }
      return { x, y };
    }

    /**
     * La dirección solo en el instante en que cambia, para moverse por un menú: leída en cada
     * frame, una flecha sostenida hacía volar el cursor (y la elección del diálogo).
     */
    pulsoDireccion() {
      const ahora = performance.now();
      const dir = this.direccion();
      // Si hacía rato que nadie preguntaba (un menú que recién se abre), lo que ya venía
      // apretado no cuenta como pulso: hay que soltar y volver a apretar.
      const antes = ahora - (this.ultimoPulso || 0) > 250 ? dir : this.direccionAnterior;
      this.direccionAnterior = dir;
      this.ultimoPulso = ahora;
      return dir.x === antes.x && dir.y === antes.y ? { x: 0, y: 0 } : dir;
    }

    /**
     * Descarta los toques durante unos ms: el toque que abrió o cerró un recuerdo no debe
     * valer también como acción para quien recién retomó el control (el diálogo lo
     * saltaría, o el álbum reabriría la foto recién cerrada).
     */
    silenciarToques(ms = 160) {
      this.silencioHasta = Math.max(this.silencioHasta, performance.now() + ms);
      this.toqueLibre = false;
      this.botonAPulsado = false;
    }

    /** Acción: verdadero solo en el instante en que se presiona. */
    accion() {
      const tecla = Phaser.Input.Keyboard.JustDown(this.teclas.accion) ||
        Phaser.Input.Keyboard.JustDown(this.teclas.accion2);
      let tactil = this.botonAPulsado || this.toqueLibre;
      this.botonAPulsado = false;
      this.toqueLibre = false;
      if (tactil && performance.now() < this.silencioHasta) tactil = false;
      return Boolean(tecla || tactil);
    }

    pausa() {
      return Phaser.Input.Keyboard.JustDown(this.teclas.pausa);
    }

    actualizar() {
      return undefined;
    }

    destruir() {
      this.controles.forEach((c_) => c_.destroy());
      this.controles = [];
    }
  };
})();
