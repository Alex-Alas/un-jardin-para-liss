window.AG = window.AG || {};

AG.Colina = class Colina extends AG.Mundo {
  constructor() {
    super({
      clave: 'Colina',
      mapa: 'colina',
      musica: 'pueblo',
      inicio: { x: 16, y: 17 },
      intro: 'colina.entrada',
      velo: true,
      petalos: 3
    });
  }

  create() {
    super.create();
    if (AG.Guardado.datos.terminado) this.mostrarRamo();
  }

  usarObjeto(objeto) {
    if (objeto.tipo === 'npc' && objeto.letra === '1') {
      this.hablarConAlex();
      return;
    }
    super.usarObjeto(objeto);
  }

  /** El final: una conversación encadenada, sin prisa, hasta los créditos. */
  hablarConAlex() {
    const pasos = [];
    if (!AG.Guardado.datos.visto['colina.alex.1']) pasos.push('colina.alex.1');
    pasos.push('colina.alex.2', 'colina.album', 'colina.mensaje', 'colina.abrazo', 'colina.tarjeta_final');

    AG.Musica.tocar('final');
    const avanzar = (i) => {
      if (i >= pasos.length) {
        AG.Guardado.datos.terminado = true;
        AG.Guardado.guardar();
        AG.FX.fundir(this, () => this.scene.start('Creditos'));
        return;
      }
      const clave = pasos[i];
      this.dialogo.abrir(clave, {
        alCerrar: () => {
          AG.Guardado.marcar(clave);
          if (clave === 'colina.alex.2') this.mostrarRamo();
          avanzar(i + 1);
        }
      });
    };
    avanzar(0);
  }

  mostrarRamo() {
    if (this.ramo) return;
    const { TILE, COLORES } = AG.CFG;
    const x = this.desfase.x + 17 * TILE + 4;
    const y = this.desfase.y + 5 * TILE + TILE;
    if (AG.hayAtlas()) {
      this.ramo = this.add.sprite(x, y, 'arte', 'ramo_0').setOrigin(0.5, 1).setDepth(y);
    } else {
      this.ramo = this.add.rectangle(x, y - 8, 12, 16, AG.UI.color(COLORES.amarillo)).setDepth(y);
    }
    AG.FX.florecer(this, x, y - 10);
  }
};
