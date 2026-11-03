"""Arma las salidas procesadas a partir de los datos crudos descargados.

Estructura esperada en `raw_dir`:
    inidep/ito-026-2025.txt         texto del informe de temporada (Anexo 1)
    inidep/observadores-2024.txt    texto del informe de observadores (Tabla 9)
    rfp/datos-de-pesca.html         página del Registro de Flota Pesquera
    gfw/apagones.json               eventos de apagón de AIS de GFW
"""

import csv
import json
from dataclasses import asdict
from pathlib import Path

from openmar.cross import match_gaps_to_trips, summarize_by_vessel
from openmar.sources.gfw import parse_gap_event
from openmar.sources.inidep import parse_observer_coverage, parse_trips_annex
from openmar.sources.rfp import parse_registry_html

RAW_FILES = {
    "trips": Path("inidep/ito-026-2025.txt"),
    "coverage": Path("inidep/observadores-2024.txt"),
    "registry": Path("rfp/datos-de-pesca.html"),
    "gaps": Path("gfw/apagones.json"),
}


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _read(raw_dir: Path, key: str) -> str:
    path = raw_dir / RAW_FILES[key]
    if not path.exists():
        raise FileNotFoundError(f"Falta {path}. Corré primero `openmar descargar`.")
    return path.read_text(encoding="utf-8")


def build_outputs(raw_dir: Path, out_dir: Path) -> dict[str, int]:
    """Cruza las fuentes y escribe los CSV en `out_dir`. Devuelve totales."""
    raw_dir, out_dir = Path(raw_dir), Path(out_dir)
    trips = parse_trips_annex(_read(raw_dir, "trips"))
    coverage = {c.vessel: c for c in parse_observer_coverage(_read(raw_dir, "coverage"))}
    registry = {}
    for entry in parse_registry_html(_read(raw_dir, "registry")):
        registry.setdefault(entry.normalized_name, entry)
    gaps = [parse_gap_event(e) for e in json.loads(_read(raw_dir, "gaps"))]

    matches = match_gaps_to_trips(gaps, trips)
    summary = summarize_by_vessel(matches)

    rows = []
    for vessel, counts in summary.items():
        entry, cov = registry.get(vessel), coverage.get(vessel)
        rows.append(
            {
                "buque": vessel,
                "matricula": entry.registration if entry else "",
                "armador": entry.owner if entry else "",
                "sanciones": entry.sanctions if entry else "",
                **counts,
                "viajes_2021_2024": cov.trips if cov else "",
                "viajes_con_observador_2021_2024": cov.with_observer if cov else "",
            }
        )
    _write_csv(out_dir / "apagones-por-buque.csv", rows)
    _write_csv(out_dir / "mareas.csv", [asdict(t) for t in trips])
    _write_csv(
        out_dir / "apagones-detalle.csv",
        [
            {
                "evento": m.gap.event_id,
                "buque": m.vessel,
                "inicio": m.gap.start.isoformat(),
                "horas": m.gap.hours,
                "km_costa_inicio": m.gap.start_km_from_shore,
                "km_costa_fin": m.gap.end_km_from_shore,
                "estado": m.status,
                "marea": m.trip.trip if m.trip else "",
            }
            for m in matches
        ],
    )
    return {"mareas": len(trips), "apagones": len(gaps), "buques_con_apagones": len(summary)}
