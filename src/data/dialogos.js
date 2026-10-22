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
  'casa.mesita': [
    { narracion: 'En la mesita de noche, apoyada contra la lámpara, hay una foto.' },
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
    { narracion: 'En el banco del parque alguien dejó una foto con una piedrita encima para que el viento no se la llevara.' },
    { darRecuerdo: 'r2' }
  ],
  'pueblo.arbol': [
    { narracion: 'En el tronco hay dos iniciales talladas. No las talló nadie hoy: llevan ahí un buen rato.' },
    { narracion: 'Al pie del tronco, alguien dejó una foto apoyada.' },
    { darRecuerdo: 'r3' }
  ],
  'pueblo.lampara': [
    { narracion: 'Alguien ató una foto al poste de la luz con un hilo amarillo.' },
    { narracion: 'El viento la hace girar despacio, como si estuviera bailando.' },
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

  'pueblo.cartel_colina': [
    { narracion: 'Un cartel de madera con una flecha que apunta camino arriba.' },
    { narracion: '«A la colina». Alguien repasó las letras con pintura amarilla hace poquito.' }
  ],
  'pueblo.caminito': [
    { narracion: 'El caminito se pierde entre los pinos. Por aquí no se sube a la colina.' }
  ],

  // Don Beto: el primero. La llama desde la plaza apenas sale de su casa, le cuenta de las fotos
  // y le da la primera flor.
  'pueblo.beto.llamado': [
    { quien: 'beto', texto: '¡Liss! ¡Eh, Liss! ¡Aquí, en la plaza!' },
    { narracion: 'Don Beto la saluda con la mano desde la fuente. Michi, a sus pies, ni se inmuta.' }
  ],
  'pueblo.beto.saludo': [
    { quien: 'beto', texto: '¡Buenos días, Liss! Feliz Día de las Flores Amarillas.' },
    { quien: 'beto', texto: 'Oye, ayer pasó por aquí un muchacho, Alex. Traía un montón de fotos.' },
    { quien: 'beto', texto: 'Las fue escondiendo por todo el pueblo: en la plaza, en los árboles, en el parque... hasta en la florería.' },
    { quien: 'beto', texto: 'Dijo que cada una tiene algo escrito atrás. Búscalas donde veas un brillito.' },
    { quien: 'beto', texto: 'Ah, casi me olvido... el chico del que te hablé me dijo que te entregara esto.' },
    { darFlor: 'beto' },
    { narracion: 'Una flor amarilla, envuelta en papel de periódico. Muy Don Beto.' },
    { quien: 'beto', texto: 'Dice que hay más. Sofi anda por el camino del parque, aquí abajo. Ve a verla.' }
  ],
  'pueblo.beto.chisme': [
    { quien: 'beto', texto: 'Ese muchacho llevaba semanas preguntando por flores. Semanas.' },
    { quien: 'beto', texto: '«¿Y si no le gustan?» me decía. «¿Y si se le olvida?»' },
    { quien: 'beto', texto: 'Ni se te olvida ni se te va a olvidar. Mírate la cara.' }
  ],
  'pueblo.beto.pista.sofi': [
    { quien: 'beto', texto: '¿Ya viste a Sofi? Anda por el camino del parque, aquí abajo de la plaza.' }
  ],
  'pueblo.beto.pista.flora': [
    { quien: 'beto', texto: 'La florería de Doña Flora está pasando la plaza, la del techo de madera. Ándale.' }
  ],
  'pueblo.beto.pista.colina': [
    { quien: 'beto', texto: '¿Tres flores? Entonces ya sabes: el camino del cartel, para arriba.' },
    { quien: 'beto', texto: 'Y no corras, que la vista es bonita.' }
  ],

  // Sofi: la hija de Doña Flora. Propone juntar los pétalos del patio (la ronda tranquila) y al
  // terminar da la segunda flor y manda a Liss a la tienda.
  'pueblo.sofi.antes': [
    { quien: 'sofi', texto: '¡Hola, Liss! Don Beto te anda buscando. Está en la plaza, con Michi.' }
  ],
  'pueblo.sofi.saludo': [
    { quien: 'sofi', texto: '¡Liss! ¿Viste el viento de hoy? Se llevó los pétalos del patio de mi mamá.' },
    { quien: 'sofi', texto: 'Mi mamá es Doña Flora, la de la florería. Los quería para un ramo bien especial.' },
    { quien: 'sofi', texto: '¿Me ayudas a atraparlos? Así se los llevamos juntas.' },
    { lanzarEscena: { clave: 'Petalos', datos: { tipo: 'petalos1', volver: 'Pueblo', inicio: { px: 496, py: 328 } } } }
  ],
  'pueblo.sofi.gracias': [
    { quien: 'sofi', texto: '¿Ya fuiste a la tienda de mi mamá? Es la del techo de madera, pasando la plaza.' }
  ],
  'pueblo.sofi.final': [
    { quien: 'sofi', texto: '¡Corre a la colina! Y después me cuentas.' }
  ],

  // Doña Flora: la última. Su ronda es la del parque al atardecer, con ráfagas y hojas secas, y
  // con su flor Liss ya tiene las tres.
  'pueblo.flora.beto': [
    { quien: 'flora', texto: '¡Liss, mi niña! Qué gusto verte por aquí.' },
    { quien: 'flora', texto: 'Don Beto te anda buscando, está en la plaza. Anda, ve a saludarlo.' }
  ],
  'pueblo.flora.sofi': [
    { quien: 'flora', texto: '¡Liss, mi niña! Ay, perdóname, ahorita ando con las manos ocupadas.' },
    { quien: 'flora', texto: '¿Ya viste a mi Sofi? Anda por el camino del parque, y creo que te necesita.' }
  ],
  'pueblo.flora.saludo': [
    { quien: 'flora', texto: '¡Liss! Sofi ya me contó que le ayudaste. Gracias, mi niña.' },
    { quien: 'flora', texto: 'Pero ay, qué día. El viento se llevó los pétalos de mi ramo más bonito hasta el parque.' },
    { quien: 'flora', texto: 'Allá sopla fuerte y se mezclan con hojas secas. ¿Me echas la mano?' },
    { lanzarEscena: { clave: 'Petalos', datos: { tipo: 'petalos2', volver: 'Floreria', inicio: { px: 248, py: 178 } } } }
  ],
  'pueblo.flora.gracias': [
    { quien: 'flora', texto: '¿Y qué haces aquí todavía? Anda, sube a la colina.' },
    { quien: 'flora', texto: 'El camino sale del cruce, donde está el cartel.' }
  ],
  'pueblo.floreria.mostrador': [
    { narracion: 'Debajo del mostrador, pegada con cinta adhesiva, hay otra foto.' },
    { narracion: 'Doña Flora no dice nada. Doña Flora sonríe.' },
    { darRecuerdo: 'r4' }
  ],
  'pueblo.floreria.estante': [
    { narracion: 'Girasoles, margaritas, un ramo que dice «para alguien especial».' },
    { narracion: 'Está apartado. Tiene el nombre de Liss, y ni siquiera está escrito.' }
  ],

  'pueblo.colina.bloqueada': [
    { narracion: 'El sendero sube entre flores. Todavía no.' },
    { narracion: 'Tres flores. Eso decía la nota.' }
  ],

  // La ronda de Sofi: el patio de la florería de día, sin viento ni hojas.
  'petalos1.intro': [
    { quien: 'sofi', texto: '¡Ahí vienen! Atrápalos antes de que toquen el suelo.' }
  ],
  'petalos1.reintento': [
    { quien: 'sofi', texto: '¡Uy, casi! No pasa nada, todavía quedan un montón. ¿Otra vez?' }
  ],
  'petalos1.victoria': [
    { quien: 'sofi', texto: '¡Los juntamos todos! Mi mamá se va a poner feliz.' },
    { quien: 'sofi', texto: 'Toma, esta es para ti. La escogí yo: es la más bonita del patio.' },
    { darFlor: 'sofi' },
    { quien: 'sofi', texto: 'Y antes de subir a la colina, pasa por la tienda de mi mamá. Creo que te tiene algo.' }
  ],

  // La ronda de Doña Flora: el parque al atardecer, con ráfagas y hojas secas.
  'petalos2.intro': [
    { quien: 'flora', texto: '¡Ahí van! Los amarillos sí, las hojas secas no.' },
    { quien: 'flora', texto: 'Y cuando sople el viento, fíjate hacia dónde se los lleva.' }
  ],
  'petalos2.reintento': [
    { quien: 'flora', texto: 'Ay, se fueron. No importa, el viento siempre presta. ¿Otra vez?' }
  ],
  'petalos2.victoria': [
    { quien: 'flora', texto: '¡Perfecto! Ni una hoja seca, ¿eh? Puro amarillo.' },
    { quien: 'flora', texto: 'Toma. Y no te la cobro, ni se te ocurra.' },
    { darFlor: 'flora' },
    { quien: 'flora', texto: 'Ya tienes las tres, mi niña. Ahora sube a la colina: allá arriba te espera la última sorpresa.' },
    { narracion: 'El cielo se está poniendo naranja.' }
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
    { quien: 'alex', texto: 'El pueblo entero me ayudó. Don Beto te guardó la primera flor.' },
    { quien: 'alex', texto: 'Sofi y Doña Flora pusieron los pétalos. Michi puso la cara de sospechoso.' },
    { quien: 'alex', texto: 'Yo solo puse las ganas.' },
    { quien: 'alex', texto: '...y esto.' },
    { efecto: 'florecer' }
  ],
  'colina.album': [
    { narracion: 'Alex saca un puñado de fotos y las va poniendo en el pasto, una por una.' },
    { narracion: 'La última no la habías visto nunca.' },
    { darRecuerdo: 'r6' },
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
    { narracion: 'El pueblo entero celebra algo más que las flores amarillas...' },
    { narracion: '...porque hoy es tu cumpleaños.' }
  ],

  'album.vacio': [
    { narracion: 'Todavía no hay fotos aquí. Ve a caminar por el pueblo.' }
  ]
};
