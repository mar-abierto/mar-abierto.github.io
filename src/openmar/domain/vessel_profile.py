"""Ficha por buque: todo lo que se sabe de un barco, cruzado entre fuentes.

La ficha muestra conductas medibles (observador, AIS, escalas) con las mismas
reglas para todos los buques. El armador aparece como dato de transparencia,
nunca como señal (ADR 0010).
"""

from collections import Counter

from openmar.domain.matching import LOCAL_TZ
from openmar.domain.model import PortVisit, Trip, YearlyCoverage
from openmar.domain.names import vessel_key
from openmar.domain.port_visits import counts, is_abroad
from openmar.domain.story import coverage_by_year

GAP_FIELDS = ("fecha_local", "horas", "estado", "marea", "franja_milla_200", "km_costa_inicio", "km_costa_fin")


def _ratio(part: float, total: float, scale: float = 1, digits: int = 2) -> float | None:
    return round(scale * part / total, digits) if total else None


def trip_rows(trips: list[Trip], gaps: list[dict]) -> list[dict]:
    """Mareas del buque en orden, cada una con los apagones que cayeron en ella."""
    per_trip = Counter(g["marea"] for g in gaps if g["marea"] != "")
    return [
        {
            "marea": t.trip,
            "inicio": t.start.isoformat(),
            "fin": t.end.isoformat(),
            "dias": t.days,
            "observador": t.observer,
            "captura_t": round(t.catch_kg / 1000, 1),
            "apagones": per_trip.get(t.trip, 0),
        }
        for t in sorted(trips, key=lambda t: t.trip)
    ]


def gap_rows(gaps: list[dict]) -> list[dict]:
    """Apagones en orden de fecha. Sin coordenadas: para ubicarlos está el mapa."""
    return [{k: g[k] for k in GAP_FIELDS} for g in sorted(gaps, key=lambda g: g["fecha_local"])]


def visit_rows(visits: list[PortVisit]) -> list[dict]:
    """Escalas que entran en los indicadores, en orden de llegada (hora argentina)."""
    return [
        {
            "llegada": v.start.astimezone(LOCAL_TZ).date().isoformat(),
            "puerto": v.port_name,
            "pais": v.port_country,
            "exterior": is_abroad(v),
            "horas": round(v.hours, 1),
            "nombre_completado": v.port_name_inferred,
        }
        for v in sorted(visits, key=lambda v: v.start)
        if counts(v)
    ]


def comparison(row: dict, fleet: dict) -> dict:
    """El buque contra el total de la flota en la misma temporada."""
    return {
        "pct_con_observador": _ratio(row["mareas_con_observador"], row["mareas_temporada"], 100, 1),
        "pct_con_observador_flota": _ratio(fleet["mareas_con_observador"], fleet["mareas"], 100, 1),
        "apagones_por_marea": _ratio(row["apagones"], row["mareas_temporada"]),
        "apagones_por_marea_flota": _ratio(fleet["apagones"], fleet["mareas"]),
    }


def profile(
    row: dict,
    trips: list[Trip],
    gaps: list[dict],
    yearly: list[YearlyCoverage],
    visits: list[PortVisit],
    season_year: int,
    fleet: dict,
) -> dict:
    """Ficha completa de un buque. `row` es su fila del gold; el resto se filtra por nombre."""
    key = vessel_key(row["buque"])
    own_trips = [t for t in trips if vessel_key(t.vessel) == key]
    own_gaps = [g for g in gaps if vessel_key(g["buque"]) == key]
    return {
        "id": key,
        "datos": row,
        "mareas": trip_rows(own_trips, own_gaps),
        "apagones_detalle": gap_rows(own_gaps),
        "observador_por_anio": coverage_by_year(
            [y for y in yearly if vessel_key(y.vessel) == key], own_trips, season_year=season_year
        ),
        "escalas_detalle": visit_rows([v for v in visits if vessel_key(v.vessel_name) == key]),
        "comparacion": comparison(row, fleet),
    }
