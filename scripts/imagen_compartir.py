"""Genera site/img/compartir.png (1200×630), la imagen para compartir en redes.

Es la única pieza del sitio con cifras "horneadas": salen de site/data/resumen.json
y site/data/fichas.json en el momento de correr el script. Si cambian los datos,
hay que regenerarla:

    uv run --with playwright python scripts/imagen_compartir.py

La primera vez puede hacer falta `uv run --with playwright playwright install chromium`.
Necesita red para bajar las tipografías de Google Fonts (las mismas del sitio).
"""

import argparse
import html
import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 1200, 630
MONTHS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre")


def long_date(day: date) -> str:
    return f"{day.day} de {MONTHS[day.month - 1]} de {day.year}"


def figures(site_data: Path) -> dict:
    summary = json.loads((site_data / "resumen.json").read_text(encoding="utf-8"))
    fichas = json.loads((site_data / "fichas.json").read_text(encoding="utf-8"))
    season = summary["relato"]["temporada"]
    trips, observed = int(season["mareas"]), int(season["mareas_con_observador"])
    last_trip = max(m["fin"] for v in fichas["buques"].values() for m in v.get("mareas", []))
    return {
        "temporada": summary["temporada"],
        "viajes": trips,
        "con_observador": observed,
        "uno_de_cada": round(trips / observed),
        "corte": long_date(date.fromisoformat(last_trip)),
        "generado": datetime.fromisoformat(summary["generado"]).date(),
    }


def page(f: dict) -> str:
    cells = "".join(
        f'<i class="{"on" if i < f["con_observador"] else ""}"></i>' for i in range(f["viajes"])
    )
    season = html.escape(f["temporada"])
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=block" rel="stylesheet">
<style>
  :root {{ --ink:#15191f; --ink-2:#353d48; --ink-3:#5a6370; --zee:#1d5fa6; --off:#d9dde2; --line:rgba(20,28,40,.14); }}
  * {{ box-sizing:border-box; margin:0; }}
  html, body {{ width:{WIDTH}px; height:{HEIGHT}px; background:#fff; color:var(--ink); }}
  body {{ display:grid; grid-template-rows:auto 1fr auto; padding:52px 64px 44px;
         font-family:"Libre Franklin", Arial, sans-serif; border-top:8px solid var(--ink); }}
  header {{ display:flex; justify-content:space-between; align-items:baseline;
           padding-bottom:18px; border-bottom:1px solid var(--line); }}
  .brand {{ font:800 30px/1 "Libre Franklin"; letter-spacing:-.02em; }}
  .brand span {{ font-weight:400; }}
  .kicker {{ font:600 17px/1 "Libre Franklin"; color:var(--ink-3); }}
  main {{ display:grid; grid-template-columns:1fr 452px; gap:56px; align-items:center; }}
  h1 {{ font:700 54px/1.06 "Libre Franklin"; letter-spacing:-.02em; text-wrap:balance; }}
  h1 b {{ color:var(--zee); font-weight:800; white-space:nowrap; }}
  p.lede {{ margin-top:22px; font:400 23px/1.4 "Source Serif 4", Georgia, serif; color:var(--ink-2); }}
  .waffle {{ display:grid; grid-template-columns:repeat(24, 14px); gap:5px; }}
  .waffle i {{ display:block; width:14px; height:14px; border-radius:3px; background:var(--off); }}
  .waffle i.on {{ background:var(--zee); }}
  .legend {{ margin-top:14px; font:400 15px/1.35 "Libre Franklin"; color:var(--ink-3); }}
  .legend em {{ font-style:normal; color:var(--zee); font-weight:600; }}
  footer {{ padding-top:16px; border-top:1px solid var(--line); font:400 15px/1.3 "Libre Franklin"; color:var(--ink-3); }}
</style></head><body>
<header><div class="brand">open<span>Mar</span></div><div class="kicker">Flota con bandera argentina · {season}</div></header>
<main>
  <div>
    <h1>Sólo <b>1 de cada {f["uno_de_cada"]}</b> viajes llevó un observador del Estado a bordo.</h1>
    <p class="lede">Adentro de la milla 200 el Estado puede controlar. En {f["viajes"]} viajes de pesca, hubo alguien a bordo en {f["con_observador"]}.</p>
  </div>
  <figure>
    <div class="waffle" aria-hidden="true">{cells}</div>
    <figcaption class="legend">Cada cuadrado es un viaje. <em>En azul</em>, los que llevaron observador.</figcaption>
  </figure>
</main>
<footer>Fuente: INIDEP, viajes hasta el {f["corte"]}. Datos generados el {f["generado"].strftime("%d/%m/%Y")}.</footer>
</body></html>"""


def render(markup: str, target: Path) -> None:
    from playwright.sync_api import sync_playwright

    target.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        tab = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
        tab.set_content(markup, wait_until="networkidle")
        tab.evaluate("document.fonts.ready")
        tab.screenshot(path=str(target), clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT})
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--datos", type=Path, default=ROOT / "site" / "data")
    parser.add_argument("--salida", type=Path, default=ROOT / "site" / "img" / "compartir.png")
    parser.add_argument("--html", type=Path, help="guarda también el HTML intermedio, para revisarlo")
    args = parser.parse_args()
    f = figures(args.datos)
    markup = page(f)
    if args.html:
        args.html.write_text(markup, encoding="utf-8")
    render(markup, args.salida)
    print(f"{args.salida} · 1 de cada {f['uno_de_cada']} · {args.salida.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
