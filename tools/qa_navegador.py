#!/usr/bin/env python3
"""QA del juego en un navegador real: recorre la partida y guarda capturas.

    tools/qa_navegador.sh                 # prepara el entorno y corre esto mismo

No es dependencia del juego: solo se usa para revisar que la partida funcione de punta a punta.
"""

from __future__ import annotations

import asyncio
import os
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8017"
SALIDA = sys.argv[2] if len(sys.argv) > 2 else "qa"
EXE = os.environ.get("QA_CHROMIUM") or None
os.makedirs(SALIDA, exist_ok=True)

MENSAJES: list[str] = []


async def captura(pagina, nombre: str) -> None:
    await pagina.screenshot(path=f"{SALIDA}/{nombre}.png")
    print(f"  · {nombre}.png")


async def pasar_dialogo(pagina, veces: int = 1, pausa: int = 260) -> None:
    for _ in range(veces):
        await pagina.keyboard.press("z")
        await pagina.wait_for_timeout(pausa)


async def cerrar_dialogo(pagina, maximo: int = 60, pausa: int = 220) -> None:
    """Avanza el diálogo hasta que se cierre (la máquina de escribir necesita dos toques por línea)."""
    for _ in range(maximo):
        activo = await pagina.evaluate(
            "() => { const s = AG.juego.scene.getScenes(true)[0];"
            " return Boolean(s && s.dialogo && s.dialogo.activa); }"
        )
        if not activo:
            return
        await pagina.keyboard.press("z")
        await pagina.wait_for_timeout(pausa)


async def usar(pagina, dialogo: str) -> None:
    """Dispara un objeto del mapa por su diálogo (para no depender de caminar hasta él)."""
    await pagina.evaluate(
        "() => { const s = AG.juego.scene.getScenes(true)[0];"
        f" const o = s.objetos.filter(x => x.dialogo === '{dialogo}')[0];"
        " if (o) s.usarObjeto(o); }"
    )
    await pagina.wait_for_timeout(500)


async def caminar(pagina, tecla: str, ms: int) -> None:
    await pagina.keyboard.down(tecla)
    await pagina.wait_for_timeout(ms)
    await pagina.keyboard.up(tecla)
    await pagina.wait_for_timeout(180)


async def a_pantalla(pagina, gx: float, gy: float):
    """Convierte coordenadas del juego (480x270) a coordenadas del navegador."""
    caja = await pagina.evaluate(
        "() => { const r = document.querySelector('canvas').getBoundingClientRect();"
        " return { x: r.x, y: r.y, w: r.width, h: r.height }; }"
    )
    return caja["x"] + gx * caja["w"] / 480, caja["y"] + gy * caja["h"] / 270


async def pasada_movil(p) -> None:
    print("  · pasada móvil (390x844 táctil)")
    contexto = await p.chromium.launch_persistent_context(
        user_data_dir="/tmp/qa-un-jardin/perfil-movil",
        viewport={"width": 390, "height": 844},
        has_touch=True,
        is_mobile=True,
        device_scale_factor=2,
        executable_path=EXE,
    )
    pagina = contexto.pages[0]
    await pagina.goto(URL, wait_until="load")
    await pagina.wait_for_timeout(1800)
    await captura(pagina, "20-movil-girar")

    try:
        await pagina.locator("#girar-seguir").click(timeout=4000)
    except Exception:
        # El hit-test de playwright no siempre coopera con capas fijas: se dispara el evento real.
        await pagina.evaluate("() => document.getElementById('girar-seguir').click()")
    await pagina.wait_for_timeout(500)
    await captura(pagina, "21-movil-titulo")

    await pagina.touchscreen.tap(195, 420)
    await pagina.wait_for_timeout(700)
    await captura(pagina, "22-movil-menu")

    x, y = await a_pantalla(pagina, 240, 161)
    await pagina.touchscreen.tap(x, y)
    await pagina.wait_for_timeout(1600)
    await captura(pagina, "23-movil-casa-dialogo")

    for _ in range(4):
        x, y = await a_pantalla(pagina, 240, 230)
        await pagina.touchscreen.tap(x, y)
        await pagina.wait_for_timeout(320)
    await captura(pagina, "24-movil-controles")

    x, y = await a_pantalla(pagina, 54, 224)
    await pagina.mouse.move(x, y)
    await pagina.mouse.down()
    await pagina.wait_for_timeout(1200)
    await pagina.mouse.up()
    await pagina.wait_for_timeout(300)
    await captura(pagina, "25-movil-movimiento")
    await contexto.close()


async def main() -> None:
    async with async_playwright() as p:
        navegador = await p.chromium.launch(executable_path=EXE)
        pagina = await navegador.new_page(viewport={"width": 960, "height": 540})
        pagina.on(
            "console",
            lambda m: MENSAJES.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None,
        )
        pagina.on("pageerror", lambda e: MENSAJES.append(f"[pageerror] {e}"))

        await pagina.goto(URL, wait_until="load")
        await pagina.wait_for_timeout(2000)
        await captura(pagina, "01-titulo")

        await pagina.keyboard.press("z")
        await pagina.wait_for_timeout(600)
        await captura(pagina, "02-menu")

        await pagina.keyboard.press("z")
        await pagina.wait_for_timeout(1400)
        await captura(pagina, "03-casa-despertar")
        await cerrar_dialogo(pagina)

        await usar(pagina, "casa.escritorio")
        await pagina.wait_for_timeout(600)
        await captura(pagina, "05-casa-recuerdo")
        await cerrar_dialogo(pagina)

        await caminar(pagina, "ArrowDown", 1400)
        await captura(pagina, "04-casa-saliendo")

        estado = await pagina.evaluate(
            "() => ({ escena: AG.juego.scene.scenes.filter(s => s.scene.isActive()).map(s => s.scene.key),"
            " flores: AG.Guardado.datos.flores, recuerdos: AG.Guardado.datos.recuerdos })"
        )
        print("  estado:", estado)

        await pagina.evaluate(
            "() => AG.debug.ir('Petalos', { tipo: 'petalos1', volver: 'Floreria', inicio: { x: 7, y: 10 } })"
        )
        await pagina.wait_for_timeout(900)
        await captura(pagina, "06-petalos-intro")
        await pasar_dialogo(pagina, 1, 400)
        await pagina.wait_for_timeout(2500)
        await captura(pagina, "07-petalos-jugando")

        await pagina.evaluate("() => AG.debug.ir('Pueblo', { inicio: { x: 6, y: 10 } })")
        await pagina.wait_for_timeout(1200)
        await captura(pagina, "08-pueblo")
        await cerrar_dialogo(pagina)
        await caminar(pagina, "ArrowDown", 900)
        await caminar(pagina, "ArrowRight", 1500)
        await captura(pagina, "09-pueblo-plaza")
        await usar(pagina, "pueblo.buzon")
        await captura(pagina, "09b-pueblo-buzon")
        await cerrar_dialogo(pagina)

        await pagina.evaluate("() => AG.debug.ir('Floreria')")
        await pagina.wait_for_timeout(1200)
        await captura(pagina, "10-floreria")
        await usar(pagina, "pueblo.floreria.mostrador")
        await captura(pagina, "10b-floreria-mostrador")
        await cerrar_dialogo(pagina)
        await usar(pagina, "pueblo.flora.saludo")
        await captura(pagina, "11-charla-flora")
        await pasar_dialogo(pagina, 6, 300)

        await pagina.evaluate(
            "() => { AG.Guardado.datos.flores = 3;"
            " AG.Guardado.datos.recuerdos = ['r1','r2','r3','r4','r5','r6']; AG.debug.ir('Colina'); }"
        )
        await pagina.wait_for_timeout(1200)
        await captura(pagina, "12-colina")
        await cerrar_dialogo(pagina)
        await caminar(pagina, "ArrowUp", 4000)
        await captura(pagina, "13-colina-arriba")
        await pasar_dialogo(pagina, 2, 500)
        await captura(pagina, "14-colina-alex")

        # Hasta el final: se avanza diálogo hasta que aparezcan los créditos.
        await captura(pagina, "15-colina-recuerdos")
        for paso in range(160):
            await pasar_dialogo(pagina, 1, 200)
            activas = await pagina.evaluate(
                "() => AG.juego.scene.scenes.filter(s => s.scene.isActive()).map(s => s.scene.key)"
            )
            if paso == 26:
                await captura(pagina, "16-colina-mensaje")
            if "Creditos" in activas:
                break
        await captura(pagina, "17-creditos")

        final = await pagina.evaluate(
            "() => ({ activas: AG.juego.scene.scenes.filter(s => s.scene.isActive()).map(s => s.scene.key),"
            " flores: AG.Guardado.datos.flores, terminado: AG.Guardado.datos.terminado })"
        )
        print("  final:", final)
        await captura(pagina, "18-creditos-en-curso")
        await navegador.close()

    async with async_playwright() as p:
        await pasada_movil(p)

    print("\nMensajes de consola:")
    for m in MENSAJES[:40]:
        print("  ", m)
    if not MENSAJES:
        print("   (ninguno)")


asyncio.run(main())
