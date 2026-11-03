"""Escalas en puerto por buque: dónde paran los barcos.

Una escala no es una descarga: puede ser reparación, cambio de tripulación o
abastecimiento. El indicador dice dónde paran los buques según el AIS, no qué
hacen ahí, y sólo cuenta lo que Global Fishing Watch detecta.
"""

import dataclasses
from collections import Counter, defaultdict

from openmar.domain.matching import LOCAL_TZ
from openmar.domain.model import PortVisit
from openmar.domain.names import vessel_key

HOME_COUNTRY = "ARG"
# Confianza de GFW: 2 = sólo entrada o salida; 3 = entrada y salida; 4 = además se detuvo.
MIN_CONFIDENCE = 3


def is_abroad(visit: PortVisit) -> bool:
    """Puerto de otro país. Un país desconocido no cuenta como exterior."""
    return bool(visit.port_country) and visit.port_country != HOME_COUNTRY


def counts(visit: PortVisit, min_confidence: int = MIN_CONFIDENCE) -> bool:
    """La escala entra en los indicadores: confianza suficiente y puerto identificado."""
    return visit.confidence >= min_confidence and bool(visit.port_name)


def arrivals_in_year(visits: list[PortVisit], year: int) -> list[PortVisit]:
    """Escalas cuya llegada al puerto fue en ese año, en hora argentina (ADR 0007).

    La API devuelve también estadías que empezaron antes y siguen en el período.
    """
    return [v for v in visits if v.start.astimezone(LOCAL_TZ).year == year]


def fill_port_names(visits: list[PortVisit]) -> list[PortVisit]:
    """Completa el nombre de puerto que falta con el de otras escalas del mismo puerto.

    Si ningún registro trae el nombre, se marca como puerto sin nombre con su id.
    Toda escala completada queda marcada con `port_name_inferred`.
    """
    names: dict[str, Counter] = defaultdict(Counter)
    for v in visits:
        if v.port_name and v.port_id:
            names[v.port_id][v.port_name] += 1

    def fill(v: PortVisit) -> PortVisit:
        if v.port_name or not v.port_id:
            return v
        known = names.get(v.port_id)
        name = known.most_common(1)[0][0] if known else f"Puerto sin nombre ({v.port_id})"
        return dataclasses.replace(v, port_name=name, port_name_inferred=True)

    return [fill(v) for v in visits]


def port_summary(visits: list[PortVisit], min_confidence: int = MIN_CONFIDENCE) -> dict[str, dict]:
    """Escalas por buque (clave: `vessel_key`), las del exterior y el puerto más frecuente."""
    by_vessel: dict[str, list[PortVisit]] = defaultdict(list)
    for v in visits:
        if counts(v, min_confidence):
            by_vessel[vessel_key(v.vessel_name)].append(v)
    summary = {}
    for key, items in by_vessel.items():
        abroad = [v for v in items if is_abroad(v)]
        abroad_ports = Counter(f"{v.port_name} ({v.port_country})" for v in abroad)
        summary[key] = {
            "escalas": len(items),
            "escalas_exterior": len(abroad),
            "escalas_pais_desconocido": sum(not v.port_country for v in items),
            "puertos_exterior": ", ".join(name for name, _ in abroad_ports.most_common()),
            "puerto_principal": Counter(v.port_name for v in items).most_common(1)[0][0],
        }
    return summary


def visit_quality(visits: list[PortVisit], year: int, min_confidence: int = MIN_CONFIDENCE) -> dict[str, int]:
    """Cuántas escalas descargadas quedan afuera del indicador y por qué."""
    in_year = arrivals_in_year(visits, year)
    confident = [v for v in in_year if v.confidence >= min_confidence]
    counted = [v for v in confident if v.port_name]
    return {
        "descargadas": len(visits),
        "de_otros_anios": len(visits) - len(in_year),
        "baja_confianza": len(in_year) - len(confident),
        "sin_puerto": len(confident) - len(counted),
        "pais_desconocido": sum(not v.port_country for v in counted),
        "nombre_completado": sum(v.port_name_inferred for v in counted),
        "contadas": len(counted),
    }
