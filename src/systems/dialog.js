window.AG = window.AG || {};

(function () {
  const c = (v) => AG.UI.color(v);

  AG.Dialogo = class Dialogo {
    constructor(scene, entrada) {
      this.scene = scene;
      this.entrada = entrada;
      this.activa = false;
      this.lineas = [];
      this.indice = 0;
      this.paginas = [];
      this.pagina = 0;
      this.reveladas = 0;
      this.pausado = false;
      this.ultimaEleccion = 0;
      this.alCerrar = null;
      this.eleccionActiva = null;
      this.indiceEleccion = 0;
      this.crear();
    }

    crear() {
      const { VIEW_W, VIEW_H, COLORES, FUENTE_CHICA } = AG.CFG;
      this.ancho = 468;
      this.alto = 94;
      this.x = (VIEW_W - this.ancho) / 2;
      this.y = VIEW_H - this.alto - 6;
      const escena = this.scene;

      this.grupo = [];
      this.grupo.push(
        escena.add
          .rectangle(this.x, this.y, this.ancho, this.alto, c(COLORES.tinta), 0.95)
          .setOrigin(0)
          .setDepth(700)
          .setScrollFactor(0)
      );
      this.grupo.push(
        escena.add
          .rectangle(this.x, this.y, this.ancho, this.alto, 0)
          .setOrigin(0)
          .setStrokeStyle(2, c(COLORES.blanco), 1)
          .setDepth(701)
          .setScrollFactor(0)
      );

      // Placa de fondo: sostiene la inicial de quien todavía no tiene retrato dibujado.
      this.placa = escena.add
        .rectangle(this.x + 8, this.y + 8, 84, 84, c(COLORES.tintaSuave))
        .setOrigin(0)
        .setDepth(702)
        .setScrollFactor(0);
      this.retrato = AG.tieneFrame(escena, 'retrato_liss_normal')
        ? escena.add
            .image(this.x + 8, this.y + 8, 'arte', 'retrato_liss_normal')
            .setOrigin(0)
            .setScale(1.75)
            .setDepth(703)
            .setScrollFactor(0)
        : null;
      this.retratoInicial = AG.UI.texto(escena, this.x + 32, this.y + 52, 'L', {
        color: COLORES.amarillo,
        escala: 4
      })
        .setOrigin(0.5)
        .setDepth(702)
        .setScrollFactor(0);

      this.nombre = AG.UI.texto(escena, this.x + 110, this.y + 12, '', { color: COLORES.amarillo })
        .setDepth(702)
        .setScrollFactor(0);
      this.texto = AG.UI.texto(escena, this.x + 110, this.y + 30, '', { color: COLORES.blanco })
        .setDepth(702)
        .setScrollFactor(0);
      if (this.texto.setLineSpacing) this.texto.setLineSpacing(3);
      this.indicador = AG.UI.corazon(escena, this.x + this.ancho - 16, this.y + this.alto - 14, 1)
        .setDepth(702)
        .setScrollFactor(0);

      this.opciones = [0, 1].map((i) =>
        AG.UI.texto(escena, this.x + 130, this.y + 40 + i * 18, '', { color: COLORES.blanco })
          .setDepth(703)
          .setScrollFactor(0)
      );

      this.fuenteChica = FUENTE_CHICA;
      this.ocultar();
      this.scene.tweens.add({
        targets: this.indicador,
        alpha: { from: 1, to: 0 },
        duration: 500,
        yoyo: true,
        repeat: -1
      });
    }

    ocultar() {
      this.grupo.forEach((g) => g.setVisible(false));
      this.placa.setVisible(false);
      if (this.retrato) this.retrato.setVisible(false);
      this.retratoInicial.setVisible(false);
      this.nombre.setVisible(false);
      this.texto.setVisible(false);
      this.indicador.setVisible(false);
      this.opciones.forEach((o) => o.setVisible(false));
    }

    mostrarUI(conRetrato) {
      this.grupo.forEach((g) => g.setVisible(true));
      this.nombre.setVisible(true);
      this.texto.setVisible(true);
      this.indicador.setVisible(true);
      const conImagen = Boolean(conRetrato && this.retrato && this.hayRetrato);
      this.placa.setVisible(Boolean(conRetrato) && !conImagen);
      if (this.retrato) this.retrato.setVisible(conImagen);
      this.retratoInicial.setVisible(Boolean(conRetrato) && !conImagen);
    }

    activo() {
      return this.activa;
    }

    /** Abre un diálogo del guion: admite variantes (array de arrays) por número de charla. */
    abrir(clave, opciones = {}) {
      const dato = AG.DIALOGOS[clave];
      if (!dato) {
        console.warn('[Dialogo] No existe el diálogo:', clave);
        return false;
      }
      let lineas = dato;
      if (Array.isArray(dato) && Array.isArray(dato[0])) {
        const veces = opciones.charla === undefined ? 1 : opciones.charla;
        lineas = dato[Math.min(veces - 1, dato.length - 1)];
      }
      this.mostrarLineas(lineas, opciones);
      return true;
    }

    mostrarLineas(lineas, opciones = {}) {
      if (this.entrada && this.entrada.mostrarControles) this.entrada.mostrarControles(false);
      this.lineas = lineas.slice();
      this.indice = 0;
      this.activa = true;
      this.pausado = false;
      this.alCerrar = opciones.alCerrar || null;
      this.limpiar();
      this.pintarLinea();
    }

    limpiar() {
      this.eleccionActiva = null;
      this.opciones.forEach((o) => o.setVisible(false));
    }

    pintarLinea() {
      const linea = this.lineas[this.indice];
      if (!linea) {
        this.cerrar();
        return;
      }
      const esNarracion = Boolean(linea.narracion);
      const contenido = linea.narracion || linea.texto || '';
      const quien = linea.quien || null;
      const personaje = quien ? AG.PERSONAJES[quien] : null;

      if (personaje) {
        this.nombre.setText(personaje.nombre);
        this.nombre.setVisible(true);
        // Mientras un personaje no tenga retrato en el atlas, se muestra su inicial.
        const marco = `retrato_${personaje.sprite || quien}_normal`;
        this.hayRetrato = AG.tieneFrame(this.scene, marco);
        if (this.hayRetrato && this.retrato) this.retrato.setFrame(marco);
        this.retratoInicial.setText(personaje.nombre.charAt(0));
      } else {
        this.nombre.setText('');
        this.nombre.setVisible(false);
      }
      this.mostrarUI(Boolean(personaje));
      if (esNarracion) this.nombre.setVisible(false);

      if (linea.eleccion) {
        this.eleccionActiva = linea.eleccion;
        this.indiceEleccion = 0;
        this.texto.setText('');
        this.paginas = [[]];
        this.pagina = 0;
        this.reveladas = 0;
        this.pintarEleccion();
        return;
      }

      const lineas = AG.UI.envolver(contenido, 42);
      this.paginas = AG.UI.paginar(lineas, 3);
      this.pagina = 0;
      this.reveladas = 0;
      this.aplicarAcciones(linea);

      // Las líneas que solo ejecutan algo (dar una flor, abrir un recuerdo) no se esperan.
      if (!contenido.trim() && !linea.eleccion && this.activa) {
        this.siguiente();
        return;
      }
      this.pintarPagina();
    }

    pintarPagina() {
      this.texto.setText((this.paginas[this.pagina] || []).join('\n'));
      this.texto.setVisible(true);
      this.indicador.setVisible(false);
    }

    escribir(delta) {
      const contenido = (this.paginas[this.pagina] || []).join('\n');
      if (this.reveladas >= contenido.length) return;
      const antes = Math.floor(this.reveladas);
      this.reveladas = Math.min(contenido.length, this.reveladas + (delta / 1000) * AG.CFG.TEXTO.VELOCIDAD);
      if (Math.floor(this.reveladas) > antes && Math.floor(this.reveladas) % AG.CFG.TEXTO.BLIP_CADA === 0) {
        AG.Musica && AG.Musica.sfx('blip');
      }
      this.texto.setText(contenido.slice(0, Math.floor(this.reveladas)));
      if (this.reveladas >= contenido.length) this.indicador.setVisible(true);
    }

    completo() {
      const total = (this.paginas[this.pagina] || []).join('\n').length;
      return this.reveladas >= total;
    }

    pintarEleccion() {
      this.opciones.forEach((opcion, i) => {
        const dato = this.eleccionActiva[i];
        if (!dato) {
          opcion.setVisible(false);
          return;
        }
        const marca = i === this.indiceEleccion ? '> ' : '  ';
        opcion.setText(marca + dato.texto);
        opcion.setVisible(true);
      });
    }

    moverEleccion(paso) {
      this.indiceEleccion = (this.indiceEleccion + paso + this.eleccionActiva.length) % this.eleccionActiva.length;
      AG.Musica && AG.Musica.sfx('blip');
      this.pintarEleccion();
    }

    confirmarEleccion() {
      const dato = this.eleccionActiva[this.indiceEleccion];
      this.ultimaEleccion = this.indiceEleccion;
      this.eleccionActiva = null;
      this.opciones.forEach((o) => o.setVisible(false));
      if (dato && dato.efecto) this.ejecutar(dato.efecto);
      AG.Musica && AG.Musica.sfx('corazon');
      this.siguiente();
    }

    aplicarAcciones(linea) {
      if (linea.darFlor) {
        AG.Guardado.flor();
        AG.Musica && AG.Musica.sfx('flor');
        this.mostrarContador();
      }
      if (linea.darRecuerdo && this.scene.recuerdos) {
        this.pausado = true;
        this.scene.recuerdos.abrir(linea.darRecuerdo, { alCerrar: () => this.reanudar() });
      }
      if (linea.verAlbum && this.scene.recuerdos) {
        this.pausado = true;
        this.scene.recuerdos.abrirAlbum({ alCerrar: () => this.reanudar() });
      }
      if (linea.efecto) this.ejecutar(linea.efecto);
      if (linea.musica) AG.Musica && AG.Musica.tocar(linea.musica);
      if (linea.lanzarEscena) {
        const { clave, datos } = linea.lanzarEscena;
        this.activa = false;
        this.ocultar();
        this.scene.time.delayedCall(120, () => this.scene.scene.start(clave, datos));
      }
    }

    ejecutar(efecto) {
      if (efecto === 'latido') AG.FX.latido(this.scene);
      else if (efecto === 'temblor') AG.FX.temblor(this.scene);
      else if (efecto === 'florecer') {
        AG.FX.florecer(this.scene, AG.CFG.VIEW_W / 2, AG.CFG.VIEW_H / 2);
        AG.Musica && AG.Musica.sfx('flor');
      }
    }

    mostrarContador() {
      const { VIEW_W, COLORES } = AG.CFG;
      const flores = AG.Guardado.datos.flores;
      const texto = AG.UI.texto(this.scene, VIEW_W - 12, 10, `x${flores}`, { color: COLORES.amarillo })
        .setOrigin(1, 0)
        .setDepth(720)
        .setScrollFactor(0);
      const icono = AG.UI.corazon(this.scene, VIEW_W - 46, 14, 1.5).setDepth(720).setScrollFactor(0);
      this.scene.tweens.add({
        targets: [texto, icono],
        y: '-=6',
        duration: 700,
        yoyo: true,
        onComplete: () => {
          texto.destroy();
          icono.destroy();
        }
      });
    }

    siguiente() {
      this.pagina += 1;
      if (this.pagina >= this.paginas.length) {
        this.indice += 1;
        this.limpiar();
        if (this.indice >= this.lineas.length) {
          this.cerrar();
          return;
        }
        this.pintarLinea();
        return;
      }
      this.reveladas = 0;
      this.pintarPagina();
      this.texto.setText('');
    }

    reanudar() {
      this.pausado = false;
      if (this.completo()) this.indicador.setVisible(true);
    }

    cerrar() {
      this.activa = false;
      this.ocultar();
      if (this.entrada && this.entrada.mostrarControles) this.entrada.mostrarControles(true);
      const cb = this.alCerrar;
      this.alCerrar = null;
      if (cb) cb();
    }

    actualizar(delta) {
      if (!this.activa || this.pausado) return;
      const accion = this.entrada.accion();

      if (this.eleccionActiva) {
        const dir = this.entrada.direccion();
        if (dir.y < 0) this.moverEleccion(-1);
        if (dir.y > 0) this.moverEleccion(1);
        if (accion) this.confirmarEleccion();
        return;
      }

      if (!this.completo()) {
        this.escribir(delta);
        if (accion) {
          this.reveladas = (this.paginas[this.pagina] || []).join('\n').length;
          this.texto.setText((this.paginas[this.pagina] || []).join('\n'));
          this.indicador.setVisible(true);
        }
        return;
      }

      if (accion) this.siguiente();
    }
  };
})();
