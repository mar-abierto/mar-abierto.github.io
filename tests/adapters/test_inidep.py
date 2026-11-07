import subprocess
from datetime import date

import pytest

from openmar.adapters.inidep import (
    parse_observer_coverage,
    parse_observer_coverage_by_year,
    parse_trips_annex,
    pdf_to_text,
)

ANEXO = """
Texto previo con 12/1/2025 y números 1 2 3 que no es el anexo.

Anexo 1. Illex argentinus. Temporada 2025. Detalle de las mareas realizadas por la flota potera según
la información proveniente de los partes de pesca semanales y finales (PF). *Marea con observador a
bordo.

                                              PRIMER          ÚLTIMO
            BUQUE                  VIAJE         DÍA            DATO      DÍAS   CAPTURA    REND.       PF
                                               PESCA           PESCA                (kg)    (t día-1)
 ARBUMASA XXVIII                       1      12/1/2025       26/1/2025    15     573.949    38,26      1
                                      2*      31/1/2025       22/2/2025    21     613.615    29,22      1
                                       5       3/5/2025        2/6/2025    29     511.369    17,63
 DON LUIS I                           1*      12/1/2025        1/2/2025    21     638.508    30,41      1
 TAE BAEK 75                          1   4/1/2025            28/1/2025    20     420.168    21,01      1
"""

TABLA_9 = """
Tabla 9. Designación de observadores del INIDEP en buques poteros. Periodo 2021-2024 y valores totales del
periodo. Buque, año, número de viajes con (C) y sin (S) observador a bordo.
                                 2021          2022          2023           2024         TOTAL 4 años     TOTAL (%)
          BUQUE
                                C S          C    S        C     S        C     S    C      S     Total    C      S
 ARBUMASA XXVIII                      4             5               6            5   0      20     20     0.0    100.0
 NATALIA                        2     1      1      1      2        3     2      2   7      7      14     50.0   50.0
Observadores del INIDEP en la pesquería del calamar argentino, temporada 2024.
                                                               19
 TAE BAEK 75                          4             6              6             5     0      21     21     0.0   100.0
                                    246     12     301     18     331    19      284   62    1162   1224    5.1   94.9
           TOTAL                3
Texto posterior.
 OTRO BUQUE                     1     1      1      1      1        1     1      1   4      4      8      50.0   50.0
"""


def test_anexo_lee_cada_marea_y_hereda_el_nombre_del_buque():
    trips = parse_trips_annex(ANEXO)

    assert [(t.vessel, t.trip) for t in trips] == [
        ("ARBUMASA XXVIII", 1),
        ("ARBUMASA XXVIII", 2),
        ("ARBUMASA XXVIII", 5),
        ("DON LUIS I", 1),
        ("TAE BAEK 75", 1),
    ]


def test_anexo_marca_mareas_con_observador_por_el_asterisco():
    trips = parse_trips_annex(ANEXO)

    assert [t.observer for t in trips] == [False, True, False, True, False]


def test_anexo_convierte_fechas_captura_y_rendimiento():
    first = parse_trips_annex(ANEXO)[0]

    assert first.start == date(2025, 1, 12)
    assert first.end == date(2025, 1, 26)
    assert first.days == 15
    assert first.catch_kg == 573_949
    assert first.rate_t_per_day == 38.26


def test_anexo_descarta_filas_sin_buque_conocido():
    text = "Anexo 1.\n                                      2*      31/1/2025       22/2/2025    21     613.615    29,22      1\n"

    assert parse_trips_annex(text) == []


HEADER = """
                                              PRIMER          ÚLTIMO
            BUQUE                  VIAJE         DÍA            DATO      DÍAS   CAPTURA    REND.       PF
                                               PESCA           PESCA                (kg)    (t día-1)
"""
ROW_NANINA_1 = " NANINA                                1      12/1/2025        2/2/2025    22     680.592    30,94      1"
ROW_CONT_2 = "                                       2       7/2/2025        9/2/2025     3     107.328    35,78      1"
ROW_CONT_1 = "                                       1       7/2/2025        9/2/2025     3     107.328    35,78      1"


def test_anexo_termina_en_el_anexo_2():
    text = f"Anexo 1.{HEADER}{ROW_NANINA_1}\n\nAnexo 2. Longitudes\n{ROW_CONT_2}\n"

    assert [(t.vessel, t.trip) for t in parse_trips_annex(text)] == [("NANINA", 1)]


def test_anexo_termina_en_la_fila_de_totales_y_la_valida():
    text = f"Anexo 1.{HEADER}{ROW_NANINA_1}\n{ROW_CONT_2}\n\n      1 barcos       2        02/01   05/06   25  787.920  20,74  2\n{ROW_CONT_2}\n"

    assert [(t.vessel, t.trip) for t in parse_trips_annex(text)] == [("NANINA", 1), ("NANINA", 2)]


def test_anexo_falla_si_las_mareas_no_suman_el_total_declarado():
    text = f"Anexo 1.{HEADER}{ROW_NANINA_1}\n\n      1 barcos       5        02/01   05/06   25  787.920  20,74  2\n"

    with pytest.raises(ValueError, match="1 mareas.*declara 5"):
        parse_trips_annex(text)


def test_anexo_no_arrastra_el_buque_a_traves_de_un_encabezado_nuevo():
    # Tras un salto de página el PDF repite el nombre: una fila sin nombre allí no se adivina.
    text = f"Anexo 1.{HEADER}{ROW_NANINA_1}\n\n  16\n{HEADER}{ROW_CONT_2}\n"

    assert [(t.vessel, t.trip) for t in parse_trips_annex(text)] == [("NANINA", 1)]


def test_anexo_falla_si_una_fila_sin_nombre_no_sigue_la_numeracion_del_buque():
    text = f"Anexo 1.{HEADER}{ROW_NANINA_1}\n{ROW_CONT_1}\n"

    with pytest.raises(ValueError, match="NANINA"):
        parse_trips_annex(text)


def test_pdf_to_text_rechaza_archivos_que_no_son_pdf(tmp_path):
    fake = tmp_path / "x.pdf"
    fake.write_bytes(b"<html>no soy un pdf</html>")

    with pytest.raises(RuntimeError, match="no es un PDF"):
        pdf_to_text(fake)


@pytest.fixture
def fake_pdf(tmp_path):
    path = tmp_path / "informe.pdf"
    path.write_bytes(b"%PDF-1.7\n")
    return path


def test_pdf_to_text_decodifica_en_utf_8(fake_pdf, monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 0, stdout="ÚLTIMO DÍA", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert pdf_to_text(fake_pdf) == "ÚLTIMO DÍA"
    [(cmd, kwargs)] = calls
    assert cmd[:4] == ["pdftotext", "-layout", "-enc", "UTF-8"]
    assert kwargs["encoding"] == "utf-8"


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (FileNotFoundError("pdftotext"), "Falta pdftotext"),
        (subprocess.CalledProcessError(1, "pdftotext"), "no pudo leer"),
        (subprocess.TimeoutExpired("pdftotext", 120), "no pudo leer"),
    ],
    ids=["sin-poppler", "falla", "timeout"],
)
def test_pdf_to_text_traduce_los_errores_de_pdftotext(fake_pdf, monkeypatch, error, message):
    def fake_run(cmd, **kwargs):
        raise error

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match=message):
        pdf_to_text(fake_pdf)


def test_anexo_ignora_texto_antes_del_titulo():
    assert parse_trips_annex("sin anexo 12/1/2025 1 2") == []


def test_tabla_9_lee_totales_por_buque_y_corta_en_total():
    rows = parse_observer_coverage(TABLA_9)

    assert [(r.vessel, r.trips, r.with_observer, r.without_observer, r.pct_with_observer) for r in rows] == [
        ("ARBUMASA XXVIII", 20, 0, 20, 0.0),
        ("NATALIA", 14, 7, 7, 50.0),
        ("TAE BAEK 75", 21, 0, 21, 0.0),
    ]


def test_tabla_9_sin_titulo_devuelve_vacio():
    assert parse_observer_coverage("nada") == []


def test_tabla_9_lee_cada_anio_por_posicion_de_columna():
    rows = parse_observer_coverage_by_year(TABLA_9)

    natalia = [(r.year, r.with_observer, r.without_observer) for r in rows if r.vessel == "NATALIA"]
    assert natalia == [(2021, 2, 1), (2022, 1, 1), (2023, 2, 3), (2024, 2, 2)]
    tae = [(r.year, r.with_observer, r.without_observer) for r in rows if r.vessel == "TAE BAEK 75"]
    assert tae == [(2021, 0, 4), (2022, 0, 6), (2023, 0, 6), (2024, 0, 5)]
    assert len(rows) == 12


def test_tabla_9_por_anio_falla_si_los_anios_no_suman_el_total():
    roto = TABLA_9.replace("2     1      1      1      2        3     2      2   7", "2     1      1      1      2        3     2      9   7")

    with pytest.raises(ValueError, match="NATALIA"):
        parse_observer_coverage_by_year(roto)


def test_tabla_9_por_anio_sin_titulo_devuelve_vacio():
    assert parse_observer_coverage_by_year("nada") == []


def test_tabla_9_por_anio_falla_sin_encabezado_de_columnas():
    sin_encabezado = "Tabla 9.\n TAE BAEK 75        4     6     6     5     0      21     21     0.0   100.0\n"

    with pytest.raises(ValueError, match="encabezado"):
        parse_observer_coverage_by_year(sin_encabezado)
