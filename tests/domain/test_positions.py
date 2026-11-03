from datetime import datetime, timezone

from openmar.domain.model import FishingEvent
from openmar.domain.positions import fishing_zone


def event(lat, lon):
    return FishingEvent("e", "X", "1", datetime(2025, 1, 1, tzinfo=timezone.utc), lat, lon)


def test_zona_de_pesca_es_la_mediana_y_resiste_un_punto_aislado():
    events = [event(-45, -60), event(-46, -61), event(-47, -62), event(10, 10)]

    lat, lon = fishing_zone(events)

    assert lat == -45.5
    assert lon == -60.5


def test_sin_eventos_no_hay_zona():
    assert fishing_zone([]) is None


def test_sin_pesca_usa_los_apagones_como_respaldo():
    from openmar.domain.positions import vessel_position

    position = vessel_position([], [(-44.0, -59.0), (-46.0, -61.0)])

    assert position == (-45.0, -60.0, "apagones")


def test_con_pesca_prefiere_la_zona_de_pesca():
    from openmar.domain.positions import vessel_position

    assert vessel_position([event(-45, -60)], [(-10.0, -10.0)]) == (-45, -60, "pesca")


def test_sin_datos_no_hay_posicion():
    from openmar.domain.positions import vessel_position

    assert vessel_position([], []) is None


def test_grilla_de_pesca_agrupa_eventos_por_celda():
    from openmar.domain.positions import fishing_grid

    events = [event(-45.01, -60.02), event(-45.04, -60.06), event(-46.5, -61.5)]

    cells = fishing_grid(events, size=0.1)

    assert sorted(cells, key=lambda c: c[2]) == [(-46.45, -61.45, 1), (-45.05, -60.05, 2)]
