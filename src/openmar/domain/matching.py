"""Cruces entre fuentes: apagones de AIS contra mareas con y sin observador."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from openmar.domain.model import AisGap, Trip
from openmar.domain.names import normalize_vessel_name, vessel_key

STATUS_WITH_OBSERVER = "en_marea_con_observador"
STATUS_WITHOUT_OBSERVER = "en_marea_sin_observador"
STATUS_NO_TRIP = "fuera_de_marea"
STATUS_UNMATCHED = "sin_mareas_del_buque"

# 200 millas náuticas ≈ 370 km. Aproximación por distancia a la costa: el cálculo
# exacto debe hacerse contra la línea de la ZEE.
NEAR_200NM_KM = (300.0, 450.0)

# Las mareas del INIDEP están en fechas locales; los eventos de GFW, en UTC.
TRIP_TOLERANCE_DAYS = 3  # un apagón cerca del inicio o fin de marea se asigna a esa marea
LOCAL_TZ = ZoneInfo("America/Argentina/Buenos_Aires")


@dataclass(frozen=True)
class GapMatch:
    gap: AisGap
    vessel: str
    trip: Trip | None
    status: str


def is_near_200nm(gap: AisGap, band: tuple[float, float] = NEAR_200NM_KM) -> bool:
    low, high = band
    return any(
        km is not None and low <= km <= high for km in (gap.start_km_from_shore, gap.end_km_from_shore)
    )


def local_date(gap: AisGap) -> date:
    """Fecha del inicio del apagón en hora argentina."""
    return gap.start.astimezone(LOCAL_TZ).date()


def _distance_days(day: date, trip: Trip) -> int:
    if trip.start <= day <= trip.end:
        return 0
    return min(abs((trip.start - day).days), abs((day - trip.end).days))


def _trips_by_vessel(trips: Iterable[Trip]) -> dict[str, list[Trip]]:
    grouped: dict[str, list[Trip]] = {}
    for trip in trips:
        grouped.setdefault(vessel_key(trip.vessel), []).append(trip)
    return grouped


def _match_one(gap: AisGap, vessel_trips: list[Trip], tolerance: timedelta) -> tuple[Trip | None, str]:
    """Elige la marea que contiene el día; si ninguna, la más cercana dentro de la tolerancia."""
    if not vessel_trips:
        return None, STATUS_UNMATCHED
    day = local_date(gap)
    candidates = [t for t in vessel_trips if _distance_days(day, t) <= tolerance.days]
    if not candidates:
        return None, STATUS_NO_TRIP
    best = min(candidates, key=lambda t: (_distance_days(day, t), not t.observer))
    return best, STATUS_WITH_OBSERVER if best.observer else STATUS_WITHOUT_OBSERVER


def resolve_vessel_name(name: str, mmsi: str, names_by_mmsi: dict[str, str] | None = None) -> str:
    """Nombre normalizado del buque; si el evento no trae nombre, lo busca por MMSI."""
    normalized = normalize_vessel_name(name)
    if normalized or not names_by_mmsi:
        return normalized
    return names_by_mmsi.get(mmsi, "")


def match_gaps_to_trips(
    gaps: Iterable[AisGap],
    trips: Iterable[Trip],
    tolerance_days: int = TRIP_TOLERANCE_DAYS,
    names_by_mmsi: dict[str, str] | None = None,
) -> list[GapMatch]:
    """Ubica cada apagón en la marea en curso del mismo buque."""
    grouped = _trips_by_vessel(trips)
    tolerance = timedelta(days=tolerance_days)
    matches = []
    for gap in gaps:
        vessel = resolve_vessel_name(gap.vessel_name, gap.mmsi, names_by_mmsi)
        vessel_trips = grouped.get(vessel_key(vessel), [])
        if vessel_trips:
            vessel = vessel_trips[0].vessel  # el nombre de la marea manda: une variantes de escritura
        trip, status = _match_one(gap, vessel_trips, tolerance)
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

