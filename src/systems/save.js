window.AG = window.AG || {};

(function () {
  const VACIO = () => ({
    flores: 0,
    recuerdos: [],
    escena: 'Casa',
    pos: null,
    charlas: {},
    terminado: false,
    visto: {}
  });

  AG.Guardado = {
    datos: VACIO(),

    cargar() {
      try {
        const crudo = window.localStorage.getItem(AG.CFG.SAVE_KEY);
        if (crudo) {
          this.datos = Object.assign(VACIO(), JSON.parse(crudo));
          return this.datos;
        }
      } catch (error) {
        console.warn('[Guardado] No se pudo leer (¿modo privado?):', error.message);
      }
      this.datos = VACIO();
      return this.datos;
    },

    guardar() {
      try {
        window.localStorage.setItem(AG.CFG.SAVE_KEY, JSON.stringify(this.datos));
        return true;
      } catch (error) {
        console.warn('[Guardado] No se pudo escribir:', error.message);
        return false;
      }
    },

    reiniciar() {
      this.datos = VACIO();
      this.guardar();
    },

    flor() {
      this.datos.flores = Math.min(3, this.datos.flores + 1);
      this.guardar();
      return this.datos.flores;
    },

    tieneFlor(n) {
      return this.datos.flores >= n;
    },

    recuerdo(id) {
      if (this.datos.recuerdos.indexOf(id) === -1) {
        this.datos.recuerdos.push(id);
        this.guardar();
      }
      return this.datos.recuerdos.length;
    },

    tieneRecuerdo(id) {
      return this.datos.recuerdos.indexOf(id) !== -1;
    },

    charla(id) {
      this.datos.charlas[id] = (this.datos.charlas[id] || 0) + 1;
      this.guardar();
      return this.datos.charlas[id];
    },

    marcar(clave) {
      this.datos.visto[clave] = true;
      this.guardar();
    },

    visto(clave) {
      const nuevo = !this.datos.visto[clave];
      this.datos.visto[clave] = true;
      return nuevo;
    },

    registrarPos(escena, x, y) {
      this.datos.escena = escena;
      this.datos.pos = { x, y };
      this.guardar();
    }
  };
})();
