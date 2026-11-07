from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

from openmar.domain.matching import (
    STATUS_NO_TRIP,
    STATUS_UNMATCHED,
    STATUS_WITH_OBSERVER,
    STATUS_WITHOUT_OBSERVER,
    is_near_200nm,
    match_gaps_to_trips,
    summarize_by_vessel,
)
from openmar.domain.model import AisGap as Gap
from openmar.domain.model import Trip


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


def test_usa_la_fecha_argentina_del_apagon_no_la_utc():
    # 2025-01-29 02:00 UTC es 2025-01-28 23:00 en Argentina: último día de la marea.
    late = gap("TAE BAEK 75", "2025-01-29")
    late = late.__class__(**{**late.__dict__, "start": datetime(2025, 1, 29, 2, 0, tzinfo=timezone.utc)})

    [m] = match_gaps_to_trips([late], TRIPS, tolerance_days=0)

    assert m.status == STATUS_WITHOUT_OBSERVER


def test_la_marea_que_contiene_el_dia_gana_a_la_vecina_por_tolerancia():
    trips = [
        trip("NANINA", "2025-01-01", "2025-01-10", False),
        trip("NANINA", "2025-01-12", "2025-01-20", True),
    ]

    [m] = match_gaps_to_trips([gap("NANINA", "2025-01-10")], trips, tolerance_days=3)

    assert m.status == STATUS_WITHOUT_OBSERVER
    assert m.trip.start == date(2025, 1, 1)


def gap_at(name, utc_iso):
    return replace(gap(name, utc_iso[:10]), start=datetime.fromisoformat(utc_iso), event_id=f"{name}-{utc_iso}")


@pytest.mark.parametrize("first_has_observer", [True, False])
def test_dia_compartido_lo_decide_la_hora_del_corte_no_el_observador(first_has_observer):
    # Un viaje termina el 10 y el siguiente sale el 10: el día es de los dos.
    trips = [
        trip("NANINA", "2025-01-01", "2025-01-10", first_has_observer),
        trip("NANINA", "2025-01-10", "2025-01-20", not first_has_observer),
    ]
    morning = gap_at("NANINA", "2025-01-10T11:00:00+00:00")  # 08:00 en Argentina
    evening = gap_at("NANINA", "2025-01-10T23:00:00+00:00")  # 20:00 en Argentina

    m_morning, m_evening = match_gaps_to_trips([morning, evening], trips)

    assert m_morning.trip.start == date(2025, 1, 1)
    assert m_evening.trip.start == date(2025, 1, 10)


def test_empate_por_tolerancia_entre_dos_viajes_tambien_es_neutral():
    trips = [
        trip("NANINA", "2025-01-01", "2025-01-10", True),
        trip("NANINA", "2025-01-14", "2025-01-20", False),
    ]
    morning = gap_at("NANINA", "2025-01-12T11:00:00+00:00")
    evening = gap_at("NANINA", "2025-01-12T23:00:00+00:00")

    m_morning, m_evening = match_gaps_to_trips([morning, evening], trips)

    assert m_morning.status == STATUS_WITH_OBSERVER
    assert m_evening.status == STATUS_WITHOUT_OBSERVER


def test_fuera_de_marea_se_asigna_a_la_mas_cercana():
    trips = [
        trip("NANINA", "2025-01-01", "2025-01-10", False),
        trip("NANINA", "2025-01-14", "2025-01-20", True),
    ]

    [m] = match_gaps_to_trips([gap("NANINA", "2025-01-13")], trips, tolerance_days=3)

    assert m.trip.start == date(2025, 1, 14)
    assert m.status == STATUS_WITH_OBSERVER


def test_distancia_desconocida_no_cuenta_como_franja():
    unknown = gap("X", "2025-01-01")
    unknown = unknown.__class__(**{**unknown.__dict__, "start_km_from_shore": None, "end_km_from_shore": None})

    assert not is_near_200nm(unknown)


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


def test_apagon_sin_nombre_se_identifica_por_mmsi():
    unnamed = gap("", "2025-01-10")

    [m] = match_gaps_to_trips([unnamed], TRIPS, names_by_mmsi={"701": "TAE BAEK 75"})

    assert m.vessel == "TAE BAEK 75"
    assert m.status == STATUS_WITHOUT_OBSERVER
