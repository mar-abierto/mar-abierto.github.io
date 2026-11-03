import csv
import json

from openmar.pipeline import build_outputs

ANEXO = """
Anexo 1. Detalle de las mareas. *Marea con observador a bordo.
 TAE BAEK 75                          1   4/1/2025            28/1/2025    20     420.168    21,01      1
 NANINA                               1*  1/3/2025            20/3/2025    20     400.000    20,00      1
"""

TABLA_9 = """
Tabla 9. Designación de observadores.
 TAE BAEK 75                          4             6              6             5     0      21     21     0.0   100.0
           TOTAL                3
"""

REGISTRO = """<table>
<tr><th>Nombre</th></tr>
<tr><td>Nº 75 TAE BAEK</td><td>2364</td><td>POTEROS / 60</td><td>CONGELADOR</td><td>ILLEX FISHING S.A.</td>
<td>Res.514/09</td><td>01/09/2024</td><td>CALAMAR</td><td></td><td></td><td></td></tr>
</table>"""


def gap_event(event_id, name, day, km=100):
    return {
        "id": event_id,
        "start": f"{day}T10:00:00.000Z",
        "end": f"{day}T23:00:00.000Z",
        "position": {"lat": -45.0, "lon": -60.0},
        "distances": {"startDistanceFromShoreKm": km, "endDistanceFromShoreKm": 100},
        "vessel": {"id": "v", "name": name, "ssvid": "701"},
        "gap": {"durationHours": 13.0, "intentionalDisabling": True},
    }


def write_raw(raw):
    (raw / "inidep").mkdir(parents=True)
    (raw / "inidep" / "ito-026-2025.txt").write_text(ANEXO)
    (raw / "inidep" / "observadores-2024.txt").write_text(TABLA_9)
    (raw / "rfp").mkdir()
    (raw / "rfp" / "datos-de-pesca.html").write_text(REGISTRO)
    (raw / "gfw").mkdir()
    events = [
        gap_event("g1", "75 TAE BAEK", "2025-01-10", km=350),
        gap_event("g2", "## NANINA ##", "2025-03-05"),
    ]
    (raw / "gfw" / "apagones.json").write_text(json.dumps(events))


def read_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def test_build_outputs_genera_la_ficha_resumen_por_buque(tmp_path):
    raw, out = tmp_path / "raw", tmp_path / "processed"
    write_raw(raw)

    stats = build_outputs(raw, out)

    rows = {r["buque"]: r for r in read_csv(out / "apagones-por-buque.csv")}
    tae = rows["TAE BAEK 75"]
    assert tae["armador"] == "ILLEX FISHING S.A."
    assert tae["matricula"] == "2364"
    assert tae["apagones"] == "1"
    assert tae["franja_milla_200"] == "1"
    assert tae["en_marea_sin_observador"] == "1"
    assert tae["viajes_2021_2024"] == "21"
    assert tae["viajes_con_observador_2021_2024"] == "0"
    assert rows["NANINA"]["en_marea_con_observador"] == "1"
    assert rows["NANINA"]["armador"] == ""
    assert stats["apagones"] == 2


def test_build_outputs_exporta_mareas_y_detalle_de_apagones(tmp_path):
    raw, out = tmp_path / "raw", tmp_path / "processed"
    write_raw(raw)

    build_outputs(raw, out)

    assert len(read_csv(out / "mareas.csv")) == 2
    detail = read_csv(out / "apagones-detalle.csv")
    assert [d["estado"] for d in detail] == ["en_marea_sin_observador", "en_marea_con_observador"]
