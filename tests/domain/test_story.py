from datetime import date

from openmar.domain.model import Coverage, Trip, YearlyCoverage
from openmar.domain.story import coverage_by_year, history_figures, season_figures


def trip(vessel, n, observer=False, catch_kg=1000):
    return Trip(vessel, n, observer, date(2025, 1, 1), date(2025, 1, 20), 20, catch_kg, 1.0)


def test_temporada_cuenta_mareas_con_y_sin_observador_y_buques():
    trips = [
        trip("A", 1, observer=True, catch_kg=2500),
        trip("A", 2),
        trip("B", 1),
        trip("C", 1, observer=True),
    ]

    figures = season_figures(trips)

    assert figures == {
        "mareas": 4,
        "mareas_con_observador": 2,
        "mareas_sin_observador": 2,
        "pct_con_observador": 50.0,
        "buques": 3,
        "buques_con_algun_observador": 2,
        "captura_t": 5.5,
    }


def test_temporada_vacia_no_divide_por_cero():
    assert season_figures([])["pct_con_observador"] == 0.0


def test_historico_cuenta_buques_que_nunca_llevaron_observador():
    coverage = [
        Coverage("A", 20, 0, 20, 0.0),
        Coverage("B", 10, 4, 6, 40.0),
        Coverage("C", 5, 0, 5, 0.0),
    ]

    figures = history_figures(coverage)

    assert figures == {
        "buques": 3,
        "viajes": 35,
        "viajes_con_observador": 4,
        "pct_con_observador": 11.4,
        "buques_nunca_con_observador": 2,
    }


def test_cobertura_por_anio_suma_buques_y_agrega_la_temporada():
    yearly = [
        YearlyCoverage("A", 2021, 1, 3),
        YearlyCoverage("B", 2021, 0, 4),
        YearlyCoverage("A", 2022, 0, 0),
    ]
    season = [trip("A", 1, observer=True), trip("B", 1)]

    series = coverage_by_year(yearly, season, season_year=2025)

    assert series == [
        {"anio": 2021, "viajes": 8, "con_observador": 1, "pct_con_observador": 12.5},
        {"anio": 2022, "viajes": 0, "con_observador": 0, "pct_con_observador": 0.0},
        {"anio": 2025, "viajes": 2, "con_observador": 1, "pct_con_observador": 50.0},
    ]


def test_historico_vacio_no_divide_por_cero():
    assert history_figures([])["pct_con_observador"] == 0.0
