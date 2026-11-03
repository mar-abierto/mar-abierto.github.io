"""GeoJSON para la capa de presentación y límite de la ZEE (Marine Regions)."""

import json
from pathlib import Path

from shapely.geometry import mapping, shape

# Zona Económica Exclusiva argentina en Marine Regions (mismo id que usa GFW).
EEZ_MRGID = 8466
EEZ_URL = (
    "https://geo.vliz.be/geoserver/MarineRegions/wfs?service=WFS&version=1.0.0"
    f"&request=GetFeature&typeName=MarineRegions:eez&cql_filter=mrgid={EEZ_MRGID}"
    "&outputFormat=application/json"
)
# Tolerancia de simplificación en grados (~3 km): suficiente para un mapa nacional.
SIMPLIFY_DEGREES = 0.03
COORD_DECIMALS = 4


def point(lon: float, lat: float, properties: dict) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [round(lon, COORD_DECIMALS), round(lat, COORD_DECIMALS)]},
        "properties": properties,
    }


def collection(features: list[dict]) -> dict:
    return {"type": "FeatureCollection", "features": features}


def write_geojson(path: Path, data: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def _round_coords(obj):
    if isinstance(obj, (list, tuple)):
        if obj and isinstance(obj[0], (int, float)):
            return [round(c, COORD_DECIMALS) for c in obj]
        return [_round_coords(o) for o in obj]
    return obj


def simplify_eez(raw_geojson: str) -> dict:
    """Simplifica el polígono de la ZEE para que pese poco en el navegador."""
    data = json.loads(raw_geojson)
    features = []
    for feature in data.get("features", []):
        geometry = shape(feature["geometry"]).simplify(SIMPLIFY_DEGREES, preserve_topology=True)
        geo = mapping(geometry)
        geo = {"type": geo["type"], "coordinates": _round_coords(geo["coordinates"])}
        name = feature.get("properties", {}).get("geoname", "")
        features.append({"type": "Feature", "geometry": geo, "properties": {"nombre": name}})
    return collection(features)
