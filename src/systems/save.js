window.AG = window.AG || {};

(function () {
  // Las tres flores, cada una de quien la da. El orden es el de la partida.
  const FLORES = ['beto', 'sofi', 'flora'];

  const VACIO = () => ({
    flores: 0,
    floresDe: [],
    recuerdos: [],
    escena: 'Casa',
    pos: null,
    charlas: {},
    terminado: false,
    visto: {}
  });

  AG.FLORES = FLORES;

  AG.Guardado = {
    datos: VACIO(),

    cargar() {
      try {
        const crudo = window.localStorage.getItem(AG.CFG.SAVE_KEY);
        if (crudo) {
          this.datos = this.migrar(Object.assign(VACIO(), JSON.parse(crudo)));
          return this.datos;
        }
      } catch (error) {
        console.warn('[Guardado] No se pudo leer (¿modo privado?):', error.message);
      }
      this.datos = VACIO();
      return this.datos;
    },

    /**
     * Antes las flores eran un contador y cualquiera daba "la siguiente": así Sofi terminaba
     * dando las tres. Un guardado de entonces no dice de quién era cada una; si la partida ya
     * terminó se le dan las tres, si no, las flores vuelven a empezar (las fotos se quedan).
     */
    migrar(datos) {
      if (!Array.isArray(datos.floresDe) || (datos.flores && !datos.floresDe.length)) {
        datos.floresDe = datos.terminado ? FLORES.slice() : [];
      }
      datos.floresDe = datos.floresDe.filter((id) => FLORES.indexOf(id) !== -1);
      datos.flores = datos.floresDe.length;
      return datos;
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

    /** La flor que da `quien` (beto, sofi o flora). Dos veces la misma no suma. */
    flor(quien) {
      if (FLORES.indexOf(quien) === -1) {
        console.warn('[Guardado] Flor de alguien desconocido:', quien);
        return this.datos.flores;
      }
      if (this.datos.floresDe.indexOf(quien) === -1) this.datos.floresDe.push(quien);
      this.datos.flores = this.datos.floresDe.length;
      this.guardar();
      return this.datos.flores;
    },

    tieneFlorDe(quien) {
      return this.datos.floresDe.indexOf(quien) !== -1;
    },

    tieneTodasLasFlores() {
      return FLORES.every((quien) => this.tieneFlorDe(quien));
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

    /** Dónde guardó Liss, en píxeles del mapa (el punto de sus pies) y en qué escena. */
    registrarPos(escena, px, py) {
      this.datos.escena = escena;
      this.datos.pos = { escena, px, py };
      this.guardar();
    },

    /** La posición guardada, solo si es de esa escena: al cruzar una puerta la escena cambia
     *  y la posición vieja ya no significa nada ahí (antes eso dejaba a Liss en cualquier lado). */
    posEn(escena) {
      const pos = this.datos.pos;
      return pos && pos.escena === escena ? { px: pos.px, py: pos.py } : undefined;
    }
  };
})();
