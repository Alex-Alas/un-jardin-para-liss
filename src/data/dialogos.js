window.AG = window.AG || {};

AG.DIALOGOS = {
  'sistema.guardado': [
    { narracion: 'Un lugarcito tranquilo. Aquí se guardan las flores y los recuerdos.' },
    { narracion: 'Listo. Todo guardado.' }
  ],

  'casa.despertar': [
    { narracion: 'La cama está tibia todavía.' },
    { narracion: 'Cinco minutos más no le harían daño a nadie.' },
    { narracion: '...pero hoy algo se siente distinto.' }
  ],
  'casa.espejo': [
    { narracion: 'Es el espejo. Ahí está Liss.' },
    { narracion: '(Guapa, como siempre.) — dice una voz que Liss no dijo.' }
  ],
  'casa.calendario': [
    { narracion: 'Septiembre. Un día está marcado con un círculo amarillo.' },
    { narracion: '21. Día de las flores amarillas.' }
  ],
  'casa.escritorio': [
    { narracion: 'En el escritorio hay un polaroid apoyado en el marco de la ventana.' },
    { darRecuerdo: 'r1' }
  ],
  'casa.nota': [
    { narracion: 'Hay una nota doblada en cuatro, con una letra que Liss conoce de memoria.' },
    { narracion: '«Hoy el pueblo entero tiene flores amarillas para ti.»' },
    { narracion: '«Busca tres y ven a la colina. Te espero. — A.»' },
    { efecto: 'latido' }
  ],
  'casa.planta': [
    { narracion: 'La planta de la ventana sigue viva.' },
    { narracion: 'Sobrevive por pura terquedad, igual que su dueña.' }
  ],
  'casa.salir': [
    { narracion: 'Afuera huele a pasto cortado y a pan.' }
  ],

  'pueblo.cartel': [
    { narracion: 'FIESTA DE LAS FLORES AMARILLAS. Hoy.' },
    { narracion: 'Todos los años. Todos los colores... bueno, uno: amarillo.' }
  ],
  'pueblo.buzon': [
    { narracion: 'Es un buzón. No tiene cartas, pero tiene esperanza.' },
    { narracion: '«Si estás leyendo esto, ya casi es la hora. Sube despacio, que la vista es bonita.» — A.' }
  ],
  'pueblo.banco': [
    { narracion: 'En el banco del parque alguien dejó un polaroid con una piedrita encima para que el viento no se lo llevara.' },
    { darRecuerdo: 'r2' }
  ],
  'pueblo.arbol': [
    { narracion: 'En el tronco hay dos iniciales talladas. No las talló nadie hoy: llevan ahí un buen rato.' },
    { darRecuerdo: 'r3' }
  ],
  'pueblo.lampara': [
    { narracion: 'Alguien ató un polaroid al poste de la luz con un hilo amarillo.' },
    { narracion: 'El viento lo hace girar despacio, como si estuviera bailando.' },
    { darRecuerdo: 'r5' }
  ],
  'pueblo.michi': [
    [
      { narracion: 'Michi te mira como si supiera algo. Los gatos siempre saben algo.' },
      { quien: 'michi', texto: '* Miau.' }
    ],
    [
      { narracion: 'Michi maúlla. Suena sospechosamente a "ánimo".' }
    ],
    [
      { narracion: 'Michi se estira. Tú también quisieras estirarte así de tranquila.' }
    ]
  ],

  'pueblo.flora.saludo': [
    { quien: 'flora', texto: '¡Liss! Justo a quien necesitaba.' },
    { quien: 'flora', texto: 'Se me volaron los pétalos del ramo más bonito del año.' },
    { quien: 'flora', texto: '¿Me ayudas a juntarlos antes de que el viento se los lleve?' },
    { lanzarEscena: { clave: 'Petalos', datos: { tipo: 'petalos1', volver: 'Floreria', inicio: { x: 7, y: 10 } } } }
  ],
  'pueblo.flora.post': [
    { quien: 'flora', texto: '¡Bien hecho, mi niña! Este ramo ya tiene dueña.' },
    { quien: 'flora', texto: 'Toma. Y no te la cobro, ni se te ocurra.' },
    { darFlor: 1 }
  ],
  'pueblo.flora.gracias': [
    { quien: 'flora', texto: 'Ese ramo va a quedar hermoso, ya verás.' },
    { quien: 'flora', texto: 'Anda, que alguien te espera arriba.' }
  ],
  'pueblo.flora.espera': [
    { quien: 'flora', texto: '¿Ya juntaste los pétalos? Vuelve cuando tengas las manos llenas.' }
  ],
  'pueblo.floreria.mostrador': [
    { narracion: 'Debajo del mostrador, pegado con cinta adhesiva, hay otro polaroid.' },
    { narracion: 'Doña Flora no dice nada. Doña Flora sonríe.' },
    { darRecuerdo: 'r4' }
  ],
  'pueblo.floreria.estante': [
    { narracion: 'Girasoles, margaritas, un ramo que dice «para alguien especial».' },
    { narracion: 'Está apartado. Tiene el nombre de Liss, y ni siquiera está escrito.' }
  ],

  'pueblo.beto.saludo': [
    { quien: 'beto', texto: 'Ah, tú. Un tal Alex pasó ayer y me dejó pagado lo que quisieras.' },
    { quien: 'beto', texto: 'No le digas que te dije.' },
    { narracion: 'El kiosquero guiña un ojo con toda la discreción de un kiosquero.' }
  ],
  'pueblo.beto.chisme': [
    { quien: 'beto', texto: 'Ese muchacho llevaba semanas preguntando por flores. Semanas.' },
    { quien: 'beto', texto: '«¿Y si no le gustan?» me decía. «¿Y si se le olvida?»' },
    { quien: 'beto', texto: 'Ni se te olvida ni se te va a olvidar. Mírate la cara.' }
  ],

  'pueblo.sofi.saludo': [
    { quien: 'sofi', texto: 'Hola. ¿Tú también vienes por las flores?' },
    { quien: 'sofi', texto: 'Yo ya tengo la mía. Esta es para ti.' },
    { darFlor: 2 },
    { quien: 'sofi', texto: 'Es de mi mamá. Tiene un jardín enorme y le sobran.' },
    { quien: 'sofi', texto: 'En el parque el viento sopla feo.' },
    { quien: 'sofi', texto: 'Si un pétalo se va de lado, ¡corre!' }
  ],
  'pueblo.sofi.pista': [
    { quien: 'sofi', texto: 'Yo te aviso si lo veo venir. Tú corre.' },
    { lanzarEscena: { clave: 'Petalos', datos: { tipo: 'petalos2', volver: 'Pueblo', inicio: { x: 29, y: 21 } } } }
  ],
  'pueblo.sofi.gracias': [
    { quien: 'sofi', texto: '¡Corre a la colina! Y después me cuentas.' }
  ],
  'pueblo.sofi.espera': [
    { quien: 'sofi', texto: '¿Vas a intentarlo? El viento no se cansa nunca.' }
  ],

  'pueblo.colina.bloqueada': [
    { narracion: 'El sendero sube entre flores. Todavía no.' },
    { narracion: 'Tres flores. Eso decía la nota.' }
  ],

  'petalos1.intro': [
    { quien: 'flora', texto: '¡Ahí van! ¡Atrápalos con las manos y con el corazón!' }
  ],
  'petalos1.reintento': [
    { quien: 'flora', texto: 'Ay, se fueron. No importa, el viento siempre presta. ¿Otra vez?' }
  ],
  'petalos1.victoria': [
    { quien: 'flora', texto: '¡Perfecto! Ni una hoja seca, ¿eh? Solo amarillo.' }
  ],

  'petalos2.intro': [
    { quien: 'sofi', texto: '¡Ahí van! ¡Y el viento sopla fuerte, corre!' }
  ],
  'petalos2.victoria': [
    { quien: 'sofi', texto: '¡Lo lograste!' },
    { quien: 'sofi', texto: 'Toma, la tercera. Entre las dos ya son tres.' },
    { darFlor: 3 },
    { narracion: 'El camino a la colina ya está libre, y el cielo se está poniendo naranja.' }
  ],

  'colina.entrada': [
    { narracion: 'Cuesta arriba hace más fresco. Huele a pasto y a algo dulce.' },
    { narracion: 'Alguien subió antes que tú.' }
  ],
  'colina.alex.1': [
    { quien: 'alex', texto: 'Llegaste.' },
    { quien: 'alex', texto: 'No sabes cuánto me alegra verte llegar.' }
  ],
  'colina.alex.2': [
    { quien: 'alex', texto: '¿Te cuento un secreto?' },
    { quien: 'alex', texto: 'El pueblo entero me ayudó. Don Beto puso el kiosco. Doña Flora puso los pétalos.' },
    { quien: 'alex', texto: 'Sofi puso la flor que no era suya. Michi puso la cara de sospechoso.' },
    { quien: 'alex', texto: 'Yo solo puse las ganas.' },
    { quien: 'alex', texto: '...y esto.' },
    { efecto: 'florecer' }
  ],
  'colina.album': [
    { narracion: 'Alex saca un puñado de fotos y las va poniendo en el pasto, una por una.' },
    { narracion: 'Cada una tiene su letra atrás.' },
    { verAlbum: true }
  ],
  'colina.mensaje': [
    { quien: 'alex', texto: 'Liss, buscaste flores por todo el pueblo...' },
    { quien: 'alex', texto: 'pero la flor más bonita siempre fuiste tú, amorcito :>' },
    { quien: 'alex', texto: 'Gracias por existir, por tu risa, por quedarte.' },
    { quien: 'alex', texto: 'Hoy el pueblo entero te dio flores amarillas,' },
    { quien: 'alex', texto: 'y yo solo quise ser el que te las entregara.' },
    { narracion: 'En el papel del ramo, con su letra de siempre:' },
    { narracion: '«Te amo <333 — Alex»' }
  ],
  'colina.abrazo': [
    { quien: 'alex', texto: '¿Me das un abrazo?' },
    { eleccion: [{ texto: 'Sí' }, { texto: 'Sí, y otro más' }] },
    { quien: 'alex', texto: '(Se queda callado un rato, sonriendo.)' },
    { narracion: 'El sol se pone. Las flores amarillas se ven naranja un rato, y después violeta.' }
  ],
  'colina.tarjeta_final': [
    { narracion: 'Feliz Día de las Flores Amarillas' },
    { narracion: '21.09' },
    { narracion: 'Gracias por jugar, Liss.' }
  ],

  'album.vacio': [
    { narracion: 'Todavía no hay fotos aquí. Ve a caminar por el pueblo.' }
  ]
};
