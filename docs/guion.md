# Guion — UN JARDÍN PARA LISS

Borrador completo y editable. Todo lo que está entre `«»` son huecos que Alex llena con nombres
reales, apodos o chistes de ustedes.

## Reglas de escritura

- **Se dice «foto», nunca «polaroid»**: en el juego suena más natural.
- **Liss casi no habla.** Es la protagonista silenciosa (como Kris en Deltarune): lo que siente sale
  como narración en `*`, y solo elige respuesta en los momentos importantes.
- **Narración** = líneas que empiezan con `*`, sin retrato, en cursiva mental. Describen cosas
  comunes como si fueran raras. Ese es el chiste.
- **Diálogo** = `PERSONAJE: texto`, con retrato y blips.
- **Él tutea, no voscea.** Para que combine con las palabras finales que eligió Alex. Si preferís
  voseo, se cambia en un solo lugar: `src/data/dialogos.js`.
- **Nada de tristeza.** El conflicto es "caminar y recibir", no "ganarle a alguien".
- Línea por línea, esto es lo que se transcribe a `src/data/dialogos.js`. Los identificadores
  (`casa.nota`, `flora.petalos`, …) son los que usa el código.

## Personajes

| Clave | Quién | Rol |
|---|---|---|
| `liss` | Liss | Protagonista. Sprite de la hoja que aporta Alex. |
| `alex` | Alex | Espera en la colina. Aparece solo en el final (y en la nota). |
| `flora` | Doña Flora | Florista, mamá de Sofi. Lanza la escena de pétalos 2 (la del viento) y da la tercera flor. |
| `beto` | Don Beto | El vecino de la plaza. Llama a Liss al salir, le cuenta de las fotos y le da la primera flor. |
| `sofi` | Sofi | Hija de Doña Flora. Lanza la escena de pétalos 1 (la tranquila) y da la segunda flor. |
| `michi` | Michi | Gato. Solo habla en `*`. Anda a los pies de Don Beto, pero nadie sabe de quién es. |
| `voz` | Voz del espejo | Chiste recurrente. No es Liss. |

Flujo de flores, una por persona y en orden: **Flor 1** ← Don Beto (de parte de Alex) · **Flor 2** ←
Sofi (pétalos 1, la ronda tranquila) · **Flor 3** ← Doña Flora (pétalos 2, la del viento) → abre la
colina.

---

## Acto 1 — Casa

**`casa.despertar`** (al entrar por primera vez)
```
* La cama está tibia todavía.
* Cinco minutos más no le harían daño a nadie.
* ...pero hoy algo se siente distinto.
```

**`casa.espejo`**
```
* Es el espejo. Ahí está Liss.
* (Guapa, como siempre.) — dice una voz que Liss no dijo.
```

**`casa.calendario`**
```
* Septiembre. Un día está marcado con un círculo amarillo.
* 21. Día de las flores amarillas.
```

**`casa.mesita`** → desbloquea **Recuerdo 1** (la foto se ve en la mesita de noche, junto a la lámpara)
```
* En la mesita de noche, apoyada contra la lámpara, hay una foto.
```
> Recuerdo 1 — «Pegaditos bien gonitos»

**`casa.nota`** (el motor de la historia)
```
* Hay una nota doblada en cuatro, con una letra que Liss conoce de memoria.
«Hoy el pueblo entero tiene flores amarillas para ti.»
«Busca tres y ven a la colina. Te espero. — A.»
```

**`casa.planta`**
```
* La planta de la ventana sigue viva.
* Sobrevive por pura terquedad, igual que su dueña.
```

**`casa.salir`**
```
* Afuera huele a pasto cortado y a pan.
```

---

## Acto 2 — El pueblo

El orden es fijo, y cada persona da **una** flor: **Don Beto → Sofi → Doña Flora**. Si Liss se
adelanta, quien todavía no le toca la manda con quien sí (`Pueblo.alUsar`, `Floreria.alUsar`).

**`pueblo.cartel`**
```
* FIESTA DE LAS FLORES AMARILLAS. Hoy.
* Todos los años. Todos los colores... bueno, uno: amarillo.
```

**`pueblo.beto.llamado`** (al salir de su casa sin la flor de Beto: la llama desde la plaza)
```
BETO: ¡Liss! ¡Eh, Liss! ¡Aquí, en la plaza!
* Don Beto la saluda con la mano desde la fuente. Michi, a sus pies, ni se inmuta.
```

**`pueblo.beto.saludo`** (Don Beto, en la plaza con Michi) → **Flor 1**
```
BETO: ¡Buenos días, Liss! Feliz Día de las Flores Amarillas.
BETO: Oye, ayer pasó por aquí un muchacho, Alex. Traía un montón de fotos.
BETO: Las fue escondiendo por todo el pueblo: en la plaza, en los árboles, en el parque... hasta en la florería.
BETO: Dijo que cada una tiene algo escrito atrás. Búscalas donde veas un brillito.
BETO: Ah, casi me olvido... el chico del que te hablé me dijo que te entregara esto.
→ entrega la flor de Don Beto
* Una flor amarilla, envuelta en papel de periódico. Muy Don Beto.
BETO: Dice que hay más. Sofi anda por el camino del parque, aquí abajo. Ve a verla.
```

**`pueblo.beto.chisme`** (la charla siguiente)
```
BETO: Ese muchacho llevaba semanas preguntando por flores. Semanas.
BETO: «¿Y si no le gustan?» me decía. «¿Y si se le olvida?»
BETO: Ni se te olvida ni se te va a olvidar. Mírate la cara.
```

**`pueblo.beto.pista.sofi`** (después, si falta la flor de Sofi)
```
BETO: ¿Ya viste a Sofi? Anda por el camino del parque, aquí abajo de la plaza.
```

**`pueblo.beto.pista.flora`** (si falta la de Doña Flora)
```
BETO: La florería de Doña Flora está pasando la plaza, la del techo de madera. Ándale.
```

**`pueblo.beto.pista.colina`** (con las tres)
```
BETO: ¿Tres flores? Entonces ya sabes: el camino del cartel, para arriba.
BETO: Y no corras, que la vista es bonita.
```

**`pueblo.buzon`**
```
* Es un buzón. No tiene cartas, pero tiene esperanza.
«Si estás leyendo esto, ya casi es la hora. Sube despacio, que la vista es bonita.» — A.
```

**`pueblo.michi`** (tres charlas en orden; Michi está a los pies de Don Beto)
```
* Michi te mira como si supiera algo. Los gatos siempre saben algo.
MICHI: * Miau.
* Michi maúlla. Suena sospechosamente a "ánimo".
* Michi se estira. Tú también quisieras estirarte así de tranquila.
```

**`pueblo.banco`** → desbloquea **Recuerdo 2**
```
* En el banco del parque alguien dejó una foto con una piedrita encima para que el viento no se la llevara.
```

**`pueblo.arbol`** → desbloquea **Recuerdo 3**
```
* En el tronco hay dos iniciales talladas. No las talló nadie hoy: llevan ahí un buen rato.
* Al pie del tronco, alguien dejó una foto apoyada.
```

**`pueblo.lampara`** → desbloquea **Recuerdo 5**
```
* Alguien ató una foto al poste de la luz con un hilo amarillo.
* El viento la hace girar despacio, como si estuviera bailando.
```

**`pueblo.sofi.antes`** (Sofi, en el camino del parque, si Liss todavía no vio a Beto)
```
SOFI: ¡Hola, Liss! Don Beto te anda buscando. Está en la plaza, con Michi.
```

**`pueblo.sofi.saludo`** (es hija de Doña Flora)
```
SOFI: ¡Liss! ¿Viste el viento de hoy? Se llevó los pétalos del patio de mi mamá.
SOFI: Mi mamá es Doña Flora, la de la florería. Los quería para un ramo bien especial.
SOFI: ¿Me ayudas a atraparlos? Así se los llevamos juntas.
```
→ inicia la **Escena de pétalos 1** (la tranquila).

**`pueblo.sofi.gracias`** (después de los pétalos, si falta Doña Flora)
```
SOFI: ¿Ya fuiste a la tienda de mi mamá? Es la del techo de madera, pasando la plaza.
```

**`pueblo.sofi.final`** (con las tres flores)
```
SOFI: ¡Corre a la colina! Y después me cuentas.
```

**`pueblo.flora.beto`** (Doña Flora, en la florería, si Liss todavía no vio a Beto)
```
FLORA: ¡Liss, mi niña! Qué gusto verte por aquí.
FLORA: Don Beto te anda buscando, está en la plaza. Anda, ve a saludarlo.
```

**`pueblo.flora.sofi`** (si todavía no ayudó a Sofi)
```
FLORA: ¡Liss, mi niña! Ay, perdóname, ahorita ando con las manos ocupadas.
FLORA: ¿Ya viste a mi Sofi? Anda por el camino del parque, y creo que te necesita.
```

**`pueblo.flora.saludo`**
```
FLORA: ¡Liss! Sofi ya me contó que le ayudaste. Gracias, mi niña.
FLORA: Pero ay, qué día. El viento se llevó los pétalos de mi ramo más bonito hasta el parque.
FLORA: Allá sopla fuerte y se mezclan con hojas secas. ¿Me echas la mano?
```
→ inicia la **Escena de pétalos 2** (la del viento).

**`pueblo.flora.gracias`** (con las tres flores)
```
FLORA: ¿Y qué haces aquí todavía? Anda, sube a la colina.
FLORA: El camino sale del cruce, donde está el cartel.
```

**`pueblo.floreria.mostrador`** → desbloquea **Recuerdo 4**
```
* Debajo del mostrador, pegada con cinta adhesiva, hay otra foto.
* Doña Flora no dice nada. Doña Flora sonríe.
```

**`pueblo.cartel_colina`** (el cartel al pie del camino de la colina)
```
* Un cartel de madera con una flecha que apunta camino arriba.
«A la colina». Alguien repasó las letras con pintura amarilla hace poquito.
```

**`pueblo.caminito`** (el caminito de la florería, que no sube)
```
* El caminito se pierde entre los pinos. Por aquí no se sube a la colina.
```

**`pueblo.colina.bloqueada`** (el camino de la colina sin las tres flores)
```
* El sendero sube entre flores. Todavía no.
* Tres flores. Eso decía la nota.
```

---

## Acto 3 — Escena de pétalos 1: «El patio de Doña Flora», con Sofi

Contexto: el viento se llevó los pétalos del patio de la florería y Sofi quiere llevárselos a su
mamá. Es la ronda **tranquila**: atrapar **10 pétalos** en 45 segundos, sin viento ni hojas secas;
nunca se pierde (si el tiempo se acaba, se vuelve a intentar sin castigo). Al terminar, Liss vuelve
al pueblo junto a Sofi.

**`petalos1.intro`**
```
SOFI: ¡Ahí vienen! Atrápalos antes de que toquen el suelo.
```

**`petalos1.reintento`**
```
SOFI: ¡Uy, casi! No pasa nada, todavía quedan un montón. ¿Otra vez?
```

**`petalos1.victoria`** → **Flor 2**
```
SOFI: ¡Los juntamos todos! Mi mamá se va a poner feliz.
SOFI: Toma, esta es para ti. La escogí yo: es la más bonita del patio.
→ entrega la flor de Sofi
SOFI: Y antes de subir a la colina, pasa por la tienda de mi mamá. Creo que te tiene algo.
```

## Acto 4 — Escena de pétalos 2: «El viento del parque», con Doña Flora

Contexto: el viento se llevó al parque los pétalos del ramo más bonito de Doña Flora. Es la ronda
**movida**: atrapar **14 pétalos** en 50 segundos, con ráfagas que empujan todo hacia un lado y
hojas secas que restan. Al terminar, Liss vuelve a la florería con las tres flores y se abre la
colina.

**`petalos2.intro`**
```
FLORA: ¡Ahí van! Los amarillos sí, las hojas secas no.
FLORA: Y cuando sople el viento, fíjate hacia dónde se los lleva.
```

**`petalos2.reintento`**
```
FLORA: Ay, se fueron. No importa, el viento siempre presta. ¿Otra vez?
```

**`petalos2.victoria`** → **Flor 3**
```
FLORA: ¡Perfecto! Ni una hoja seca, ¿eh? Puro amarillo.
FLORA: Toma. Y no te la cobro, ni se te ocurra.
→ entrega la flor de Doña Flora
FLORA: Ya tienes las tres, mi niña. Ahora sube a la colina: allá arriba te espera la última sorpresa.
* El cielo se está poniendo naranja.
```

---

## Acto 5 — La colina (final)

**`colina.entrada`**
```
* Cuesta arriba hace más fresco. Huele a pasto y a algo dulce.
* Alguien subió antes que tú.
```

**`colina.alex.1`**
```
ALEX: Llegaste.
ALEX: No sabes cuánto me alegra verte llegar.
```

**`colina.alex.2`**
```
ALEX: ¿Te cuento un secreto?
ALEX: El pueblo entero me ayudó. Don Beto te guardó la primera flor.
ALEX: Sofi y Doña Flora pusieron los pétalos. Michi puso la cara de sospechoso.
ALEX: Yo solo puse las ganas.
ALEX: ...y esto.
```
→ aparece el ramo.

**`colina.album`** → desbloquea **Recuerdo 6** y después muestra el álbum con los 6
```
* Alex saca un puñado de fotos y las va poniendo en el pasto, una por una.
* La última no la habías visto nunca.
* Cada una tiene su letra atrás.
```

**`colina.mensaje`** (las palabras de Alex — ya ajustadas por él ✅)
```
ALEX: Liss, buscaste flores por todo el pueblo...
ALEX: pero la flor más bonita siempre fuiste tú, amorcito :>
ALEX: Gracias por existir, por tu risa, por quedarte.
ALEX: Hoy el pueblo entero te dio flores amarillas,
ALEX: y yo solo quise ser el que te las entregara.
```
```
* En el papel del ramo, con su letra de siempre:
«Te amo <333 — Alex»
```

**`colina.abrazo`** (última elección)
```
ALEX: ¿Me das un abrazo?
```
Opciones: `Sí` · `Sí, y otro más`
```
ALEX: (Se queda callado un rato, sonriendo.)
* El sol se pone. Las flores amarillas se ven naranja un rato, y después violeta.
```

**`colina.tarjeta_final`** (la antesala de los créditos, que abren con el «¡FELIZ CUMPLEAÑOS!»)
```
* El pueblo entero celebra algo más que las flores amarillas...
* ...porque hoy es tu cumpleaños.
```

---

## Los 6 recuerdos

Cada uno es una foto real con su marco, un pie de foto y un mensajito de Alex. Las fotos las
aporta Alex en `_referencias/fotos/`; el pipeline las optimiza a `assets/fotos/recuerdo_rN.jpg`.

Los textos son los que se ven en el juego y viven en `src/data/personajes.js`: esta tabla es el
registro de qué foto quedó en cada recuerdo. Los recuerdos 1 a 5 se encuentran en los mapas: cada
foto se ve donde está (`foto x y` en `maps/*.txt`) con un brillo suave hasta que Liss la mira. Título y pie se parten solos en renglones de 23
letras bajo la foto (caben 4 entre los dos) y el mensaje en renglones de 24 (caben 10);
`node tools/validar_contenido.js` avisa si un texto nuevo no entra.

| # | Título | Pie de foto | Mensaje | Foto que quedó |
|---|---|---|---|---|
| 1 | «Pegaditos bien gonitos» | «Tan preciosa con tu overol :>» | «Tu estilazo siempre hace q nuestras fotos juntos brillen.» | Selfie de día, mejilla con mejilla |
| 2 | «Nuestra plantita de amor» | «Crecimos tanto ese día» | «Desde ese día siento que hemos crecido tantísimo juntos y siento que nuestro compromiso ha tomado más fuerza.» | Ella haciéndote carita de burla, con la plantita |
| 3 | «Entre las luces» | «Tú siempre brillas más» | «Un bello recuerdo de una salida juntos inolvidable, con tu risa siendo siempre la luz más brillante q acompaña a la mía <3» | Los dos riéndose, de noche, con guirnaldas |
| 4 | «Más sonrisitas» | «Más amorsss» | «Otro día que recuerdo con mucha felicidad y cariño de nosotros compartiendo una bella noche nuestro bello amor.» | Un lugar con luces y un cartel violeta detrás |
| 5 | «En mi pecho» | «Lo más cerca de mí <3» | «Siempre me encanta tenerte cerca mío, pero esta posición es mi favorita pq es cuando más cerca te siento de mí.» | Los dos en el sillón, ella apoyada en él |
| 6 | «Bajo las flores» | «Besando la flor más bella» | «Mil jardines llenos de flores he visto y aun así sólo quiero contemplar la flor más bella que es tu ser completo y el amor q compartimos.» | Posada bajo el arco de flores, con las luces |

---

## Créditos (pantalla final)

Sin nada técnico: el motor, la fuente y sus licencias quedan en el README.

```
UN JARDÍN PARA LISS
Una aventura hecha a mano por Alex
(Y con ayuda de Claudio, jeje)

Historia, arte y fotos: Alex y Liss
Música: Alex, con Gemini

Gracias a Doña Flora, a Don Beto, a Sofi y a Michi,
que son inventados, pero ayudaron muchísimo.

21 de septiembre.

Feliz Día de las Flores Amarillas.

Y hoy, sobre todo:
¡FELIZ CUMPLEAÑOS, AMOYCHITO!

Gracias, mi chulita, por tu atención,
por tu cariño, por tu compromiso
y por tu inmenso amor.

Te deseo flores, mi osita preciosita,
y una vida llenísima
de bendiciones y amors.

Este jardín de flores es para ti,
mi bellísima noviecita :>

Te amo, mi Liss hermosa.
```

Al terminar de subir queda la pantalla final: «¡Feliz cumpleaños, amorcito!» y «Gracias por jugar,
te amo <333».

---

## Pendientes para Alex

1. **Nombres reales** de los NPCs (Doña Flora, Don Beto, Sofi, Michi) si prefieres los de verdad.
2. **Un chiste interno** para `pueblo.beto.chisme` (marcado para reemplazo).
3. **Un apodo** que quieras que use el espejo en `casa.espejo`.
4. **Las 6 fotos** con sus descripciones reales (tabla de arriba).
5. ~~**¿Canción significativa?**~~ ✅ Alex hizo la música con Gemini: siete pistas, una por momento
   (ver `docs/musica.md`).
