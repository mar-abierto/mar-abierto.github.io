"""Chequeo de coherencia de los datos publicados: una sola cifra de cortes por barco.

La cifra principal de cada barco es el total de cortes de señal de la temporada
(`apagones`). El desglose (sin observador, con observador, fuera de las fechas de
viaje, sin viajes informados) siempre suma ese total, y la historia, el tablero,
las fichas y el mapa leen los mismos campos. Esta función lo verifica.
"""

from collections import defaultdict

from openmar.domain.dashboard import GAP_BREAKDOWN, NO_OWNER
from openmar.domain.matching import STATUS_WITHOUT_OBSERVER

# Nombre del campo "sin observador" del tablero antes de publicar el desglose completo.
LEGACY_OWNER_KEYS = {STATUS_WITHOUT_OBSERVER: "apagones_sin_observador"}


def _n(row: dict, key: str) -> int:
    return int(float(row.get(key) or 0))


def _breakdown_problem(where: str, row: dict) -> str | None:
    parts = sum(_n(row, k) for k in GAP_BREAKDOWN)
    total = _n(row, "apagones")
    return None if parts == total else f"{where}: el desglose suma {parts} y el total es {total}"


def _vessel_problems(vessels: list[dict]) -> list[str]:
    return [p for v in vessels if (p := _breakdown_problem(f"ficha de {v['buque']}", v))]


def _fleet_problems(summary: dict, vessels: list[dict]) -> list[str]:
    problems = []
    total = sum(_n(v, "apagones") for v in vessels)
    if _n(summary, "apagones") != total:
        problems.append(f"flota: el resumen dice {_n(summary, 'apagones')} cortes y los barcos suman {total}")
    by_status = summary.get("apagones_por_estado") or {}
    if sum(_n(by_status, k) for k in GAP_BREAKDOWN) != _n(summary, "apagones"):
        problems.append("flota: el desglose por estado no suma el total de cortes")
    return problems


def _story_problems(summary: dict, by_name: dict[str, dict]) -> list[str]:
    problems = []
    for row in (summary.get("relato") or {}).get("senales_repetidas", []):
        vessel = by_name.get(row["buque"])
        if vessel is None:
            problems.append(f"historia: {row['buque']} no tiene ficha")
            continue
        for key in ("apagones", *GAP_BREAKDOWN):
            if key in row and _n(row, key) != _n(vessel, key):
                problems.append(f"historia: {row['buque']} tiene {_n(row, key)} en {key} y su ficha {_n(vessel, key)}")
    return problems


def _owner_problems(summary: dict, vessels: list[dict]) -> list[str]:
    sums: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for v in vessels:
        for key in ("apagones", *GAP_BREAKDOWN):
            sums[v["armador"] or NO_OWNER][key] += _n(v, key)
    problems = []
    for owner in (summary.get("tablero") or {}).get("por_armador", []):
        expected = sums.get(owner["armador"], {})
        for key in ("apagones", *GAP_BREAKDOWN):
            field = key if key in owner else LEGACY_OWNER_KEYS.get(key)
            if field is None or field not in owner:
                continue
            if _n(owner, field) != expected.get(key, 0):
                problems.append(f"tablero: {owner['armador']} tiene {_n(owner, field)} en {key} y sus barcos suman {expected.get(key, 0)}")
    return problems


def gap_count_problems(summary: dict, fichas: dict) -> list[str]:
    """Diferencias entre las cifras de cortes de resumen.json y fichas.json. Vacío si todo coincide."""
    vessels = [f["datos"] for f in fichas.get("buques", {}).values()]
    by_name = {v["buque"]: v for v in vessels}
    return [
        *_vessel_problems(vessels),
        *_fleet_problems(summary, vessels),
        *_story_problems(summary, by_name),
        *_owner_problems(summary, vessels),
    ]
