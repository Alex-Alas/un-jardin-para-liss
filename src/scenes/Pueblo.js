window.AG = window.AG || {};

AG.Pueblo = class Pueblo extends AG.Mundo {
  constructor() {
    super({
      clave: 'Pueblo',
      mapa: 'pueblo',
      musica: 'pueblo',
      intro: 'casa.salir',
      petalos: 2
    });
  }

  alUsar(objeto, clave) {
    if (objeto.nombre === 'sofi') {
      if (!AG.Guardado.tieneFlor(2)) return 'pueblo.sofi.saludo';
      if (!AG.Guardado.datos.visto['petalos2.listo']) return 'pueblo.sofi.pista';
      return 'pueblo.sofi.gracias';
    }
    if (objeto.nombre === 'beto') {
      return AG.Guardado.visto('beto.saludo') ? 'pueblo.beto.chisme' : 'pueblo.beto.saludo';
    }
    return clave;
  }

  antesDePuerta(puerta) {
    if (puerta.a === 'Colina' && !AG.Guardado.tieneFlor(3)) {
      this.dialogo.abrir('pueblo.colina.bloqueada');
      return false;
    }
    return true;
  }
};
