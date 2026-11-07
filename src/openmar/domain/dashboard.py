"""Indicadores del tablero: los mismos números para todas las empresas (ADR 0010)."""

from collections import defaultdict

from openmar.domain.matching import STATUS_NO_TRIP, STATUS_UNMATCHED, STATUS_WITH_OBSERVER, STATUS_WITHOUT_OBSERVER
from openmar.domain.model import PortVisit
from openmar.domain.port_visits import MIN_CONFIDENCE, counts, is_abroad
from openmar.domain.signals import RED

NO_OWNER = "Sin armador en el registro"
# El total de cortes es la cifra principal; el desglose usa las mismas claves que cada buque
# y siempre suma el total.
GAP_BREAKDOWN = (STATUS_WITHOUT_OBSERVER, STATUS_WITH_OBSERVER, STATUS_NO_TRIP, STATUS_UNMATCHED)
_SUMS = {
    "mareas": "mareas_temporada",
    "mareas_con_observador": "mareas_con_observador",
    "apagones": "apagones",
    **{status: status for status in GAP_BREAKDOWN},
    "escalas": "escalas",
    "escalas_exterior": "escalas_exterior",
    "captura_t": "captura_t",
}


def by_owner(vessels: list[dict]) -> list[dict]:
    """Agrupa los buques por armador. Ordena por cantidad de mareas."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for v in vessels:
        groups[v["armador"] or NO_OWNER].append(v)
    owners = []
    for owner, items in groups.items():
        totals = {key: sum(float(v.get(field) or 0) for v in items) for key, field in _SUMS.items()}
        trips = int(totals["mareas"])
        owners.append(
            {
                "armador": owner,
                "buques": len(items),
                "mareas": trips,
                "mareas_con_observador": int(totals["mareas_con_observador"]),
                "pct_con_observador": round(100 * totals["mareas_con_observador"] / trips, 1) if trips else 0.0,
                "apagones": int(totals["apagones"]),
                **{status: int(totals[status]) for status in GAP_BREAKDOWN},
                "escalas": int(totals["escalas"]),
                "escalas_exterior": int(totals["escalas_exterior"]),
                "buques_senales_repetidas": sum(v["semaforo"] == RED for v in items),
                "captura_t": round(totals["captura_t"], 1),
            }
        )
    return sorted(owners, key=lambda o: (o["armador"] == NO_OWNER, -o["mareas"], o["armador"]))


def port_ranking(visits: list[PortVisit], foreign_only: bool = False, min_confidence: int = MIN_CONFIDENCE) -> list[dict]:
    """Puertos donde hicieron escala los buques, de más a menos escalas."""
    by_port: dict[tuple[str, str], list[str]] = defaultdict(list)
    for v in visits:
        if not counts(v, min_confidence) or (foreign_only and not is_abroad(v)):
            continue
        by_port[(v.port_name, v.port_country)].append(v.vessel_name)
    rows = [
        {"puerto": port, "pais": country, "escalas": len(names), "buques": len(set(names))}
        for (port, country), names in by_port.items()
    ]
    return sorted(rows, key=lambda r: (-r["escalas"], r["puerto"]))
