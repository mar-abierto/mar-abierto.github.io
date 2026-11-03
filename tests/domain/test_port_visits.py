import dataclasses
from datetime import datetime, timezone

from openmar.domain.model import PortVisit
from openmar.domain.port_visits import (
    HOME_COUNTRY,
    arrivals_in_year,
    fill_port_names,
    port_summary,
    visit_quality,
)

MARCH = datetime(2025, 3, 1, tzinfo=timezone.utc)


def visit(vessel, port, country, confidence=4, event_id=None, when=MARCH, port_id=None):
    return PortVisit(
        event_id or f"{vessel}-{port}", vessel, "701", when, when, 24.0, port, country, confidence, -38.0, -57.5,
        port_id=port_id if port_id is not None else f"{country.lower()}-{port.lower().replace(' ', '')}",
    )


def test_resumen_cuenta_escalas_por_buque_y_separa_las_del_exterior():
    visits = [
        visit("A", "MAR DEL PLATA", HOME_COUNTRY, event_id="1"),
        visit("A", "MONTEVIDEO", "URY", event_id="2"),
        visit("A", "MONTEVIDEO", "URY", event_id="3"),
        visit("B", "PUERTO MADRYN", HOME_COUNTRY),
    ]

    summary = port_summary(visits)

    assert summary["A"] == {
        "escalas": 3,
        "escalas_exterior": 2,
        "escalas_pais_desconocido": 0,
        "puertos_exterior": "MONTEVIDEO (URY)",
        "puerto_principal": "MONTEVIDEO",
    }
    assert summary["B"]["escalas_exterior"] == 0
    assert summary["B"]["puertos_exterior"] == ""


def test_resumen_une_las_distintas_grafias_del_mismo_buque():
    visits = [
        visit("75 TAE BAEK", "MAR DEL PLATA", HOME_COUNTRY, event_id="1"),
        visit("TAE BAEK 75", "PUERTO MADRYN", HOME_COUNTRY, event_id="2"),
    ]

    summary = port_summary(visits)

    assert list(summary) == ["TAE BAEK 75"]
    assert summary["TAE BAEK 75"]["escalas"] == 2


def test_pais_desconocido_no_cuenta_como_exterior():
    summary = port_summary([visit("A", "PUERTO X", "")])

    assert summary["A"]["escalas_exterior"] == 0
    assert summary["A"]["escalas_pais_desconocido"] == 1


def test_resumen_descarta_escalas_de_baja_confianza():
    visits = [visit("A", "MONTEVIDEO", "URY", confidence=2), visit("A", "MAR DEL PLATA", HOME_COUNTRY, confidence=3)]

    summary = port_summary(visits)

    assert summary["A"]["escalas"] == 1
    assert summary["A"]["escalas_exterior"] == 0


def test_resumen_ignora_escalas_sin_puerto_identificado():
    assert port_summary([visit("A", "", "")]) == {}


def test_llegadas_del_anio_usan_la_fecha_argentina():
    late_2024 = visit("A", "MAR DEL PLATA", HOME_COUNTRY, event_id="1", when=datetime(2024, 6, 10, tzinfo=timezone.utc))
    new_year_utc = visit("A", "MAR DEL PLATA", HOME_COUNTRY, event_id="2", when=datetime(2025, 1, 1, 2, tzinfo=timezone.utc))
    march = visit("A", "MAR DEL PLATA", HOME_COUNTRY, event_id="3")

    assert [v.event_id for v in arrivals_in_year([late_2024, new_year_utc, march], 2025)] == ["3"]


def test_nombres_faltantes_se_completan_y_quedan_marcados():
    named = visit("A", "PUERTO MADRYN", HOME_COUNTRY, event_id="1")
    unnamed = visit("B", "", HOME_COUNTRY, event_id="2", port_id="arg-puertomadryn")
    unknown = visit("B", "", HOME_COUNTRY, event_id="3", port_id="arg-raro")

    filled = fill_port_names([named, unnamed, unknown])

    assert [v.port_name for v in filled] == ["PUERTO MADRYN", "PUERTO MADRYN", "Puerto sin nombre (arg-raro)"]
    assert [v.port_name_inferred for v in filled] == [False, True, True]


def test_calidad_cuenta_lo_que_queda_afuera_del_indicador():
    visits = [
        visit("A", "MAR DEL PLATA", HOME_COUNTRY, event_id="ok"),
        visit("A", "MAR DEL PLATA", HOME_COUNTRY, event_id="viejo", when=datetime(2024, 6, 1, tzinfo=timezone.utc)),
        visit("A", "MONTEVIDEO", "URY", event_id="dudosa", confidence=2),
        visit("A", "", "", event_id="sin-puerto"),
        visit("A", "PUERTO X", "", event_id="sin-pais"),
        dataclasses.replace(visit("A", "PUERTO MADRYN", HOME_COUNTRY, event_id="inferido"), port_name_inferred=True),
    ]

    assert visit_quality(visits, 2025) == {
        "descargadas": 6,
        "de_otros_anios": 1,
        "baja_confianza": 1,
        "sin_puerto": 1,
        "pais_desconocido": 1,
        "nombre_completado": 1,
        "contadas": 3,
    }
