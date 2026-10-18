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
    pie: 'Tan preciosa con tu overol :>',
    mensaje: 'Tu estilazo siempre hace q nuestras fotos juntos brillen.',
    foto: 'assets/fotos/recuerdo_r1.jpg'
  },
  {
    id: 'r2',
    titulo: 'Nuestra plantita de amor',
    pie: 'Crecimos tanto ese día',
    mensaje: 'Desde ese día siento que hemos crecido tantísimo juntos y siento que nuestro compromiso ha tomado más fuerza.',
    foto: 'assets/fotos/recuerdo_r2.jpg'
  },
  {
    id: 'r3',
    titulo: 'Entre las luces',
    pie: 'Tú siempre brillas más',
    mensaje: 'Un bello recuerdo de una salida juntos inolvidable, con tu risa siendo siempre la luz más brillante q acompaña a la mía <3',
    foto: 'assets/fotos/recuerdo_r3.jpg'
  },
  {
    id: 'r4',
    titulo: 'Más sonrisitas',
    pie: 'Más amorsss',
    mensaje: 'Otro día que recuerdo con mucha felicidad y cariño de nosotros compartiendo una bella noche nuestro bello amor.',
    foto: 'assets/fotos/recuerdo_r4.jpg'
  },
  {
    id: 'r5',
    titulo: 'En mi pecho',
    pie: 'Lo más cerca de mí <3',
    mensaje: 'Siempre me encanta tenerte cerca mío, pero esta posición es mi favorita pq es cuando más cerca te siento de mí.',
    foto: 'assets/fotos/recuerdo_r5.jpg'
  },
  {
    id: 'r6',
    titulo: 'Bajo las flores',
    pie: 'Besando la flor más bella',
    mensaje: 'Mil jardines llenos de flores he visto y aun así sólo quiero contemplar la flor más bella que es tu ser completo y el amor q compartimos.',
    foto: 'assets/fotos/recuerdo_r6.jpg'
  }
];

AG.recuerdoPorId = function (id) {
  return AG.RECUERDOS.filter((r) => r.id === id)[0] || null;
};
