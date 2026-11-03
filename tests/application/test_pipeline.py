"""De bronze a gold y al sitio, con datos mínimos pero con la forma real de cada fuente."""

import json

import pytest

from openmar.adapters.filesystem import LocalRawStore
from openmar.adapters.tabular import read_rows
from openmar.application.download import BRONZE
from openmar.application.gold import build_gold, publish_site
from openmar.application.silver import build_silver

ANEXO = """
Anexo 1. Detalle de las mareas. *Marea con observador a bordo.
 TAE BAEK 75                          1   4/1/2025            28/1/2025    20     420.168    21,01      1
 NANINA                               1*  1/3/2025            20/3/2025    20     400.000    20,00      1
 SIN APAGONES                         1   1/2/2025            20/2/2025    20     300.000    15,00      1
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

VESSELS = [
    {"selfReportedInfo": [{"id": "v1", "shipname": "75 TAE BAEK", "ssvid": "701", "flag": "ARG"}]},
    {"selfReportedInfo": [{"id": "v2", "shipname": "## NANINA ##", "ssvid": "702", "flag": "ARG"}]},
]

EEZ = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"geoname": "Argentinian Exclusive Economic Zone"},
            "geometry": {"type": "Polygon", "coordinates": [[[-70, -55], [-55, -55], [-55, -38], [-70, -38], [-70, -55]]]},
        }
    ],
}


def gap_event(event_id, name, mmsi, start, km=100):
    return {
        "id": event_id,
        "start": start,
        "end": start,
        "position": {"lat": -45.0, "lon": -60.0},
        "distances": {"startDistanceFromShoreKm": km, "endDistanceFromShoreKm": 100},
        "vessel": {"id": "v", "name": name, "ssvid": mmsi},
        "gap": {"durationHours": 13.0, "intentionalDisabling": True},
    }


def fishing_event(event_id, name, mmsi, lat, lon):
    return {"id": event_id, "start": "2025-01-10T00:00:00Z", "position": {"lat": lat, "lon": lon},
            "vessel": {"name": name, "ssvid": mmsi}}


@pytest.fixture
def bronze(tmp_path):
    store = LocalRawStore(tmp_path / "bronze")
    store.save(BRONZE["inidep_trips"], ANEXO, source="test")
    store.save(BRONZE["inidep_coverage"], TABLA_9, source="test")
    store.save(BRONZE["registry"], REGISTRO, source="test")
    store.save(BRONZE["gfw_vessels"], json.dumps(VESSELS), source="test")
    gaps = [
        gap_event("g1", "75 TAE BAEK", "701", "2025-01-10T10:00:00Z", km=350),
        gap_event("g2", "", "701", "2025-01-12T10:00:00Z"),  # sin nombre: se resuelve por MMSI
        gap_event("g3", "", "701", "2025-01-14T10:00:00Z"),
        gap_event("g4", "## NANINA ##", "702", "2025-03-05T10:00:00Z"),
    ]
    store.save(BRONZE["gfw_gaps"], json.dumps(gaps), source="test")
    fishing = [fishing_event("f1", "75 TAE BAEK", "701", -45, -60), fishing_event("f2", "", "702", -46, -61)]
    store.save(BRONZE["gfw_fishing"], json.dumps(fishing), source="test")
    store.save(BRONZE["eez"], json.dumps(EEZ), source="test")
    return store


def test_silver_unifica_nombres_y_resuelve_por_mmsi(bronze, tmp_path):
    counts = build_silver(bronze, tmp_path / "silver")

    assert counts["mareas"] == 3
    gaps = read_rows(tmp_path / "silver" / "apagones.csv")
    assert [g["vessel_name"] for g in gaps] == ["TAE BAEK 75", "TAE BAEK 75", "TAE BAEK 75", "NANINA"]
    fishing = read_rows(tmp_path / "silver" / "pesca.csv")
    assert fishing[1]["vessel_name"] == "NANINA"


def test_gold_arma_semaforo_ficha_y_capas_del_mapa(bronze, tmp_path):
    build_silver(bronze, tmp_path / "silver")

    summary = build_gold(tmp_path / "silver", tmp_path / "gold")

    rows = {r["buque"]: r for r in read_rows(tmp_path / "gold" / "apagones-por-buque.csv")}
    tae = rows["TAE BAEK 75"]
    assert tae["semaforo"] == "rojo"
    assert tae["armador"] == "ILLEX FISHING S.A."
    assert tae["apagones"] == "3"
    assert tae["franja_milla_200"] == "1"
    assert tae["viajes_con_observador_2021_2024"] == "0"
    assert rows["NANINA"]["semaforo"] == "amarillo"
    assert rows["SIN APAGONES"]["semaforo"] == "verde"
    assert summary["por_color"] == {"verde": 1, "amarillo": 1, "rojo": 1}

    buques = json.loads((tmp_path / "gold" / "mapa" / "buques.geojson").read_text())
    assert {f["properties"]["buque"] for f in buques["features"]} == {"TAE BAEK 75", "NANINA"}
    assert summary["buques_en_mapa"] == 2
    assert [v["buque"] for v in summary["sin_posicion"]] == ["SIN APAGONES"]
    assert summary["sin_armador"] == ["NANINA", "SIN APAGONES"]
    relato = summary["relato"]
    assert relato["temporada"]["mareas"] == 3
    assert relato["temporada"]["mareas_con_observador"] == 1
    assert relato["historico_2021_2024"]["buques_nunca_con_observador"] == 1
    assert relato["horas_sin_ais"] == 52.0
    assert relato["apagones_por_marea"] == {"sin_observador": 1.5, "con_observador": 1.0}
    assert [v["buque"] for v in relato["senales_repetidas"]] == ["TAE BAEK 75"]
    zee = json.loads((tmp_path / "gold" / "mapa" / "zee.geojson").read_text())
    assert zee["features"][0]["properties"]["nombre"] == "Argentinian Exclusive Economic Zone"


def test_publicar_copia_las_capas_al_sitio(bronze, tmp_path):
    build_silver(bronze, tmp_path / "silver")
    build_gold(tmp_path / "silver", tmp_path / "gold")

    copied = publish_site(tmp_path / "gold", tmp_path / "site" / "data")

    assert sorted(p.name for p in copied) == [
        "apagones.geojson", "buques.geojson", "pesca.geojson", "resumen.json", "zee.geojson",
    ]


def test_publicar_borra_capas_viejas(bronze, tmp_path):
    build_silver(bronze, tmp_path / "silver")
    build_gold(tmp_path / "silver", tmp_path / "gold")
    site = tmp_path / "site" / "data"
    site.mkdir(parents=True)
    (site / "vieja.geojson").write_text("{}")

    publish_site(tmp_path / "gold", site)

    assert not (site / "vieja.geojson").exists()
