from openmar.domain.dashboard import by_owner, port_ranking
from openmar.domain.model import PortVisit
from datetime import datetime, timezone


def row(buque, armador, semaforo="verde", mareas=2, con_obs=0, apagones=0, sin_obs=0, escalas=1, exterior=0):
    return {
        "buque": buque, "armador": armador, "semaforo": semaforo, "mareas_temporada": mareas,
        "mareas_con_observador": con_obs, "apagones": apagones, "en_marea_sin_observador": sin_obs,
        "escalas": escalas, "escalas_exterior": exterior, "captura_t": 10.0,
    }


def test_por_armador_suma_buques_y_ordena_por_mareas():
    rows = [
        row("A1", "UNO S.A.", semaforo="rojo", mareas=5, con_obs=1, apagones=4, sin_obs=3, escalas=3, exterior=2),
        row("A2", "UNO S.A.", mareas=3),
        row("B1", "DOS S.A.", mareas=2, con_obs=2),
        row("C1", "", mareas=1),
    ]

    owners = by_owner(rows)

    assert owners[0] == {
        "armador": "UNO S.A.", "buques": 2, "mareas": 8, "mareas_con_observador": 1, "pct_con_observador": 12.5,
        "apagones": 4, "apagones_sin_observador": 3, "escalas": 4, "escalas_exterior": 2,
        "buques_senales_repetidas": 1, "captura_t": 20.0,
    }
    assert [o["armador"] for o in owners] == ["UNO S.A.", "DOS S.A.", "Sin armador en el registro"]


def test_ranking_de_puertos_cuenta_escalas_y_buques():
    when = datetime(2025, 3, 1, tzinfo=timezone.utc)

    def v(vessel, port, country, confidence=4):
        return PortVisit(f"{vessel}{port}{confidence}", vessel, "", when, when, 1.0, port, country, confidence, 0.0, 0.0, "")

    visits = [v("A", "MONTEVIDEO", "URY"), v("B", "MONTEVIDEO", "URY"), v("A", "MAR DEL PLATA", "ARG"),
              v("C", "PUNTA ARENAS", "CHL", confidence=2)]

    assert port_ranking(visits, foreign_only=True) == [{"puerto": "MONTEVIDEO", "pais": "URY", "escalas": 2, "buques": 2}]
    assert [p["puerto"] for p in port_ranking(visits)] == ["MONTEVIDEO", "MAR DEL PLATA"]


def test_por_armador_sin_mareas_no_divide_por_cero_y_acepta_celdas_vacias():
    owners = by_owner([row("X1", "TRES S.A.", mareas=0, escalas="", exterior="")])

    assert owners[0]["pct_con_observador"] == 0.0
    assert owners[0]["escalas"] == 0


def test_ranking_exterior_no_incluye_pais_desconocido():
    when = datetime(2025, 3, 1, tzinfo=timezone.utc)
    unknown = PortVisit("u", "A", "", when, when, 1.0, "PUERTO X", "", 4, 0.0, 0.0, "")

    assert port_ranking([unknown], foreign_only=True) == []
