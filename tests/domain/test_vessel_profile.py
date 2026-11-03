from datetime import date, datetime, timezone

from openmar.domain.matching import STATUS_WITH_OBSERVER, STATUS_WITHOUT_OBSERVER
from openmar.domain.model import PortVisit, Trip, YearlyCoverage
from openmar.domain.vessel_profile import comparison, gap_rows, profile, trip_rows, visit_rows


def trip(n, observer=False, vessel="A"):
    return Trip(vessel, n, observer, date(2025, 1, n * 10), date(2025, 1, n * 10 + 5), 6, 120_000, 20.0)


def gap(marea, estado=STATUS_WITHOUT_OBSERVER, fecha="2025-01-12", buque="A"):
    return {
        "buque": buque, "fecha_local": fecha, "horas": 14.5, "estado": estado, "marea": marea,
        "franja_milla_200": False, "km_costa_inicio": 210.0, "km_costa_fin": 180.0, "lat": -45.0, "lon": -60.0,
    }


def port(when, name="MAR DEL PLATA", country="ARG", confidence=4, vessel="A"):
    return PortVisit(f"{name}-{when}", vessel, "701", when, when, 30.0, name, country, confidence, -38.0, -57.5, "x")


def test_cada_marea_lleva_sus_apagones():
    rows = trip_rows([trip(2), trip(1, observer=True)], [gap(1, STATUS_WITH_OBSERVER), gap(2), gap(2), gap("")])

    assert [r["marea"] for r in rows] == [1, 2]
    assert rows[0] == {
        "marea": 1, "inicio": "2025-01-10", "fin": "2025-01-15", "dias": 6,
        "observador": True, "captura_t": 120.0, "apagones": 1,
    }
    assert rows[1]["apagones"] == 2


def test_apagones_ordenados_por_fecha_sin_coordenadas():
    rows = gap_rows([gap(2, fecha="2025-03-01"), gap(1, fecha="2025-01-05")])

    assert [r["fecha_local"] for r in rows] == ["2025-01-05", "2025-03-01"]
    assert "lat" not in rows[0] and "buque" not in rows[0]


def test_escalas_cuentan_solo_las_confiables_en_orden_y_marcan_el_exterior():
    visits = [
        port(datetime(2025, 4, 1, 12, tzinfo=timezone.utc), "MONTEVIDEO", "URY"),
        port(datetime(2025, 2, 1, 12, tzinfo=timezone.utc)),
        port(datetime(2025, 3, 1, 12, tzinfo=timezone.utc), confidence=2),
        port(datetime(2025, 1, 1, 1, tzinfo=timezone.utc)),
    ]

    rows = visit_rows(visits)

    assert [r["llegada"] for r in rows] == ["2024-12-31", "2025-02-01", "2025-04-01"]
    assert rows[-1] == {
        "llegada": "2025-04-01", "puerto": "MONTEVIDEO", "pais": "URY", "exterior": True,
        "horas": 30.0, "nombre_completado": False,
    }
    assert rows[0]["exterior"] is False


def test_comparacion_con_la_flota():
    row = {"mareas_temporada": 4, "mareas_con_observador": 1, "apagones": 6}
    fleet = {"mareas": 100, "mareas_con_observador": 5, "apagones": 50}

    assert comparison(row, fleet) == {
        "pct_con_observador": 25.0, "pct_con_observador_flota": 5.0,
        "apagones_por_marea": 1.5, "apagones_por_marea_flota": 0.5,
    }


def test_comparacion_sin_mareas_no_divide_por_cero():
    result = comparison({"mareas_temporada": 0, "mareas_con_observador": 0, "apagones": 2}, {"mareas": 0, "mareas_con_observador": 0, "apagones": 0})

    assert result["pct_con_observador"] is None
    assert result["apagones_por_marea"] is None


def test_ficha_junta_todo_y_filtra_por_buque():
    row = {"buque": "A", "armador": "X S.A.", "mareas_temporada": 2, "mareas_con_observador": 1, "apagones": 1}
    yearly = [YearlyCoverage("A", 2021, 1, 3), YearlyCoverage("B", 2021, 0, 9)]

    result = profile(
        row,
        trips=[trip(1, observer=True), trip(1, vessel="B")],
        gaps=[gap(1), gap(1, buque="B")],
        yearly=yearly,
        visits=[port(datetime(2025, 2, 1, tzinfo=timezone.utc)), port(datetime(2025, 2, 1, tzinfo=timezone.utc), vessel="B")],
        season_year=2025,
        fleet={"mareas": 10, "mareas_con_observador": 1, "apagones": 5},
    )

    assert result["id"] == "A"
    assert result["datos"] is row
    assert len(result["mareas"]) == 1
    assert len(result["apagones_detalle"]) == 1
    assert len(result["escalas_detalle"]) == 1
    assert result["observador_por_anio"] == [
        {"anio": 2021, "viajes": 4, "con_observador": 1, "pct_con_observador": 25.0},
        {"anio": 2025, "viajes": 1, "con_observador": 1, "pct_con_observador": 100.0},
    ]
    assert result["comparacion"]["pct_con_observador_flota"] == 10.0


def test_ficha_une_grafias_del_buque_entre_fuentes():
    row = {"buque": "TAE BAEK 75", "mareas_temporada": 0, "mareas_con_observador": 0, "apagones": 0}

    result = profile(
        row, trips=[], gaps=[], yearly=[YearlyCoverage("Nº 75 TAE BAEK", 2022, 0, 2)],
        visits=[port(datetime(2025, 2, 1, tzinfo=timezone.utc), vessel="75 TAE BAEK")],
        season_year=2025, fleet={"mareas": 1, "mareas_con_observador": 0, "apagones": 0},
    )

    assert result["observador_por_anio"][0]["viajes"] == 2
    assert len(result["escalas_detalle"]) == 1
