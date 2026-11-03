"""Cruces entre fuentes: apagones de AIS contra mareas con y sin observador."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import timedelta

from openmar.normalize import normalize_vessel_name
from openmar.sources.gfw import Gap
from openmar.sources.inidep import Trip

STATUS_WITH_OBSERVER = "en_marea_con_observador"
STATUS_WITHOUT_OBSERVER = "en_marea_sin_observador"
STATUS_NO_TRIP = "fuera_de_marea"
STATUS_UNMATCHED = "sin_mareas_del_buque"

# 200 millas náuticas ≈ 370 km. Aproximación por distancia a la costa: el cálculo
# exacto debe hacerse contra la línea de la ZEE.
NEAR_200NM_KM = (300.0, 450.0)


@dataclass(frozen=True)
class GapMatch:
    gap: Gap
    vessel: str
    trip: Trip | None
    status: str


def is_near_200nm(gap: Gap, band: tuple[float, float] = NEAR_200NM_KM) -> bool:
    low, high = band
    return any(low <= km <= high for km in (gap.start_km_from_shore, gap.end_km_from_shore))


def _trips_by_vessel(trips: Iterable[Trip]) -> dict[str, list[Trip]]:
    grouped: dict[str, list[Trip]] = {}
    for trip in trips:
        grouped.setdefault(trip.vessel, []).append(trip)
    return grouped


def _match_one(gap: Gap, vessel_trips: list[Trip], tolerance: timedelta) -> tuple[Trip | None, str]:
    if not vessel_trips:
        return None, STATUS_UNMATCHED
    day = gap.start.date()
    in_range = [t for t in vessel_trips if t.start - tolerance <= day <= t.end + tolerance]
    if not in_range:
        return None, STATUS_NO_TRIP
    with_observer = [t for t in in_range if t.observer]
    if with_observer:
        return with_observer[0], STATUS_WITH_OBSERVER
    return in_range[0], STATUS_WITHOUT_OBSERVER


def match_gaps_to_trips(gaps: Iterable[Gap], trips: Iterable[Trip], tolerance_days: int = 3) -> list[GapMatch]:
    """Ubica cada apagón en la marea en curso del mismo buque."""
    grouped = _trips_by_vessel(trips)
    tolerance = timedelta(days=tolerance_days)
    matches = []
    for gap in gaps:
        vessel = normalize_vessel_name(gap.vessel_name)
        trip, status = _match_one(gap, grouped.get(vessel, []), tolerance)
        matches.append(GapMatch(gap=gap, vessel=vessel, trip=trip, status=status))
    return matches


def summarize_by_vessel(matches: Iterable[GapMatch]) -> dict[str, dict[str, int]]:
    """Cuenta apagones por buque, por estado y en la franja de la milla 200."""
    statuses = (STATUS_WITHOUT_OBSERVER, STATUS_WITH_OBSERVER, STATUS_NO_TRIP, STATUS_UNMATCHED)
    summary: dict[str, dict[str, int]] = {}
    for match in matches:
        row = summary.setdefault(
            match.vessel, {"apagones": 0, "franja_milla_200": 0, **{s: 0 for s in statuses}}
        )
        row["apagones"] += 1
        row["franja_milla_200"] += int(is_near_200nm(match.gap))
        row[match.status] += 1
    return dict(sorted(summary.items(), key=lambda item: -item[1]["apagones"]))

