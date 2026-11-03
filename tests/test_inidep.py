from datetime import date

from openmar.sources.inidep import parse_observer_coverage, parse_trips_annex

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


def test_pdf_to_text_rechaza_archivos_que_no_son_pdf(tmp_path):
    from openmar.sources.inidep import pdf_to_text

    fake = tmp_path / "x.pdf"
    fake.write_bytes(b"<html>no soy un pdf</html>")

    import pytest

    with pytest.raises(RuntimeError, match="no es un PDF"):
        pdf_to_text(fake)


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
