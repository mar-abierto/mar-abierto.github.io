"""Caso de uso: de silver a gold. Cruces listos para usar y GeoJSON del mapa."""

import json
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from openmar.adapters import geo
from openmar.adapters.tabular import (
    read_coverage,
    read_fishing,
    read_gaps,
    read_registry,
    read_trips,
    read_yearly_coverage,
    write_rows,
)
from openmar.application.silver import SILVER
from openmar.domain import signals
from openmar.domain.matching import (
    NEAR_200NM_KM,
    STATUS_NO_TRIP,
    STATUS_UNMATCHED,
    STATUS_WITH_OBSERVER,
    STATUS_WITHOUT_OBSERVER,
    TRIP_TOLERANCE_DAYS,
    is_near_200nm,
    local_date,
    match_gaps_to_trips,
    summarize_by_vessel,
)
from openmar.domain.model import RegistryRecord
from openmar.domain.names import vessel_key
from openmar.domain.positions import fishing_grid, vessel_position
from openmar.domain.story import coverage_by_year, history_figures, season_figures

SEASON_YEAR = 2025

# Criterio del conjunto público de apagones de Global Fishing Watch (no lo elegimos nosotros).
GFW_GAP_MIN_HOURS = 12

# Celdas de la capa de actividad de pesca: ~25 km, liviana para el navegador.
FISHING_GRID_DEGREES = 0.25

EMPTY_COUNTS = {
    "apagones": 0,
    "franja_milla_200": 0,
    STATUS_WITHOUT_OBSERVER: 0,
    STATUS_WITH_OBSERVER: 0,
    STATUS_NO_TRIP: 0,
    STATUS_UNMATCHED: 0,
}

SOURCES = [
    {"nombre": "Global Fishing Watch", "url": "https://globalfishingwatch.org", "aporta": "identidad de buques, apagones de AIS y eventos de pesca"},
    {"nombre": "INIDEP, repositorio Mar Abierto", "url": "https://marabierto.inidep.edu.ar", "aporta": "mareas por buque y cobertura de observadores"},
    {"nombre": "Registro de Flota Pesquera (CPA y Sin Azul No Hay Verde)", "url": "https://registroflotapesquera.org", "aporta": "matrícula, armador y sanciones"},
    {"nombre": "Marine Regions", "url": "https://www.marineregions.org", "aporta": "límite de la ZEE argentina"},
]


def _registry_index(records: list[RegistryRecord]) -> dict[str, RegistryRecord]:
    """Índice por nombre normalizado; ante nombres repetidos prefiere el potero."""
    index: dict[str, RegistryRecord] = {}
    for record in records:
        key = vessel_key(record.vessel)
        current = index.get(key)
        if current is None or (record.is_squid_jigger and not current.is_squid_jigger):
            index[key] = record
    return index


def _vessel_rows(silver_dir: Path) -> tuple[list[dict], list]:
    trips = read_trips(silver_dir / SILVER["trips"])
    coverage = {vessel_key(c.vessel): c for c in read_coverage(silver_dir / SILVER["coverage"])}
    registry = _registry_index(read_registry(silver_dir / SILVER["registry"]))
    gaps = read_gaps(silver_dir / SILVER["gaps"])
    fishing = read_fishing(silver_dir / SILVER["fishing"])

    matches = match_gaps_to_trips(gaps, trips)
    summary = summarize_by_vessel(matches)
    trips_by_vessel, fishing_by_key, hours, gap_points = defaultdict(list), defaultdict(list), defaultdict(float), defaultdict(list)
    for t in trips:
        trips_by_vessel[t.vessel].append(t)
    for f in fishing:
        fishing_by_key[vessel_key(f.vessel_name)].append(f)
    for m in matches:
        hours[m.vessel] += m.gap.hours
        if m.gap.lat is not None and m.gap.lon is not None:
            gap_points[m.vessel].append((m.gap.lat, m.gap.lon))

    rows = []
    for vessel in sorted(set(trips_by_vessel) | {v for v in summary if v}):
        counts = summary.get(vessel, EMPTY_COUNTS)
        key = vessel_key(vessel)
        record, cov, vtrips = registry.get(key), coverage.get(key), trips_by_vessel.get(vessel, [])
        vessel_fishing = fishing_by_key.get(key, [])
        position = vessel_position(vessel_fishing, gap_points.get(vessel, []))
        color = signals.classify(counts)
        rows.append(
            {
                "buque": vessel,
                "semaforo": color,
                "semaforo_texto": signals.LABELS[color],
                "matricula": record.registration if record else "",
                "armador": record.owner if record else "",
                "sanciones_registradas": record.sanctions if record else "",
                "fechas_sanciones": record.sanction_dates if record else "",
                "mareas_temporada": len(vtrips),
                "mareas_con_observador": sum(t.observer for t in vtrips),
                "captura_t": round(sum(t.catch_kg for t in vtrips) / 1000, 1),
                "viajes_2021_2024": cov.trips if cov else "",
                "viajes_con_observador_2021_2024": cov.with_observer if cov else "",
                **counts,
                "horas_sin_ais": round(hours.get(vessel, 0.0), 1),
                "eventos_de_pesca": len(vessel_fishing),
                "lat_zona_pesca": round(position[0], 4) if position else "",
                "lon_zona_pesca": round(position[1], 4) if position else "",
                "posicion_segun": position[2] if position else "",
            }
        )
    return rows, matches


def _gap_rows(matches) -> list[dict]:
    return [
        {
            "evento": m.gap.event_id,
            "buque": m.vessel,
            "fecha_local": local_date(m.gap).isoformat(),
            "inicio_utc": m.gap.start.isoformat(),
            "horas": round(m.gap.hours, 1),
            "km_costa_inicio": m.gap.start_km_from_shore,
            "km_costa_fin": m.gap.end_km_from_shore,
            "franja_milla_200": is_near_200nm(m.gap),
            "estado": m.status,
            "marea": m.trip.trip if m.trip else "",
            "lat": m.gap.lat,
            "lon": m.gap.lon,
        }
        for m in matches
    ]


def _map_layers(vessels: list[dict], gaps: list[dict], silver_dir: Path, map_dir: Path) -> None:
    geo.write_geojson(
        map_dir / "buques.geojson",
        geo.collection([geo.point(v["lon_zona_pesca"], v["lat_zona_pesca"], v) for v in vessels if v["lat_zona_pesca"] != ""]),
    )
    geo.write_geojson(
        map_dir / "apagones.geojson",
        geo.collection([geo.point(g["lon"], g["lat"], g) for g in gaps if g["lat"] is not None]),
    )
    fishing = read_fishing(silver_dir / SILVER["fishing"])
    geo.write_geojson(
        map_dir / "pesca.geojson",
        geo.collection([geo.point(lon, lat, {"eventos": n}) for lat, lon, n in fishing_grid(fishing, size=FISHING_GRID_DEGREES)]),
    )
    shutil.copyfile(silver_dir / SILVER["eez"], map_dir / "zee.geojson")


def _per_trip(gaps: int, trips: int) -> float:
    return round(gaps / trips, 2) if trips else 0.0


def _story(vessels: list[dict], gaps: list[dict], silver_dir: Path) -> dict:
    """Cifras de la portada: mareas, observadores y apagones, con su contexto."""
    trips = read_trips(silver_dir / SILVER["trips"])
    season = season_figures(trips)
    yearly = read_yearly_coverage(silver_dir / SILVER["coverage_by_year"])
    history = history_figures(read_coverage(silver_dir / SILVER["coverage"]))
    by_status = {s: sum(g["estado"] == s for g in gaps) for s in (STATUS_WITHOUT_OBSERVER, STATUS_WITH_OBSERVER)}
    red = sorted((v for v in vessels if v["semaforo"] == signals.RED), key=lambda v: -v["apagones"])
    return {
        "temporada": season,
        "historico_2021_2024": history,
        "cobertura_por_anio": coverage_by_year(yearly, trips, season_year=SEASON_YEAR),
        "horas_sin_ais": round(sum(g["horas"] for g in gaps), 1),
        "apagones_por_marea": {
            "sin_observador": _per_trip(by_status[STATUS_WITHOUT_OBSERVER], season["mareas_sin_observador"]),
            "con_observador": _per_trip(by_status[STATUS_WITH_OBSERVER], season["mareas_con_observador"]),
        },
        "senales_repetidas": [
            {k: v[k] for k in ("buque", "armador", "apagones", STATUS_WITHOUT_OBSERVER, STATUS_WITH_OBSERVER, STATUS_NO_TRIP,
                                "viajes_2021_2024", "viajes_con_observador_2021_2024")}
            for v in red
        ],
    }


def _summary(vessels: list[dict], gaps: list[dict], silver_dir: Path) -> dict:
    by_color = {c: sum(v["semaforo"] == c for v in vessels) for c in (signals.GREEN, signals.YELLOW, signals.RED)}
    return {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "temporada": f"Calamar {SEASON_YEAR}",
        "buques": len(vessels),
        "buques_en_mapa": sum(v["lat_zona_pesca"] != "" for v in vessels),
        "por_color": by_color,
        "sin_posicion": [
            {k: v[k] for k in ("buque", "armador", "matricula", "semaforo", "mareas_temporada", "apagones")}
            for v in vessels
            if v["lat_zona_pesca"] == ""
        ],
        "sin_armador": [v["buque"] for v in vessels if not v["armador"]],
        "apagones": len(gaps),
        "apagones_por_estado": {s: sum(g["estado"] == s for g in gaps) for s in EMPTY_COUNTS if s not in ("apagones", "franja_milla_200")},
        "reglas": {
            "umbral_senales_repetidas": signals.REPEATED_SIGNALS,
            "franja_milla_200_km": list(NEAR_200NM_KM),
            "tolerancia_dias_marea": TRIP_TOLERANCE_DAYS,
            "horas_minimas_apagon": GFW_GAP_MIN_HOURS,
        },
        "relato": _story(vessels, gaps, silver_dir),
        "fuentes": SOURCES,
    }


def build_gold(silver_dir: Path, gold_dir: Path) -> dict:
    silver_dir, gold_dir = Path(silver_dir), Path(gold_dir)
    vessels, matches = _vessel_rows(silver_dir)
    gaps = _gap_rows(matches)
    write_rows(gold_dir / "apagones-por-buque.csv", vessels)
    write_rows(gold_dir / "apagones-detalle.csv", gaps)
    map_dir = gold_dir / "mapa"
    _map_layers(vessels, gaps, silver_dir, map_dir)
    summary = _summary(vessels, gaps, silver_dir)
    (map_dir / "resumen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def publish_site(gold_dir: Path, site_data_dir: Path) -> list[Path]:
    """Copia los GeoJSON y el resumen del mapa a la carpeta del sitio."""
    site_data_dir = Path(site_data_dir)
    site_data_dir.mkdir(parents=True, exist_ok=True)
    for stale in site_data_dir.iterdir():
        if stale.is_file():
            stale.unlink()
    copied = []
    for source in sorted((Path(gold_dir) / "mapa").iterdir()):
        target = site_data_dir / source.name
        shutil.copyfile(source, target)
        copied.append(target)
    return copied
