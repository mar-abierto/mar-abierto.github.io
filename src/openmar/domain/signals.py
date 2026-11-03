"""Semáforo de señales para revisar (ADR 0008).

El color indica dónde mirar primero, no culpables.
"""

from openmar.domain.matching import STATUS_NO_TRIP, STATUS_WITHOUT_OBSERVER

GREEN = "verde"
YELLOW = "amarillo"
RED = "rojo"

# Umbral de apagones sin observador (o fuera de marea) para "señales repetidas".
# Cambiarlo requiere un ADR nuevo.
REPEATED_SIGNALS = 3

LABELS = {
    GREEN: "Sin señales",
    YELLOW: "Señales aisladas",
    RED: "Señales repetidas",
}


def classify(counts: dict[str, int]) -> str:
    """Clasifica un buque a partir de su resumen de apagones."""
    if counts.get("apagones", 0) == 0:
        return GREEN
    unobserved = counts.get(STATUS_WITHOUT_OBSERVER, 0) + counts.get(STATUS_NO_TRIP, 0)
    return RED if unobserved >= REPEATED_SIGNALS else YELLOW
