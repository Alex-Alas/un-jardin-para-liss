window.AG = window.AG || {};

AG.PERSONAJES = {
  liss: { nombre: 'Liss', color: '#f2a8b8', sprite: 'liss' },
  alex: { nombre: 'Alex', color: '#7fc7e8', sprite: 'alex' },
  flora: { nombre: 'Doña Flora', color: '#ffd23f', sprite: 'flora' },
  beto: { nombre: 'Don Beto', color: '#f2802c', sprite: 'beto' },
  sofi: { nombre: 'Sofi', color: '#a8d672', sprite: 'sofi' },
  michi: { nombre: 'Michi', color: '#8b8b9e', sprite: 'michi' }
};

AG.RECUERDOS = [
  {
    id: 'r1',
    titulo: 'Pegaditos bien gonitos',
    pie: 'La primera vez q te tuve tan cómoda cerca de mí',
    mensaje: 'Antes de esta foto yo ya estaba nervioso. Después también :P',
    foto: 'assets/fotos/recuerdo_r1.jpg'
  },
  {
    id: 'r2',
    titulo: 'Tu carita',
    pie: 'Aquí te burlabas de mí',
    mensaje: 'No es la mejor foto que te he tomado, pero es mi favorita.',
    foto: 'assets/fotos/recuerdo_r2.jpg'
  },
  {
    id: 'r3',
    titulo: 'Tu risa',
    pie: 'Esa noche, entre las luces',
    mensaje: 'No nos importó nada. Volvería a esa noche contigo.',
    foto: 'assets/fotos/recuerdo_r3.jpg'
  },
  {
    id: 'r4',
    titulo: 'El lugar de siempre',
    pie: 'Ya nos conocen y todo',
    mensaje: 'Aquí quiero volver contigo mil veces más.',
    foto: 'assets/fotos/recuerdo_r4.jpg'
  },
  {
    id: 'r5',
    titulo: 'Nosotros',
    pie: 'Un día cualquiera, contigo',
    mensaje: 'Los días normales contigo no tienen nada de normales.',
    foto: 'assets/fotos/recuerdo_r5.jpg'
  },
  {
    id: 'r6',
    titulo: 'Bajo las flores',
    pie: 'Un jardín entero para vos',
    mensaje: 'Te beso y se prenden todas las luces.',
    foto: 'assets/fotos/recuerdo_r6.jpg'
  }
];

AG.recuerdoPorId = function (id) {
  return AG.RECUERDOS.filter((r) => r.id === id)[0] || null;
};
