from datetime import date, datetime, timezone

from openmar.cross import (
    STATUS_NO_TRIP,
    STATUS_UNMATCHED,
    STATUS_WITH_OBSERVER,
    STATUS_WITHOUT_OBSERVER,
    is_near_200nm,
    match_gaps_to_trips,
    summarize_by_vessel,
)
from openmar.sources.gfw import Gap
from openmar.sources.inidep import Trip


def gap(name, day, start_km=100, end_km=100):
    return Gap(
        event_id=f"{name}-{day}",
        vessel_id="v",
        vessel_name=name,
        mmsi="701",
        start=datetime.fromisoformat(f"{day}T10:00:00+00:00"),
        end=datetime.fromisoformat(f"{day}T23:00:00+00:00"),
        hours=13.0,
        start_km_from_shore=start_km,
        end_km_from_shore=end_km,
        lat=-45.0,
        lon=-60.0,
        intentional=True,
    )


def trip(vessel, start, end, observer):
    return Trip(
        vessel=vessel,
        trip=1,
        observer=observer,
        start=date.fromisoformat(start),
        end=date.fromisoformat(end),
        days=10,
        catch_kg=1000,
        rate_t_per_day=1.0,
    )


TRIPS = [
    trip("TAE BAEK 75", "2025-01-04", "2025-01-28", False),
    trip("NANINA", "2025-03-01", "2025-03-20", True),
]


def test_apagon_dentro_de_marea_sin_observador():
    [m] = match_gaps_to_trips([gap("75 TAE BAEK", "2025-01-10")], TRIPS)

    assert m.status == STATUS_WITHOUT_OBSERVER
    assert m.vessel == "TAE BAEK 75"


def test_apagon_dentro_de_marea_con_observador():
    [m] = match_gaps_to_trips([gap("## NANINA ##", "2025-03-05")], TRIPS)

    assert m.status == STATUS_WITH_OBSERVER


def test_tolerancia_de_dias_alrededor_de_la_marea():
    [inside, outside] = match_gaps_to_trips(
        [gap("NANINA", "2025-03-23"), gap("NANINA", "2025-03-25")], TRIPS, tolerance_days=3
    )

    assert inside.status == STATUS_WITH_OBSERVER
    assert outside.status == STATUS_NO_TRIP


def test_buque_sin_mareas_queda_sin_cruce():
    [m] = match_gaps_to_trips([gap("DESCONOCIDO", "2025-01-10")], TRIPS)

    assert m.status == STATUS_UNMATCHED


def test_franja_de_la_milla_200():
    assert is_near_200nm(gap("X", "2025-01-01", start_km=320, end_km=100))
    assert is_near_200nm(gap("X", "2025-01-01", start_km=100, end_km=450))
    assert not is_near_200nm(gap("X", "2025-01-01", start_km=100, end_km=299))


def test_resumen_por_buque_cuenta_estados_y_franja():
    matches = match_gaps_to_trips(
        [
            gap("TAE BAEK 75", "2025-01-10", start_km=350),
            gap("TAE BAEK 75", "2025-01-12"),
            gap("NANINA", "2025-03-05"),
        ],
        TRIPS,
    )

    summary = summarize_by_vessel(matches)

    assert summary["TAE BAEK 75"] == {
        "apagones": 2,
        "franja_milla_200": 1,
        STATUS_WITHOUT_OBSERVER: 2,
        STATUS_WITH_OBSERVER: 0,
        STATUS_NO_TRIP: 0,
        STATUS_UNMATCHED: 0,
    }
    assert summary["NANINA"][STATUS_WITH_OBSERVER] == 1
