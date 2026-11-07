"""CSV para periodistas: una fila por barco, a partir de site/data/fichas.json."""

import csv
import io
import json

import pytest

from openmar.application.exportar import (
    CSV_NAME,
    PUBLICATION_NAME,
    export_site,
    openmar_version,
    vessel_rows,
    write_csv,
)


def _ficha(name, **datos):
    base = {
        "buque": name,
        "semaforo": "verde",
        "semaforo_texto": "Sin señales",
        "matricula": "0001",
        "armador": "EMPRESA S.A.",
        "mareas_temporada": 4,
        "mareas_con_observador": 1,
        "captura_t": 1200.5,
        "viajes_2021_2024": 10,
        "viajes_con_observador_2021_2024": 2,
        "apagones": 0,
        "franja_milla_200": 0,
        "en_marea_sin_observador": 0,
        "en_marea_con_observador": 0,
        "fuera_de_marea": 0,
        "sin_mareas_del_buque": 0,
        "horas_sin_ais": 0.0,
        "escalas": 3,
        "escalas_exterior": 0,
    }
    base.update(datos)
    return {"id": name, "datos": base, "mareas": []}


FICHAS = {
    "generado": "2026-11-03T23:22:34+00:00",
    "temporada": "Calamar 2025",
    "buques": {
        "ZETA": _ficha("ZETA"),
        "ÑANDÚ 1": _ficha(
            "ÑANDÚ I",
            semaforo="rojo",
            semaforo_texto="Señales repetidas",
            armador="PESQUERA, DEL SUR S.A.",
            apagones=5,
            en_marea_sin_observador=3,
            en_marea_con_observador=1,
            fuera_de_marea=1,
            franja_milla_200=2,
            horas_sin_ais=80.25,
        ),
    },
}


def test_una_fila_por_barco_ordenadas_por_nombre():
    rows = vessel_rows(FICHAS)

    assert len(rows) == 2
    assert [r["barco"] for r in rows] == sorted(r["barco"] for r in rows)


def test_la_fila_trae_viajes_cortes_y_su_desglose():
    row = next(r for r in vessel_rows(FICHAS) if r["barco"] == "ÑANDÚ I")

    assert row["matricula"] == "0001"
    assert row["armador"] == "PESQUERA, DEL SUR S.A."
    assert row["temporada"] == "Calamar 2025"
    assert row["viajes_temporada"] == 4
    assert row["viajes_con_observador"] == 1
    assert row["viajes_sin_observador"] == 3
    assert row["cortes_de_senal"] == 5
    assert row["cortes_en_viaje_sin_observador"] == 3
    assert row["cortes_en_viaje_con_observador"] == 1
    assert row["cortes_fuera_de_viaje"] == 1
    assert row["cortes_cerca_milla_200"] == 2
    assert row["horas_sin_senal"] == 80.25
    assert row["semaforo"] == "rojo"
    assert row["semaforo_texto"] == "Señales repetidas"
    assert "Global Fishing Watch" in row["fuente"]
    assert "INIDEP" in row["fuente"]
    assert "Registro de Flota Pesquera" in row["fuente"]


def test_la_ficha_es_un_link_absoluto_con_el_nombre_codificado():
    row = next(r for r in vessel_rows(FICHAS) if r["barco"] == "ÑANDÚ I")

    assert row["ficha"].startswith("http")
    assert row["ficha"].endswith("buque.html?b=%C3%91AND%C3%9A%20I")


def test_un_dato_faltante_queda_vacio_y_no_rompe():
    fichas = {"temporada": "X", "buques": {"A": {"id": "A", "datos": {"buque": "A"}}}}

    row = vessel_rows(fichas)[0]

    assert row["armador"] == ""
    assert row["viajes_temporada"] == ""
    assert row["viajes_sin_observador"] == ""


def test_sin_buques_es_un_error_claro():
    with pytest.raises(ValueError, match="buques"):
        vessel_rows({"temporada": "X"})


def test_el_csv_lleva_bom_utf8_encabezado_y_comillas_donde_hace_falta(tmp_path):
    target = tmp_path / "buques.csv"

    write_csv(vessel_rows(FICHAS), target)

    raw = target.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    assert "\r\n" in text
    parsed = list(csv.DictReader(io.StringIO(text)))
    nandu = next(r for r in parsed if r["barco"] == "ÑANDÚ I")
    assert nandu["armador"] == "PESQUERA, DEL SUR S.A."
    assert text.splitlines()[0].startswith("barco,matricula,armador")


def test_export_site_escribe_csv_y_datos_de_publicacion(tmp_path):
    (tmp_path / "fichas.json").write_text(json.dumps(FICHAS, ensure_ascii=False), encoding="utf-8")

    stats = export_site(tmp_path, version="9.9.9")

    assert stats == {"barcos": 2, "archivo": str(tmp_path / CSV_NAME)}
    assert (tmp_path / CSV_NAME).exists()
    publication = json.loads((tmp_path / PUBLICATION_NAME).read_text(encoding="utf-8"))
    assert publication == {
        "version": "9.9.9",
        "generado": "2026-11-03T23:22:34+00:00",
        "temporada": "Calamar 2025",
        "csv": CSV_NAME,
        "barcos": 2,
    }


def test_export_site_sin_fichas_avisa(tmp_path):
    with pytest.raises(FileNotFoundError, match="fichas.json"):
        export_site(tmp_path, version="1")


def test_la_version_sale_del_paquete():
    assert openmar_version().count(".") >= 1
