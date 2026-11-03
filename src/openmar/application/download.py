"""Caso de uso: descargar cada fuente a la capa bronze (ADR 0004 y 0006)."""

import json
from collections.abc import Callable

from openmar.adapters import geo, inidep, rfp
from openmar.adapters.gfw import BASE_URL, FISHING_DATASET, GAPS_DATASET, GFWClient
from openmar.ports import RawStore

# Ubicación de cada dato crudo dentro de bronze. Un solo lugar para cambiarla.
BRONZE = {
    "gfw_vessels": "gfw/buques.json",
    "gfw_gaps": "gfw/apagones.json",
    "gfw_fishing": "gfw/pesca.json",
    "inidep_trips": "inidep/ito-026-2025.txt",
    "inidep_coverage": "inidep/observadores-2024.txt",
    "registry": "rfp/datos-de-pesca.html",
    "eez": "marineregions/zee-argentina.geojson",
}

SQUID_FLEET_QUERY = "flag='ARG' AND geartypes='SQUID_JIGGER'"

Fetch = Callable[[str], bytes]


def _vessel_id(entry: dict) -> tuple[str, str]:
    info = (entry.get("selfReportedInfo") or [{}])[0]
    return info.get("id", ""), info.get("transmissionDateTo") or ""


def download_gfw(store: RawStore, client: GFWClient, start: str, end: str) -> dict[str, int]:
    """Poteros con bandera argentina, sus apagones de AIS y sus eventos de pesca."""
    vessels = client.search_vessels(SQUID_FLEET_QUERY)
    store.save(BRONZE["gfw_vessels"], json.dumps(vessels), source=f"{BASE_URL}/vessels/search", query=SQUID_FLEET_QUERY)
    # Un buque sin fecha de última transmisión se conserva: mejor de más que perderlo.
    active = [vid for vid, last in map(_vessel_id, vessels) if vid and (not last or last[:10] >= start)]
    period = f"{start}/{end}"
    gaps = client.get_events(GAPS_DATASET, active, start, end)
    store.save(BRONZE["gfw_gaps"], json.dumps(gaps), source=f"{BASE_URL}/events", dataset=GAPS_DATASET, period=period)
    fishing = client.get_events(FISHING_DATASET, active, start, end)
    store.save(
        BRONZE["gfw_fishing"], json.dumps(fishing), source=f"{BASE_URL}/events", dataset=FISHING_DATASET, period=period
    )
    return {"buques": len(vessels), "activos": len(active), "apagones": len(gaps), "eventos_de_pesca": len(fishing)}


def download_inidep(store: RawStore, fetch: Fetch) -> dict[str, int]:
    """Informes del INIDEP en PDF, convertidos a texto."""
    names = {"ito-026-2025": BRONZE["inidep_trips"], "observadores-2024": BRONZE["inidep_coverage"]}
    for name, url in inidep.REPORTS.items():
        pdf = store.save(f"inidep/{name}.pdf", fetch(url), source=url)
        store.save(names[name], inidep.pdf_to_text(pdf), source=url, converted_with="pdftotext -layout")
    return {"informes": len(inidep.REPORTS)}


def download_registry(store: RawStore, fetch: Fetch) -> dict[str, int]:
    """Registro de Flota Pesquera (CPA y Sin Azul No Hay Verde)."""
    store.save(BRONZE["registry"], fetch(rfp.URL).decode("utf-8"), source=rfp.URL)
    return {"paginas": 1}


def download_eez(store: RawStore, fetch: Fetch) -> dict[str, int]:
    """Límite de la ZEE argentina desde Marine Regions."""
    store.save(BRONZE["eez"], fetch(geo.EEZ_URL).decode("utf-8"), source=geo.EEZ_URL, mrgid=str(geo.EEZ_MRGID))
    return {"poligonos": 1}
