# Guion — UN JARDÍN PARA LISS

Borrador completo y editable. Todo lo que está entre `«»` son huecos que Alex llena con nombres
reales, apodos o chistes de ustedes.

## Reglas de escritura

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
| `flora` | Doña Flora | Florista. Da la primera flor y lanza la escena de pétalos 1. |
| `beto` | Don Beto | Kiosquero. Suelta el mensajito pagado por Alex. |
| `sofi` | Sofi | Niña del parque. Regala la segunda flor y da el tip del viento. |
| `michi` | Michi | Gato. Solo habla en `*`. Nadie sabe de quién es. |
| `voz` | Voz del espejo | Chiste recurrente. No es Liss. |

Flujo de flores: **Flor 1** ← Doña Flora (pétalos 1) · **Flor 2** ← Sofi (cariño) · **Flor 3** ←
pétalos 2 en el parque → abre la colina.

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

**`casa.escritorio`** → desbloquea **Recuerdo 1**
```
* En el escritorio hay un polaroid apoyado en el marco de la ventana.
```
> Recuerdo 1 — «La primera vez»

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

**`pueblo.cartel`**
```
* FIESTA DE LAS FLORES AMARILLAS. Hoy.
* Todos los años. Todos los colores... bueno, uno: amarillo.
```

**`pueblo.flora.saludo`** (Doña Flora, en la florería)
```
FLORA: ¡Liss! Justo a quien necesitaba.
FLORA: Se me volaron los pétalos del ramo más bonito del año.
FLORA: ¿Me ayudas a juntarlos antes de que el viento se los lleve?
```
→ inicia la **Escena de pétalos 1**.

**`pueblo.flora.post`** → entrega **Flor 1**
```
FLORA: ¡Bien hecho, mi niña! Este ramo ya tiene dueña.
FLORA: Toma. Y no te la cobro, ni se te ocurra.
```

**`pueblo.beto.saludo`** (Don Beto, kiosco)
```
BETO: Ah, tú. Un tal Alex pasó ayer y me dejó pagado lo que quisieras.
BETO: No le digas que te dije.
* El kiosquero guiña un ojo con toda la discreción de un kiosquero.
```

**`pueblo.beto.chisme`** (segunda charla)
```
BETO: Ese muchacho llevaba semanas preguntando por flores. Semanas.
BETO: «¿Y si no le gustan?» me decía. «¿Y si se le olvida?»
BETO: Ni se te olvida ni se te va a olvidar. Mírate la cara.
```

**`pueblo.buzon`**
```
* Es un buzón. No tiene cartas, pero tiene esperanza.
«Si estás leyendo esto, ya casi es la hora. Sube despacio, que la vista es bonita.» — A.
```

**`pueblo.michi`** (tres charlas en orden)
```
* Michi te mira como si supiera algo. Los gatos siempre saben algo.
* Michi maúlla. Suena sospechosamente a "ánimo".
* Michi se estira. Tú también quisieras estirarte así de tranquila.
```

**`pueblo.banco`** → desbloquea **Recuerdo 2**
```
* En el banco del parque alguien dejó un polaroid con una piedrita encima para que el viento no se
  lo llevara.
```

**`pueblo.arbol`** → desbloquea **Recuerdo 3**
```
* En el tronco hay dos iniciales talladas. No las talló nadie hoy: llevan ahí un buen rato.
```

**`pueblo.floreria.mostrador`** → desbloquea **Recuerdo 4**
```
* Debajo del mostrador, pegado con cinta adhesiva, hay otro polaroid.
* Doña Flora no dice nada. Doña Flora sonríe.
```

**`pueblo.sofi.saludo`** (Sofi, cerca del parque)
```
SOFI: Hola. ¿Tú también vienes por las flores?
SOFI: Yo ya tengo la mía. Esta es para ti.
```
→ entrega **Flor 2**.

```
SOFI: Es de mi mamá. Tiene un jardín enorme y le sobran.
SOFI: En el parque el viento sopla feo.
SOFI: Si un pétalo se va de lado, ¡corre!
```

**`pueblo.sofi.pista`** (antes de los pétalos 2)
```
SOFI: Yo te aviso si lo veo venir. Tú corre.
```
→ inicia la **Escena de pétalos 2**.

**`pueblo.lampara`** → desbloquea **Recuerdo 5**
```
* Alguien ató un polaroid al poste de la luz con un hilo amarillo.
* El viento lo hace girar despacio, como si estuviera bailando.
```

---

## Acto 3 — Escena de pétalos 1: «Los pétalos de la plaza»

Contexto: los pétalos del ramo de Doña Flora se volaron. Reglas: atrapar **10 pétalos** en 45
segundos; nunca se pierde (si el tiempo se acaba, se puede volver a intentar sin castigo).

**`petalos1.intro`**
```
FLORA: ¡Ahí van! ¡Atrápalos con las manos y con el corazón!
```
**`petalos1.reintento`**
```
FLORA: Ay, se fueron. No importa, el viento siempre presta. ¿Otra vez?
```
**`petalos1.victoria`**
```
FLORA: ¡Perfecto! Ni una hoja seca, ¿eh? Solo amarillo.
```
→ **Flor 1**.

## Acto 4 — Escena de pétalos 2: «El viento del parque»

Contexto: el viento sopla fuerte. Reglas: atrapar **14 pétalos** en 50 segundos; el viento empuja
los pétalos hacia un lado y hay hojas secas que restan. Al ganar, se abre la colina.

**`petalos2.intro`**
```
SOFI: ¡Ahí van! ¡Y el viento sopla fuerte, corre!
```
**`petalos2.victoria`**
```
SOFI: ¡Lo lograste!
SOFI: Toma, la tercera. Entre las dos ya son tres.
* El camino a la colina ya está libre, y el cielo se está poniendo naranja.
```
→ **Flor 3**.

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
ALEX: El pueblo entero me ayudó. Don Beto puso el kiosco. Doña Flora puso los pétalos.
ALEX: Sofi puso la flor que no era suya. Michi puso la cara de sospechoso.
ALEX: Yo solo puse las ganas.
ALEX: ...y esto.
```
→ aparece el ramo.

**`colina.album`** (se muestran los 6 recuerdos, uno por uno, con su foto)
```
* Alex saca un puñado de fotos y las va poniendo en el pasto, una por una.
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

**`colina.tarjeta_final`**
```
* Feliz Día de las Flores Amarillas
* 21.09
* Gracias por jugar, Liss.
```

---

## Los 6 recuerdos

Cada uno es un polaroid con la foto real, un pie de foto y un mensajito de Alex. Las fotos las
aporta Alex en `_referencias/fotos/`; el pipeline las optimiza a `assets/fotos/recuerdo_0N.jpg`.

| # | Título | Pie de foto | Mensaje | Foto sugerida |
|---|---|---|---|---|
| 1 | «La primera vez» | «El día que nos conocimos» | «Antes de esta foto yo ya estaba nervioso. Después también.» | La foto más vieja que tengan juntos |
| 2 | «Tu risa» | «Aquí te reías de mí» | «No es la mejor foto que te he tomado, pero es mi favorita.» | Ella riéndose |
| 3 | «Ese día que llovió» | «No llevábamos paraguas» | «No nos importó. Volvería a mojarme contigo.» | Foto con lluvia / paraguas |
| 4 | «El lugar de siempre» | «Ya nos conocen y todo» | «Aquí quiero volver contigo mil veces más.» | El café, la plaza, su lugar |
| 5 | «Nosotros» | «Un día cualquiera, contigo» | «Los días normales contigo no tienen nada de normales.» | Foto espontánea favorita |
| 6 | «Hoy» | «Esta la tomamos hoy» | «La puse al final a propósito. Es la que sigue.» | Una foto de hoy, o una que le tomen el mismo 21 |

---

## Créditos (pantalla final)

```
UN JARDÍN PARA LISS
Una aventura hecha a mano por Alex, con ayuda de Claude.

Historia, arte y fotos: Alex y Liss
Motor: Phaser 4
Fuente: Press Start 2P (OFL)
Música: chiptune generado en vivo por el navegador

Gracias a Doña Flora, a Don Beto, a Sofi y a Michi,
que son inventados, pero ayudaron muchísimo.

21 de septiembre.
```

---

## Pendientes para Alex

1. **Nombres reales** de los NPCs (Doña Flora, Don Beto, Sofi, Michi) si prefieres los de verdad.
2. **Un chiste interno** para `pueblo.beto.chisme` (marcado para reemplazo).
3. **Un apodo** que quieras que use el espejo en `casa.espejo`.
4. **Las 6 fotos** con sus descripciones reales (tabla de arriba).
5. **¿Canción significativa?** Si existe, se versiona a chiptune para los créditos; si no, se compone una.
