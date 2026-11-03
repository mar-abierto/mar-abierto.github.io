"""Cliente mínimo de la API v3 de Global Fishing Watch.

Requiere un token gratuito para uso no comercial:
https://globalfishingwatch.org/our-apis/tokens
Los datos de GFW se citan como fuente según sus términos de uso.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

import requests

BASE_URL = "https://gateway.api.globalfishingwatch.org/v3"
IDENTITY_DATASET = "public-global-vessel-identity:latest"
GAPS_DATASET = "public-global-gaps-events:latest"
FISHING_DATASET = "public-global-fishing-events:latest"
EVENTS_PAGE_SIZE = 500


class GFWError(RuntimeError):
    """Error de la API de GFW. Nunca incluye el token."""


@dataclass(frozen=True)
class Gap:
    event_id: str
    vessel_id: str
    vessel_name: str
    mmsi: str
    start: datetime
    end: datetime
    hours: float
    start_km_from_shore: float | None
    end_km_from_shore: float | None
    lat: float | None
    lon: float | None
    intentional: bool


def _optional_float(value) -> float | None:
    return None if value is None else float(value)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_gap_event(raw: dict) -> Gap:
    """Convierte un evento de apagón de AIS de la API en un `Gap`."""
    vessel = raw.get("vessel", {})
    distances = raw.get("distances", {})
    position = raw.get("position", {})
    gap = raw.get("gap", {})
    return Gap(
        event_id=raw["id"],
        vessel_id=vessel.get("id", ""),
        vessel_name=vessel.get("name") or "",
        mmsi=vessel.get("ssvid", ""),
        start=_parse_time(raw["start"]),
        end=_parse_time(raw["end"]),
        hours=float(gap.get("durationHours", 0)),
        start_km_from_shore=_optional_float(distances.get("startDistanceFromShoreKm")),
        end_km_from_shore=_optional_float(distances.get("endDistanceFromShoreKm")),
        lat=_optional_float(position.get("lat")),
        lon=_optional_float(position.get("lon")),
        intentional=bool(gap.get("intentionalDisabling", False)),
    )


class GFWClient:
    def __init__(
        self,
        token: str,
        session=None,
        page_size: int = 50,
        batch_size: int = 20,
        max_pages: int = 100,
        timeout: int = 60,
    ):
        if not token:
            raise GFWError("Falta el token de GFW (variable GFW_API_TOKEN).")
        self._headers = {"Authorization": f"Bearer {token}"}
        self._session = session or requests.Session()
        self._page_size = page_size
        self._max_pages = max_pages
        self._batch_size = batch_size
        self._timeout = timeout

    def _get(self, path: str, params: dict) -> dict:
        response = self._session.get(
            f"{BASE_URL}{path}", params=params, headers=self._headers, timeout=self._timeout
        )
        if response.status_code != 200:
            raise GFWError(f"GFW respondió HTTP {response.status_code} en {path}")
        return response.json()

    def search_vessels(self, where: str, dataset: str = IDENTITY_DATASET) -> list[dict]:
        """Busca buques con una consulta avanzada y recorre todas las páginas.

        La paginación de GFW puede devolver páginas llenas de buques repetidos: se
        descartan por id y se corta cuando una página no trae nada nuevo, o al llegar
        al tope de páginas.
        """
        seen: dict[str, dict] = {}
        since = None
        for _ in range(self._max_pages):
            params = {"where": where, "datasets[0]": dataset, "limit": self._page_size}
            if since:
                params["since"] = since
            page = self._get("/vessels/search", params)
            entries = page.get("entries", [])
            before = len(seen)
            for entry in entries:
                info = (entry.get("selfReportedInfo") or [{}])[0]
                key = info.get("id") or str(len(seen))
                seen.setdefault(key, entry)
            since = page.get("since")
            if not since or len(entries) < self._page_size or len(seen) == before:
                break
        return list(seen.values())

    def get_events(self, dataset: str, vessel_ids: Iterable[str], start_date: str, end_date: str) -> list[dict]:
        """Descarga eventos de un conjunto de datos para una lista de buques."""
        ids = list(vessel_ids)
        events: list[dict] = []
        for i in range(0, len(ids), self._batch_size):
            batch = ids[i : i + self._batch_size]
            offset = 0
            for _ in range(self._max_pages):
                params = {
                    "datasets[0]": dataset,
                    "start-date": start_date,
                    "end-date": end_date,
                    "limit": EVENTS_PAGE_SIZE,
                    "offset": offset,
                }
                params.update({f"vessels[{j}]": vid for j, vid in enumerate(batch)})
                page = self._get("/events", params)
                events.extend(page.get("entries", []))
                next_offset = page.get("nextOffset")
                # Se sigue sólo si hay próxima página y el offset avanza: un offset
                # trabado (o en 0) no puede hacer girar el ciclo para siempre.
                if next_offset is None or next_offset <= offset:
                    break
                offset = next_offset
        return events
