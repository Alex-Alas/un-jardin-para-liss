window.AG = window.AG || {};

(function () {
  const c = (v) => AG.UI.color(v);

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
    }

    activo() {
      return this.abierto;
    }

    limpiar() {
      this.objetos.forEach((o) => o.destroy());
      this.objetos = [];
    }

    abrir(id, opciones = {}) {
      const recuerdo = AG.recuerdoPorId(id);
      if (!recuerdo) return;
      this.id = id;
      this.alCerrar = opciones.alCerrar || null;
      AG.Guardado.recuerdo(id);
      this.abierto = true;
      this.esAlbum = false;
      this.modo = 'polaroid';

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
      if (AG.hayFoto(id)) {
        const clave = `foto_${id}`;
        this.cargarFoto(clave, recuerdo, () => {
          const imagen = this.scene.add
            .image(fotoX, fotoY, clave)
            .setOrigin(0)
            .setDepth(802)
            .setScrollFactor(0);
          const escala = Math.max(fotoAncho / imagen.width, 168 / imagen.height);
          imagen.setScale(escala);
          imagen.setCrop(0, 0, fotoAncho / escala, 168 / escala);
          this.objetos.push(imagen);
        });
      } else {
        this.objetos.push(
          this.scene.add
            .rectangle(fotoX, fotoY, fotoAncho, 168, c(COLORES.grisOscuro), 1)
            .setOrigin(0)
            .setDepth(802)
            .setScrollFactor(0)
        );
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

      this.objetos.push(
        AG.UI.texto(this.scene, 36, 208, recuerdo.titulo, { color: COLORES.tinta })
          .setDepth(803)
          .setScrollFactor(0)
      );
      this.objetos.push(
        AG.UI.texto(this.scene, 36, 224, recuerdo.pie, { color: COLORES.marron })
          .setDepth(803)
          .setScrollFactor(0)
      );

      const lineas = AG.UI.envolver(recuerdo.mensaje, 26);
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
        AG.UI.texto(this.scene, 260, 76, lineas.join('\n'), { color: COLORES.blanco })
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
    }

    abrirAlbum(opciones = {}) {
      const abiertos = AG.RECUERDOS.filter((r) => AG.Guardado.tieneRecuerdo(r.id));
      this.alCerrar = opciones.alCerrar || null;
      this.abierto = true;
      this.esAlbum = true;
      this.modo = 'album';
      this.cursor = 0;

      const { VIEW_W, VIEW_H, COLORES } = AG.CFG;
      this.objetos.push(
        this.scene.add
          .rectangle(0, 0, VIEW_W, VIEW_H, c(COLORES.negro), 0.88)
          .setOrigin(0)
          .setDepth(800)
          .setScrollFactor(0)
      );
      this.objetos.push(
        AG.UI.texto(this.scene, VIEW_W / 2, 16, 'NUESTROS RECUERDOS', { color: COLORES.amarillo })
          .setOrigin(0.5, 0)
          .setDepth(801)
          .setScrollFactor(0)
      );
      this.objetos.push(
        AG.UI.texto(this.scene, VIEW_W / 2, 32, `${abiertos.length} de ${AG.RECUERDOS.length}`, {
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

      abiertos.forEach((recuerdo, i) => {
        const columna = i % 3;
        const fila = Math.floor(i / 3);
        const x = 92 + columna * 106;
        const y = 60 + fila * 96;
        const marco = this.scene.add
          .rectangle(x, y, 92, 84, c(COLORES.crema), 1)
          .setOrigin(0)
          .setDepth(801)
          .setScrollFactor(0);
        marco.id = recuerdo.id;
        this.objetos.push(marco);
        if (AG.hayFoto(recuerdo.id)) {
          const clave = `foto_${recuerdo.id}`;
          this.cargarFoto(clave, recuerdo, () => {
            const imagen = this.scene.add.image(x + 6, y + 6, clave).setOrigin(0).setDepth(802).setScrollFactor(0);
            const escala = Math.max(80 / imagen.width, 60 / imagen.height);
            imagen.setScale(escala);
            imagen.setCrop(0, 0, 80 / escala, 60 / escala);
            this.objetos.push(imagen);
          });
        } else {
          this.objetos.push(
            this.scene.add
              .rectangle(x + 6, y + 6, 80, 60, c(COLORES.grisOscuro), 1)
              .setOrigin(0)
              .setDepth(802)
              .setScrollFactor(0)
          );
        }
        this.objetos.push(
          AG.UI.texto(this.scene, x + 6, y + 70, recuerdo.titulo.slice(0, 12), { color: COLORES.tinta, escala: 0.8 })
            .setDepth(802)
            .setScrollFactor(0)
        );
      });

      this.cursorCorazon = AG.UI.corazon(this.scene, 92, 60, 1).setDepth(803).setScrollFactor(0);
      this.objetos.push(this.cursorCorazon);
      this.objetos.push(
        AG.UI.texto(this.scene, VIEW_W / 2, VIEW_H - 18, 'A abre · ESC cierra', { color: COLORES.gris })
          .setOrigin(0.5)
          .setDepth(801)
          .setScrollFactor(0)
      );
      this.moverCursor(0, abiertos);
    }

    moverCursor(paso, abiertos) {
      const lista = abiertos || AG.RECUERDOS.filter((r) => AG.Guardado.tieneRecuerdo(r.id));
      if (!lista.length) return;
      this.cursor = (this.cursor + paso + lista.length) % lista.length;
      const columna = this.cursor % 3;
      const fila = Math.floor(this.cursor / 3);
      this.cursorCorazon.setPosition(88 + columna * 106, 62 + fila * 96);
      AG.Musica && AG.Musica.sfx('blip');
    }

    cargarFoto(clave, recuerdo, alListo) {
      if (this.scene.textures.exists(clave)) {
        alListo();
        return;
      }
      this.scene.load.image(clave, recuerdo.foto);
      this.scene.load.once(`filecomplete-image-${clave}`, () => alListo());
      this.scene.load.once(`loaderror`, () => console.warn('[Recuerdos] Falta la foto:', recuerdo.foto));
      this.scene.load.start();
    }

    cerrar() {
      this.abierto = false;
      this.limpiar();
      const cb = this.alCerrar;
      this.alCerrar = null;
      if (cb) cb();
    }

    actualizar() {
      if (!this.abierto) return;
      const accion = this.scene.entrada.accion();
      if (this.esAlbum && this.objetos.length) {
        const dir = this.scene.entrada.direccion();
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
      if (accion || this.scene.entrada.pausa()) this.cerrar();
    }
  };
})();
