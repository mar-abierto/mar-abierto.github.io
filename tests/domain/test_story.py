from datetime import date

from openmar.domain.model import Coverage, Trip
from openmar.domain.story import history_figures, season_figures


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
