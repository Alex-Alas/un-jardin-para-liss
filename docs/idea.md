# Idea — UN JARDÍN PARA LISS

## En una frase

Un jueguito top-down de 6 a 10 minutos donde Liss despierta el 21 de septiembre, recorre un pueblo
pixelado que le da mensajitos y fotos de Alex, y termina en la colina recibiendo sus flores amarillas.

## Para quién

Para **Liss**, en su celular, hoy. No hay tutorial largo, no hay forma de perder, no hay pantalla de
derrota: la única posibilidad es llegar al final.

## Tono

Indie retro cozy tipo **Deltarune**: humor seco y tierno, cajas de diálogo con retratos, corazón de
guardado, transiciones oscuras, descripciones raras de objetos comunes y un final sincero sin
cursilería.

## Lo que hace el juego (sistemas)

1. **Exploración top-down** en mapas pintados a mano (generados por script): casa, pueblo (con plaza, kiosco, florería y parque),
   florería y colina.
2. **Diálogos** como vehículo principal: cada NPC suelta algo que Alex escribió para ella.
3. **Recuerdos** (6): objetos interactuables abren un polaroid con una foto real de los dos, un pie de
   foto y un mensajito. Quedan guardados en un **álbum** que puede revisar cuando quiera.
4. **2 escenas de pétalos** (el núcleo mecánico, máximo dos): atrapar pétalos que caen; la primera es
   un tutorial suave, la segunda tiene viento y hojas que restan. Son las que hacen avanzar la
   historia y entregan flores.
5. **Final**: la colina al atardecer, el álbum completo, el ramo y el mensaje final.

## Los cinco latidos

1. **Casa** — despertar, la nota firmada "— A.", el primer recuerdo en el escritorio.
2. **Pueblo** — los NPCs y sus mensajitos; tres flores que conseguir.
3. **Pétalos 1 (plaza)** — aprender a atrapar pétalos; flor 1.
4. **Pétalos 2 (parque)** — el viento; flor 3 y camino a la colina.
5. **Colina** — Alex, el ramo, los seis recuerdos y el mensaje final.

## Decisiones y por qué

- **Liss es la protagonista** (no Alex): el juego es su aventura; él la espera al final.
- **Sin batallas**: el conflicto no es ganarle a nadie, es recorrer y recibir.
- **Máximo 2 minijuegos**: pedido explícito de Alex; la historia avanza con ellos, no con relleno.
- **Fotos reales dentro del juego**: los recuerdos son el corazón; el pixel art los enmarca.
- **Nada de perder**: es un regalo, no un reto.
- **Sin backend, sin frameworks**: Phaser vendorizado y arte generado con Python. El juego entero
  funciona con abrir `index.html`, y también cabe en un solo archivo HTML si hace falta enviarlo.

## Lo que NO es

No es un RPG largo, no tiene inventario complejo, no tiene múltiples finales, no tiene monedas, no
tiene combate, no tiene inglés. Si algo de eso aparece, se recorta.
