"""Caso de uso: de bronze a silver. Una sola forma por concepto (ADR 0006)."""

import dataclasses
import json
from pathlib import Path

from openmar.adapters import geo
from openmar.adapters.gfw import parse_fishing_event, parse_gap_event
from openmar.adapters.inidep import parse_observer_coverage, parse_observer_coverage_by_year, parse_trips_annex
from openmar.adapters.rfp import parse_registry_html
from openmar.adapters.tabular import write_items, write_rows
from openmar.application.download import BRONZE
from openmar.domain.matching import resolve_vessel_name
from openmar.domain.names import normalize_vessel_name
from openmar.ports import RawStore

SILVER = {
    "trips": "mareas.csv",
    "coverage": "cobertura.csv",
    "coverage_by_year": "cobertura-anual.csv",
    "registry": "registro.csv",
    "vessels": "buques.csv",
    "gaps": "apagones.csv",
    "fishing": "pesca.csv",
    "eez": "zee.geojson",
}


def _identities(vessels: list[dict]) -> list[dict]:
    rows = []
    for entry in vessels:
        for info in entry.get("selfReportedInfo") or []:
            rows.append(
                {
                    "buque": normalize_vessel_name(info.get("shipname")),
                    "mmsi": info.get("ssvid", ""),
                    "gfw_id": info.get("id", ""),
                    "bandera": info.get("flag", ""),
                    "transmite_desde": (info.get("transmissionDateFrom") or "")[:10],
                    "transmite_hasta": (info.get("transmissionDateTo") or "")[:10],
                }
            )
    return rows


def names_by_mmsi(identities: list[dict]) -> dict[str, str]:
    """MMSI → nombre normalizado, tomando la primera identidad con nombre."""
    names: dict[str, str] = {}
    for row in identities:
        if row["buque"] and row["mmsi"]:
            names.setdefault(row["mmsi"], row["buque"])
    return names


def build_silver(store: RawStore, silver_dir: Path) -> dict[str, int]:
    silver_dir = Path(silver_dir)
    out = {key: silver_dir / name for key, name in SILVER.items()}

    identities = _identities(json.loads(store.read_text(BRONZE["gfw_vessels"])))
    by_mmsi = names_by_mmsi(identities)

    def unify(event):
        return dataclasses.replace(event, vessel_name=resolve_vessel_name(event.vessel_name, event.mmsi, by_mmsi))

    gaps = [unify(parse_gap_event(e)) for e in json.loads(store.read_text(BRONZE["gfw_gaps"]))]
    fishing = [unify(parse_fishing_event(e)) for e in json.loads(store.read_text(BRONZE["gfw_fishing"]))]

    coverage_text = store.read_text(BRONZE["inidep_coverage"])
    counts = {
        "mareas": write_items(out["trips"], parse_trips_annex(store.read_text(BRONZE["inidep_trips"]))),
        "cobertura": write_items(out["coverage"], parse_observer_coverage(coverage_text)),
        "cobertura_anual": write_items(out["coverage_by_year"], parse_observer_coverage_by_year(coverage_text)),
        "registro": write_items(out["registry"], parse_registry_html(store.read_text(BRONZE["registry"]))),
        "identidades": write_rows(out["vessels"], identities),
        "apagones": write_items(out["gaps"], gaps),
        "eventos_de_pesca": write_items(out["fishing"], fishing),
    }
    geo.write_geojson(out["eez"], geo.simplify_eez(store.read_text(BRONZE["eez"])))
    return counts
