from datetime import datetime, timezone

from openmar.domain.model import PortVisit
from openmar.domain.port_visits import HOME_COUNTRY, fill_port_names, port_summary


def visit(vessel, port, country, confidence=4, event_id=None):
    when = datetime(2025, 3, 1, tzinfo=timezone.utc)
    return PortVisit(event_id or f"{vessel}-{port}", vessel, "701", when, when, 24.0, port, country, confidence, -38.0, -57.5,
                     port_id=f"{country.lower()}-{port.lower().replace(' ', '')}")


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
        "puertos_exterior": "MONTEVIDEO (URY)",
        "puerto_principal": "MONTEVIDEO",
    }
    assert summary["B"]["escalas_exterior"] == 0
    assert summary["B"]["puertos_exterior"] == ""


def test_resumen_descarta_escalas_de_baja_confianza():
    visits = [visit("A", "MONTEVIDEO", "URY", confidence=2), visit("A", "MAR DEL PLATA", HOME_COUNTRY, confidence=3)]

    summary = port_summary(visits)

    assert summary["A"]["escalas"] == 1
    assert summary["A"]["escalas_exterior"] == 0


def test_resumen_ignora_escalas_sin_puerto_identificado():
    assert port_summary([visit("A", "", "")]) == {}


def test_nombres_faltantes_se_completan_con_el_mismo_puerto_en_otras_escalas():
    named = visit("A", "PUERTO MADRYN", HOME_COUNTRY, event_id="1")
    unnamed = visit("B", "", HOME_COUNTRY, event_id="2")
    unnamed = type(unnamed)(**{**unnamed.__dict__, "port_id": "arg-puertomadryn"})
    unknown = type(unnamed)(**{**unnamed.__dict__, "event_id": "3", "port_id": "arg-raro"})

    filled = fill_port_names([named, unnamed, unknown])

    assert [v.port_name for v in filled] == ["PUERTO MADRYN", "PUERTO MADRYN", "arg-raro"]
