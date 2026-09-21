window.AG = window.AG || {};

(function () {
  const c = (v) => AG.UI.color(v);

  AG.Entrada = class Entrada {
    constructor(scene) {
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
      this.ejeTactil = { x: 0, y: 0 };
      this.controles = [];
      this.crearControles();
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

      [['izquierda', -16, 0], ['derecha', 16, 0], ['arriba', 0, -16], ['abajo', 0, 16]].forEach(([nombre, dx, dy]) => {
        const flecha = this.scene.add
          .rectangle(centro.x + dx, centro.y + dy, 7, 7, c(COLORES.blanco), 0.75)
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
      this.scene.input.on('pointermove', (p) => {
        if (p.isDown) this.pointerAbajo(p, centro);
      });
      this.scene.input.on('pointerup', (p) => this.pointerArriba(p, centro));
      this.scene.input.on('pointerupoutside', () => this.soltarTodo());
    }

    hayTactil() {
      return (navigator.maxTouchPoints || 0) > 0 || 'ontouchstart' in window;
    }

    pointerAbajo(pointer, centro) {
      const distancia = Phaser.Math.Distance.Between(pointer.x, pointer.y, centro.x, centro.y);
      if (distancia < 40) {
        const dx = pointer.x - centro.x;
        const dy = pointer.y - centro.y;
        if (Math.abs(dx) < 6 && Math.abs(dy) < 6) {
          this.ejeTactil = { x: 0, y: 0 };
          return;
        }
        this.ejeTactil =
          Math.abs(dx) > Math.abs(dy) ? { x: Math.sign(dx), y: 0 } : { x: 0, y: Math.sign(dy) };
        return;
      }
      if (pointer.x > AG.CFG.VIEW_W - 96 && pointer.y > AG.CFG.VIEW_H - 96) {
        this.botonA = true;
        this.botonAPulsado = true;
      }
    }

    pointerArriba(pointer, centro) {
      const distancia = Phaser.Math.Distance.Between(pointer.x, pointer.y, centro.x, centro.y);
      if (distancia < 40) this.ejeTactil = { x: 0, y: 0 };
      if (pointer.x > AG.CFG.VIEW_W - 96 && pointer.y > AG.CFG.VIEW_H - 96) this.botonA = false;
    }

    soltarTodo() {
      this.ejeTactil = { x: 0, y: 0 };
      this.botonA = false;
    }

    /** Dirección de movimiento en 4 sentidos, ya combinando teclado y táctil. */
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
      if (x && y) {
        if (Math.abs(x) >= Math.abs(y)) y = 0;
        else x = 0;
      }
      return { x, y };
    }

    /** Acción: verdadero solo en el instante en que se presiona. */
    accion() {
      const tecla = Phaser.Input.Keyboard.JustDown(this.teclas.accion) ||
        Phaser.Input.Keyboard.JustDown(this.teclas.accion2);
      const tactil = this.botonAPulsado;
      this.botonAPulsado = false;
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
