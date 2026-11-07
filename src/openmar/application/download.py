"""Caso de uso: descargar cada fuente a la capa bronze (ADR 0004 y 0006)."""

import json
from collections.abc import Callable

from openmar.adapters import geo, inidep, rfp
from openmar.adapters.gfw import BASE_URL, FISHING_DATASET, GAPS_DATASET, PORT_VISITS_DATASET, GFWClient
from openmar.ports import RawStore

# Ubicación de cada dato crudo dentro de bronze. Un solo lugar para cambiarla.
BRONZE = {
    "gfw_vessels": "gfw/buques.json",
    "gfw_gaps": "gfw/apagones.json",
    "gfw_fishing": "gfw/pesca.json",
    "gfw_port_visits": "gfw/puertos.json",
    "inidep_trips": "inidep/ito-026-2025.txt",
    "inidep_coverage": "inidep/observadores-2024.txt",
    "registry": "rfp/datos-de-pesca.html",
    "eez": "marineregions/zee-argentina.geojson",
}

SQUID_FLEET_QUERY = "flag='ARG' AND geartypes='SQUID_JIGGER'"

Fetch = Callable[[str], bytes]


def active_vessel_ids(entry: dict, start: str, end: str) -> list[str]:
    """Ids de todas las identidades del buque que transmitieron dentro del período.

    GFW parte un mismo buque en varias identidades (una por cada tramo de AIS) y los
    eventos quedan atados a la identidad que los emitió: si se consulta sólo una, se
    pierden los de las otras. Una fecha que falta no descarta: mejor de más que perderlo.
    """
    ids = []
    for info in entry.get("selfReportedInfo") or []:
        first, last = info.get("transmissionDateFrom") or "", info.get("transmissionDateTo") or ""
        if info.get("id") and (not last or last[:10] >= start) and (not first or first[:10] <= end):
            ids.append(info["id"])
    return ids


def download_gfw(store: RawStore, client: GFWClient, start: str, end: str) -> dict[str, int]:
    """Poteros con bandera argentina: apagones de AIS, eventos de pesca y escalas en puerto."""
    vessels = client.search_vessels(SQUID_FLEET_QUERY)
    store.save(BRONZE["gfw_vessels"], json.dumps(vessels), source=f"{BASE_URL}/vessels/search", query=SQUID_FLEET_QUERY)
    ids_by_vessel = [ids for ids in (active_vessel_ids(v, start, end) for v in vessels) if ids]
    # Una identidad puede figurar en más de un buque de la búsqueda: se pide una sola vez.
    active = list(dict.fromkeys(vid for ids in ids_by_vessel for vid in ids))
    period = f"{start}/{end}"
    gaps = client.get_events(GAPS_DATASET, active, start, end)
    store.save(BRONZE["gfw_gaps"], json.dumps(gaps), source=f"{BASE_URL}/events", dataset=GAPS_DATASET, period=period)
    fishing = client.get_events(FISHING_DATASET, active, start, end)
    store.save(
        BRONZE["gfw_fishing"], json.dumps(fishing), source=f"{BASE_URL}/events", dataset=FISHING_DATASET, period=period
    )
    visits = client.get_events(PORT_VISITS_DATASET, active, start, end)
    store.save(
        BRONZE["gfw_port_visits"], json.dumps(visits), source=f"{BASE_URL}/events", dataset=PORT_VISITS_DATASET, period=period
    )
    return {
        "buques": len(vessels),
        "activos": len(ids_by_vessel),
        "identidades": len(active),
        "apagones": len(gaps),
        "eventos_de_pesca": len(fishing),
        "escalas_en_puerto": len(visits),
    }


def download_inidep(store: RawStore, fetch: Fetch) -> dict[str, int]:
    """Informes del INIDEP en PDF, convertidos a texto."""
    names = {"ito-026-2025": BRONZE["inidep_trips"], "observadores-2024": BRONZE["inidep_coverage"]}
    for name, url in inidep.REPORTS.items():
        pdf = store.save(f"inidep/{name}.pdf", fetch(url), source=url)
        store.save(names[name], inidep.pdf_to_text(pdf), source=url, converted_with="pdftotext -layout -enc UTF-8")
    return {"informes": len(inidep.REPORTS)}


def download_registry(store: RawStore, fetch: Fetch) -> dict[str, int]:
    """Registro de Flota Pesquera (CPA y Sin Azul No Hay Verde)."""
    store.save(BRONZE["registry"], fetch(rfp.URL).decode("utf-8"), source=rfp.URL)
    return {"paginas": 1}


def download_eez(store: RawStore, fetch: Fetch) -> dict[str, int]:
    """Límite de la ZEE argentina desde Marine Regions."""
    store.save(BRONZE["eez"], fetch(geo.EEZ_URL).decode("utf-8"), source=geo.EEZ_URL, mrgid=str(geo.EEZ_MRGID))
    return {"poligonos": 1}
