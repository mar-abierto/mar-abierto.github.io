"""Cifras del relato: lo que la portada cuenta, calculado desde los datos."""

from collections import defaultdict

from openmar.domain.model import Coverage, Trip, YearlyCoverage


def _pct(part: int, total: int) -> float:
    return round(100 * part / total, 1) if total else 0.0


def season_figures(trips: list[Trip]) -> dict:
    """Mareas de la temporada con y sin observador, buques, captura y fecha de corte.

    La fecha de corte es el regreso del último viaje informado: la temporada
    publicada llega hasta ahí, no hasta fin de año.
    """
    observed = sum(t.observer for t in trips)
    return {
        "mareas": len(trips),
        "mareas_con_observador": observed,
        "mareas_sin_observador": len(trips) - observed,
        "pct_con_observador": _pct(observed, len(trips)),
        "buques": len({t.vessel for t in trips}),
        "buques_con_algun_observador": len({t.vessel for t in trips if t.observer}),
        "captura_t": round(sum(t.catch_kg for t in trips) / 1000, 1),
        "fecha_corte": max(t.end for t in trips).isoformat() if trips else None,
    }


def history_figures(coverage: list[Coverage]) -> dict:
    """Viajes con observador en el período histórico del INIDEP."""
    trips = sum(c.trips for c in coverage)
    observed = sum(c.with_observer for c in coverage)
    return {
        "buques": len(coverage),
        "viajes": trips,
        "viajes_con_observador": observed,
        "pct_con_observador": _pct(observed, trips),
        "buques_nunca_con_observador": sum(c.with_observer == 0 for c in coverage),
    }


def coverage_by_year(yearly: list[YearlyCoverage], season: list[Trip], season_year: int) -> list[dict]:
    """Serie anual de viajes con observador: el histórico más la temporada en curso."""
    totals: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for row in yearly:
        totals[row.year][0] += row.with_observer + row.without_observer
        totals[row.year][1] += row.with_observer
    totals[season_year] = [len(season), sum(t.observer for t in season)]
    return [
        {"anio": year, "viajes": trips, "con_observador": observed, "pct_con_observador": _pct(observed, trips)}
        for year, (trips, observed) in sorted(totals.items())
    ]
