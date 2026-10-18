window.AG = window.AG || {};

(function () {
  const c = (v) => AG.UI.color(v);

  // La grilla del álbum: 3 × 2 tarjetas de 140 × 100. Son anchas para que el título vaya a tamaño
  // completo: la fuente achicada (0.75) se deformaba y no se leía.
  const GRILLA = { x: 20, y: 40, pasoX: 150, pasoY: 106, ancho: 140, alto: 100 };
  const celda = (i) => ({
    x: GRILLA.x + (i % 3) * GRILLA.pasoX,
    y: GRILLA.y + Math.floor(i / 3) * GRILLA.pasoY
  });

  AG.Recuerdos = class Recuerdos {
    constructor(scene) {
      this.scene = scene;
      this.abierto = false;
      this.esAlbum = false;
      this.id = null;
      this.alCerrar = null;
      this.cursor = 0;
      this.objetos = [];
      this.modo = null;
      // Si la escena se va con un polaroid abierto, la foto de la capa HTML no tiene que quedar.
      this.scene.events.on('shutdown', () => AG.Fotos.ocultar());
    }

    activo() {
      return this.abierto;
    }

    limpiar() {
      this.objetos.forEach((o) => o.destroy());
      this.objetos = [];
      AG.Fotos.ocultar();
    }

    abrir(id, opciones = {}) {
      const recuerdo = AG.recuerdoPorId(id);
      if (!recuerdo) return;
      this.id = id;
      this.alCerrar = opciones.alCerrar || null;
      AG.Guardado.recuerdo(id);
      if (this.scene.alVerRecuerdo) this.scene.alVerRecuerdo(id);
      this.abierto = true;
      this.esAlbum = false;
      this.modo = 'polaroid';
      this.silenciarToques();

      const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
      const velo = this.scene.add
        .rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.negro), 0.82)
        .setOrigin(0)
        .setDepth(800)
        .setScrollFactor(0);
      this.objetos.push(velo);

      const marco = this.scene.add
        .rectangle(24, 19, 208, 232, c(COLORES.crema), 1)
        .setOrigin(0)
        .setDepth(801)
        .setScrollFactor(0);
      this.objetos.push(marco);

      const fotoX = 40;
      const fotoY = 31;
      const fotoAncho = 176;
      const fotoAlto = 168;
      // El respaldo oscuro se ve mientras la foto carga, y queda si todavía no hay foto.
      this.objetos.push(
        this.scene.add
          .rectangle(fotoX, fotoY, fotoAncho, fotoAlto, c(COLORES.grisOscuro), 1)
          .setOrigin(0)
          .setDepth(802)
          .setScrollFactor(0)
      );
      if (AG.hayFoto(id)) {
        // La foto va en la capa HTML: adentro del canvas de 480 × 270 saldría pixelada.
        AG.Fotos.mostrar([{ id, x: fotoX, y: fotoY, ancho: fotoAncho, alto: fotoAlto }]);
      } else {
        this.objetos.push(
          AG.UI.texto(this.scene, fotoX + fotoAncho / 2, fotoY + 74, 'foto pendiente', {
            color: COLORES.crema
          })
            .setOrigin(0.5)
            .setDepth(803)
            .setScrollFactor(0)
        );
        this.objetos.push(
          AG.UI.texto(this.scene, fotoX + fotoAncho / 2, fotoY + 92, `assets/fotos/recuerdo_${id}.jpg`, {
            color: COLORES.gris
          })
            .setOrigin(0.5)
            .setDepth(803)
            .setScrollFactor(0)
        );
      }

      // Título y pie se apilan bajo la foto, partidos para no salirse del marco: con un título
      // de dos renglones el pie baja, en vez de pisarlo.
      const { POLAROID } = AG.CFG;
      let y = fotoY + fotoAlto + 8;
      [
        [recuerdo.titulo, COLORES.tinta],
        [recuerdo.pie, COLORES.marron]
      ].forEach(([cadena, color]) => {
        const renglones = AG.UI.envolver(cadena, POLAROID.LETRAS_MARCO);
        this.objetos.push(
          this.renglones(AG.UI.texto(this.scene, 36, y, renglones.join('\n'), { color }))
            .setDepth(803)
            .setScrollFactor(0)
        );
        y += renglones.length * 10 + 4;
      });

      const lineas = AG.UI.envolver(recuerdo.mensaje, POLAROID.LETRAS_MENSAJE);
      this.objetos.push(
        this.scene.add
          .rectangle(248, 60, 216, 140, c(COLORES.crema), 0.12)
          .setOrigin(0)
          .setDepth(801)
          .setScrollFactor(0)
      );
      this.objetos.push(
        this.scene.add
          .rectangle(248, 60, 216, 140, 0)
          .setOrigin(0)
          .setStrokeStyle(2, c(COLORES.crema), 0.6)
          .setDepth(801)
          .setScrollFactor(0)
      );
      this.objetos.push(
        this.renglones(AG.UI.texto(this.scene, 260, 76, lineas.join('\n'), { color: COLORES.blanco }))
          .setDepth(802)
          .setScrollFactor(0)
      );
      this.objetos.push(
        AG.UI.texto(this.scene, 260, 176, '— Alex', { color: COLORES.amarillo })
          .setDepth(802)
          .setScrollFactor(0)
      );
      this.objetos.push(
        AG.UI.texto(this.scene, 260, 232, 'A o toca para cerrar', { color: COLORES.gris })
          .setDepth(802)
          .setScrollFactor(0)
      );

      AG.Musica && AG.Musica.sfx('recuerdo');
      this.escucharToque();
    }

    /** Dos píxeles entre renglones: la fuente mide 8 y sin aire las líneas se pegan. */
    renglones(texto) {
      if (texto.setLineSpacing) texto.setLineSpacing(2);
      return texto;
    }

    /** El toque que abrió/cerró un recuerdo no debe ser leído como una acción nueva. */
    silenciarToques() {
      const entrada = this.scene.entrada;
      if (entrada && entrada.silenciarToques) entrada.silenciarToques();
    }

    /** Cerrar el polaroid tocando en cualquier lado (celular). */
    escucharToque() {
      this.quitarToque();
      // Si el mismo toque que abrió la foto se entrega en este dispatch, se ignora:
      // sin este filtro la foto se cerraría sola apenas se abre.
      this.abrioEn = performance.now();
      this.cierreTactil = () => {
        if (performance.now() - this.abrioEn < 150) return;
        this.cerrar();
      };
      this.scene.input.on('pointerdown', this.cierreTactil);
    }

    quitarToque() {
      if (this.cierreTactil) {
        this.scene.input.off('pointerdown', this.cierreTactil);
        this.cierreTactil = null;
      }
    }

    abrirAlbum(opciones = {}) {
      const abiertos = AG.RECUERDOS.filter((r) => AG.Guardado.tieneRecuerdo(r.id));
      this.alCerrar = opciones.alCerrar || null;
      this.abierto = true;
      this.esAlbum = true;
      this.modo = 'album';
      this.cursor = 0;
      this.silenciarToques();

      const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
      this.objetos.push(
        this.scene.add
          .rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.negro), 0.88)
          .setOrigin(0)
          .setDepth(800)
          .setScrollFactor(0)
      );
      this.objetos.push(
        AG.UI.texto(this.scene, VIEW_W / 2, 10, 'NUESTROS RECUERDOS', { color: COLORES.amarillo })
          .setOrigin(0.5, 0)
          .setDepth(801)
          .setScrollFactor(0)
      );
      this.objetos.push(
        AG.UI.texto(this.scene, VIEW_W / 2, 24, `${abiertos.length} de ${AG.RECUERDOS.length}`, {
          color: COLORES.crema
        })
          .setOrigin(0.5, 0)
          .setDepth(801)
          .setScrollFactor(0)
      );

      if (!abiertos.length) {
        this.objetos.push(
          AG.UI.texto(this.scene, VIEW_W / 2, VIEW_H / 2, 'Todavía no hay fotos aquí.\nVe a caminar por el pueblo.', {
            color: COLORES.crema
          })
            .setOrigin(0.5)
            .setDepth(801)
            .setScrollFactor(0)
        );
        return;
      }

      const capas = [];
      const { POLAROID } = AG.CFG;
      abiertos.forEach((recuerdo, i) => {
        const { x, y } = celda(i);
        const marco = this.scene.add
          .rectangle(x, y, GRILLA.ancho, GRILLA.alto, c(COLORES.crema), 1)
          .setOrigin(0)
          .setDepth(801)
          .setScrollFactor(0);
        marco.id = recuerdo.id;
        marco.setInteractive({ useHandCursor: true });
        marco.on('pointerdown', () => this.abrirDesdeAlbum(recuerdo.id));
        this.objetos.push(marco);
        const fotoAncho = GRILLA.ancho - 12;
        if (AG.hayFoto(recuerdo.id)) {
          capas.push({ id: recuerdo.id, x: x + 6, y: y + 6, ancho: fotoAncho, alto: 68 });
        } else {
          this.objetos.push(
            this.scene.add
              .rectangle(x + 6, y + 6, fotoAncho, 68, c(COLORES.grisOscuro), 1)
              .setOrigin(0)
              .setDepth(802)
              .setScrollFactor(0)
          );
        }
        // Hasta dos renglones de 8 px bajo la foto (y+78 a y+96); si no entra, se corta con "…".
        const lineas = AG.UI.envolver(recuerdo.titulo, POLAROID.LETRAS_ALBUM);
        const visibles = lineas.slice(0, POLAROID.RENGLONES_ALBUM);
        if (lineas.length > visibles.length) visibles[visibles.length - 1] += '…';
        this.objetos.push(
          this.renglones(AG.UI.texto(this.scene, x + 6, y + 78, visibles.join('\n'), { color: COLORES.tinta }))
            .setDepth(802)
            .setScrollFactor(0)
        );
      });
      // Las fotos del álbum van juntas a la capa HTML, que las pega encima del canvas.
      AG.Fotos.mostrar(capas);

      const cerrar = AG.UI.texto(this.scene, VIEW_W - 14, 10, 'cerrar', { color: COLORES.gris })
        .setOrigin(1, 0)
        .setDepth(801)
        .setScrollFactor(0)
        .setInteractive({ useHandCursor: true });
      cerrar.on('pointerdown', () => this.cerrar());
      this.objetos.push(cerrar);

      this.cursorCorazon = AG.UI.corazon(this.scene, GRILLA.x, GRILLA.y, 1).setDepth(803).setScrollFactor(0);
      this.objetos.push(this.cursorCorazon);
      this.objetos.push(
        AG.UI.texto(this.scene, VIEW_W / 2, VIEW_H - 12, 'A abre · ESC cierra', { color: COLORES.gris })
          .setOrigin(0.5)
          .setDepth(801)
          .setScrollFactor(0)
      );
      this.moverCursor(0, abiertos);
    }

    abrirDesdeAlbum(id) {
      const alCerrar = this.alCerrar;
      this.limpiar();
      this.abierto = false;
      AG.Musica.sfx('recuerdo');
      this.abrir(id, { alCerrar: () => this.abrirAlbum({ alCerrar }) });
    }

    moverCursor(paso, abiertos) {
      const lista = abiertos || AG.RECUERDOS.filter((r) => AG.Guardado.tieneRecuerdo(r.id));
      if (!lista.length) return;
      this.cursor = (this.cursor + paso + lista.length) % lista.length;
      const { x, y } = celda(this.cursor);
      this.cursorCorazon.setPosition(x - 4, y + 2);
      AG.Musica && AG.Musica.sfx('blip');
    }

    cerrar() {
      this.quitarToque();
      this.silenciarToques();
      this.abierto = false;
      this.limpiar();
      const cb = this.alCerrar;
      this.alCerrar = null;
      if (cb) cb();
    }

    actualizar() {
      if (!this.abierto) return;
      const entrada = this.scene.entrada;
      if (!entrada) return;
      const accion = entrada.accion();
      if (this.esAlbum && this.objetos.length) {
        const dir = entrada.pulsoDireccion();
        if (dir.x < 0 || dir.y < 0) this.moverCursor(-1);
        if (dir.x > 0 || dir.y > 0) this.moverCursor(1);
        if (accion) {
          const abiertos = AG.RECUERDOS.filter((r) => AG.Guardado.tieneRecuerdo(r.id));
          const elegido = abiertos[this.cursor];
          if (elegido) {
            const alCerrar = this.alCerrar;
            this.limpiar();
            this.abierto = false;
            this.abrir(elegido.id, { alCerrar: () => this.abrirAlbum({ alCerrar }) });
          }
          return;
        }
      }
      if (accion || entrada.pausa()) this.cerrar();
    }
  };
})();
