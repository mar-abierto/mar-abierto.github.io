"""Escalas en puerto por buque: dónde termina cada viaje.

Una escala no es una descarga: puede ser reparación, cambio de tripulación o
abastecimiento. El indicador dice dónde paran los buques, no qué hacen ahí.
"""

import dataclasses
from collections import Counter, defaultdict

from openmar.domain.model import PortVisit

HOME_COUNTRY = "ARG"
# Confianza de GFW: 2 = sólo entrada o salida; 3 = entrada y salida; 4 = además se detuvo.
MIN_CONFIDENCE = 3


def fill_port_names(visits: list[PortVisit]) -> list[PortVisit]:
    """Completa el nombre de puerto que falta con el de otras escalas del mismo puerto.

    Si ningún registro trae el nombre, queda el identificador del puerto de GFW.
    """
    names: dict[str, Counter] = defaultdict(Counter)
    for v in visits:
        if v.port_name and v.port_id:
            names[v.port_id][v.port_name] += 1

    def fill(v: PortVisit) -> PortVisit:
        if v.port_name or not v.port_id:
            return v
        known = names.get(v.port_id)
        return dataclasses.replace(v, port_name=known.most_common(1)[0][0] if known else v.port_id)

    return [fill(v) for v in visits]


def port_summary(visits: list[PortVisit], min_confidence: int = MIN_CONFIDENCE) -> dict[str, dict]:
    """Escalas confiables por buque, las del exterior y el puerto más frecuente."""
    by_vessel: dict[str, list[PortVisit]] = defaultdict(list)
    for v in visits:
        if v.confidence >= min_confidence and v.port_name:
            by_vessel[v.vessel_name].append(v)
    summary = {}
    for vessel, items in by_vessel.items():
        abroad = [v for v in items if v.port_country != HOME_COUNTRY]
        abroad_ports = Counter(f"{v.port_name} ({v.port_country})" for v in abroad)
        summary[vessel] = {
            "escalas": len(items),
            "escalas_exterior": len(abroad),
            "puertos_exterior": ", ".join(name for name, _ in abroad_ports.most_common()),
            "puerto_principal": Counter(v.port_name for v in items).most_common(1)[0][0],
        }
    return summary
