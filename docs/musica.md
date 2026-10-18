# Música — UN JARDÍN PARA LISS

Siete pistas que Alex hizo con Gemini, una por momento de la historia. Si alguna falta o el
navegador no la puede leer, ese momento suena con el chiptune de siempre, así que el juego nunca
se queda mudo.

## Qué suena dónde

| Pista (`assets/musica/`) | Título en Gemini | Dónde suena | Por qué esa |
|---|---|---|---|
| `interiores.mp3` | Petals by the Window Pane | la casa y la florería | Do mayor, ~89 BPM, sin batería: el sol por la ventana que pedían los prompts de los dos interiores |
| `pueblo.mp3` | Yellow Petals on the Path | el pueblo | la caminata de la fiesta: ~92 BPM, con percusión suave |
| `petalos1.mp3` | Golden Petals Afternoon | pétalos 1 (el patio) | Sol mayor, ~144 BPM, la más brillante: la tarde de la plaza |
| `petalos2.mp3` | Chasing Golden Leaves | pétalos 2 (el parque) | ~152 BPM, la más rápida; las hojas doradas son las del viento |
| `colina.mp3` | Hillside Promise | subiendo la colina | ~80 BPM, como se pidió; *hillside* es la ladera |
| `final.mp3` | Last Light at the Summit | la escena con Alex | ~66 BPM y casi sin percusión: piano y cuerdas en la cima, al atardecer |
| `creditos.mp3` | After the Final Petal | los créditos, el título y el álbum | el cierre; el título la comparte para que el juego termine con la canción con la que empezó |

Las tres de la colina se repartieron por título y se confirmaron por tempo: las tres son lentas y
sin batería, y los prompts pedían 80 (colina), 66 (final) y 92 BPM (créditos).

## Cómo se comporta

- **Cada escena pide su tema** (`musica:` en el constructor, o `AG.Musica.tocar(clave)`), y
  `PISTAS` en `src/audio/chiptune.js` dice qué archivo suena con cada clave. Si dos claves
  comparten archivo (la casa y la florería), la canción sigue sin cortarse al cruzar la puerta.
- **Retoma donde iba**: volver al pueblo no lo empieza de cero.
- **Fundido**: 0.7 s de salida y 1.2 s de entrada entre pistas.
- **Loop**: cada pista se repite entera; termina con su propio fade-out, así que la vuelta se oye
  como la canción que empieza otra vez.
- **Carga**: la primera pista se baja apenas abre el título, todavía antes del primer toque. Las
  demás se bajan de a una en segundo plano. Decodificadas se guardan dos (~65 MB cada una).
- **Pestaña escondida**: la música se pausa y vuelve al volver (o con el próximo toque, en iOS).
- **Respaldo**: si una pista falla (falta el archivo, no hay red, `index.html` abierto desde el
  disco), ese tema suena en chiptune por el resto de la partida. Avisa en la consola, una vez por pista.

## Mezcla

Las pistas salen de `tools/preparar_musica.py` a **-16 LUFS** y en el juego suenan a ~-22 (bus
`pistas` a 0.5). Los efectos y el chiptune se escribieron con ganancias muy bajas, así que se
subieron (buses `efectos` a 2 y `chiptune` a 1.6) para que los blips del diálogo se oigan encima de
una pista grabada. Al final hay un limitador para que un efecto encima de un pico no sature.
Todo está en `VOLUMEN`, en `src/audio/chiptune.js`.

## Cambiar o agregar una pista

1. Bajar el `.mp3` de Gemini a `assets/source/musica/`, que no se sube al repo. El nombre puede
   traer un prefijo; se busca por el título.
2. En `tools/preparar_musica.py`, poner ese título en `PISTAS` (pista del juego → título).
3. Correr:
   ```bash
   .venv/bin/python tools/preparar_musica.py     # recorta silencios, normaliza, 128 kbps (pide ffmpeg)
   .venv/bin/python tools/actualizar_manifest.py
   ```
4. Si es una pista nueva (no un reemplazo), apuntarla en `PISTAS` de `src/audio/chiptune.js`.
   Por ejemplo, para que el título tenga la suya: `titulo: 'titulo'`.

Pendiente opcional: el título comparte la pista de los créditos y la casa la de la florería. Si
alguna vez se quiere una propia para cada uno, son estos mismos cuatro pasos.

## Build de un solo archivo

`tools/build_single.py` incrusta la música y el archivo pasa de ~4 a ~27 MB. Con `--sin-musica`
queda liviano y suena el chiptune.
