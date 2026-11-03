"""Posición representativa de un buque: la mediana de sus eventos de pesca."""

from collections.abc import Iterable
from statistics import median

from openmar.domain.model import FishingEvent


def fishing_zone(events: Iterable[FishingEvent]) -> tuple[float, float] | None:
    """Mediana de latitud y longitud: su zona habitual de pesca, no su posición actual."""
    events = list(events)
    if not events:
        return None
    return median(e.lat for e in events), median(e.lon for e in events)


def vessel_position(
    events: Iterable[FishingEvent], gap_points: Iterable[tuple[float, float]]
) -> tuple[float, float, str] | None:
    """Zona de pesca si hay eventos de pesca; si no, la mediana de sus apagones."""
    zone = fishing_zone(events)
    if zone:
        return zone[0], zone[1], "pesca"
    points = list(gap_points)
    if not points:
        return None
    return median(p[0] for p in points), median(p[1] for p in points), "apagones"
