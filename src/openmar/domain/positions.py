"""Posición representativa de un buque: la mediana de sus eventos de pesca."""

import math
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


def fishing_grid(events: Iterable[FishingEvent], size: float = 0.1) -> list[tuple[float, float, int]]:
    """Cuenta eventos de pesca por celda de `size` grados. Devuelve (lat, lon, eventos) del centro."""
    counts: dict[tuple[int, int], int] = {}
    for e in events:
        # Tolerancia mínima: -46.5 / 0.1 da -465.00000000000006 y caería en la celda de abajo.
        cell = (math.floor(round(e.lat / size, 9)), math.floor(round(e.lon / size, 9)))
        counts[cell] = counts.get(cell, 0) + 1
    return [
        (round((i + 0.5) * size, 4), round((j + 0.5) * size, 4), n) for (i, j), n in sorted(counts.items())
    ]
