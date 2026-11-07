"""Cliente mínimo de la API v3 de Global Fishing Watch.

Requiere un token gratuito para uso no comercial:
https://globalfishingwatch.org/our-apis/tokens
Los datos de GFW se citan como fuente según sus términos de uso.
"""

import json
import time
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime

import requests

from openmar.domain.model import AisGap, FishingEvent, PortVisit

BASE_URL = "https://gateway.api.globalfishingwatch.org/v3"
IDENTITY_DATASET = "public-global-vessel-identity:latest"
GAPS_DATASET = "public-global-gaps-events:latest"
FISHING_DATASET = "public-global-fishing-events:latest"
PORT_VISITS_DATASET = "public-global-port-visits-events:latest"
EVENTS_PAGE_SIZE = 500
# Respuestas que vale la pena reintentar, además de cualquier 5xx.
TRANSIENT_STATUS = {429}


class GFWError(RuntimeError):
    """Error de la API de GFW. Nunca incluye el token."""


def _optional_float(value) -> float | None:
    return None if value is None else float(value)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_gap_event(raw: dict) -> AisGap:
    """Convierte un evento de apagón de AIS de la API en un `Gap`."""
    vessel = raw.get("vessel", {})
    distances = raw.get("distances", {})
    position = raw.get("position", {})
    gap = raw.get("gap", {})
    return AisGap(
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


def parse_fishing_event(raw: dict) -> FishingEvent:
    """Convierte un evento de pesca de la API en un `FishingEvent`."""
    vessel = raw.get("vessel", {})
    position = raw.get("position", {})
    return FishingEvent(
        event_id=raw["id"],
        vessel_name=vessel.get("name") or "",
        mmsi=vessel.get("ssvid", ""),
        start=_parse_time(raw["start"]),
        lat=float(position["lat"]),
        lon=float(position["lon"]),
    )


def parse_port_visit(raw: dict) -> PortVisit:
    """Convierte una escala en puerto de la API en un `PortVisit`.

    El puerto es el ancladero de llegada; si no está, el de salida.
    """
    vessel = raw.get("vessel", {})
    position = raw.get("position", {})
    visit = raw.get("port_visit", {})
    anchorage = visit.get("endAnchorage") or visit.get("startAnchorage") or {}
    return PortVisit(
        event_id=raw["id"],
        vessel_name=vessel.get("name") or "",
        mmsi=vessel.get("ssvid", ""),
        start=_parse_time(raw["start"]),
        end=_parse_time(raw["end"]),
        hours=float(visit.get("durationHrs") or 0),
        port_name=anchorage.get("name") or "",
        port_country=anchorage.get("flag") or "",
        confidence=int(visit.get("confidence") or 0),
        lat=float(position.get("lat", 0.0)),
        lon=float(position.get("lon", 0.0)),
        port_id=anchorage.get("id") or "",
    )


def _entry_key(entry: dict) -> str:
    """Clave de un buque: todas sus identidades; sin ids, el contenido completo."""
    ids = sorted(info.get("id") for info in entry.get("selfReportedInfo") or [] if info.get("id"))
    return "ids:" + "|".join(ids) if ids else "json:" + json.dumps(entry, sort_keys=True)


def _event_key(event: dict) -> str:
    """Clave de un evento: su id; sin id, el contenido completo (nunca se descarta a ciegas)."""
    return f"id:{event['id']}" if event.get("id") else "json:" + json.dumps(event, sort_keys=True)


class GFWClient:
    """Cliente de la API de GFW.

    Ante 429, 5xx, timeout o error de conexión reintenta `retries` veces, con esperas
    de 2, 4, 8… segundos (`backoff * 2**n`). Si se agotan, o ante cualquier otro error
    HTTP, levanta `GFWError`. Si una paginación llega a `max_pages` y la API todavía
    ofrece más, también levanta `GFWError`: preferimos no publicar antes que publicar
    datos truncados sin saberlo.
    """

    def __init__(
        self,
        token: str,
        session=None,
        page_size: int = 50,
        batch_size: int = 20,
        max_pages: int = 100,
        timeout: int = 60,
        retries: int = 3,
        backoff: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
    ):
        if not token:
            raise GFWError("Falta el token de GFW (variable GFW_API_TOKEN).")
        self._headers = {"Authorization": f"Bearer {token}"}
        self._session = session or requests.Session()
        self._page_size = page_size
        self._max_pages = max_pages
        self._batch_size = batch_size
        self._timeout = timeout
        self._retries = retries
        self._backoff = backoff
        self._sleep = sleep

    def _get(self, path: str, params: dict) -> dict:
        attempts = self._retries + 1
        problem = ""
        for attempt in range(attempts):
            if attempt:
                self._sleep(self._backoff * 2 ** (attempt - 1))
            try:
                response = self._session.get(
                    f"{BASE_URL}{path}", params=params, headers=self._headers, timeout=self._timeout
                )
            except (requests.Timeout, requests.ConnectionError) as exc:
                problem = type(exc).__name__
                continue
            except requests.RequestException as exc:
                raise GFWError(f"GFW falló en {path}: {type(exc).__name__}") from None
            if response.status_code in TRANSIENT_STATUS or response.status_code >= 500:
                problem = f"HTTP {response.status_code}"
                continue
            if response.status_code != 200:
                raise GFWError(f"GFW respondió HTTP {response.status_code} en {path}")
            try:
                return response.json()
            except ValueError:
                raise GFWError(f"GFW devolvió una respuesta que no es JSON en {path}") from None
        raise GFWError(f"GFW no respondió bien en {path} tras {attempts} intentos (último: {problem})")

    def _page_limit_error(self, what: str) -> GFWError:
        return GFWError(
            f"{what}: se llegó al tope de {self._max_pages} páginas y GFW ofrece más. "
            "No se corta en silencio: subí max_pages o acotá la consulta."
        )

    def search_vessels(self, where: str, dataset: str = IDENTITY_DATASET) -> list[dict]:
        """Busca buques con una consulta avanzada y recorre todas las páginas.

        La paginación de GFW puede devolver páginas llenas de buques repetidos: se
        descartan (por el conjunto de sus ids) y se corta cuando una página no trae
        nada nuevo. Llegar al tope de páginas con más por venir es un error.
        """
        seen: dict[str, dict] = {}
        since = None
        total = None
        for _ in range(self._max_pages):
            params = {"where": where, "datasets[0]": dataset, "limit": self._page_size}
            if since:
                params["since"] = since
            page = self._get("/vessels/search", params)
            entries = page.get("entries", [])
            total = page.get("total", total)
            before = len(seen)
            for entry in entries:
                seen.setdefault(_entry_key(entry), entry)
            since = page.get("since")
            if not since or len(entries) < self._page_size or len(seen) == before:
                break
        else:
            raise self._page_limit_error("Búsqueda de buques")
        # La paginación de GFW deja de avanzar pasados ~100 resultados y repite
        # páginas: si faltan buques respecto del total anunciado, se avisa.
        if isinstance(total, int) and len(seen) < total:
            raise GFWError(
                f"Búsqueda de buques: GFW anuncia {total} buques y la paginación entregó {len(seen)}. "
                "Acotá la consulta (por ejemplo, por fechas de transmisión)."
            )
        return list(seen.values())

    def get_events(self, dataset: str, vessel_ids: Iterable[str], start_date: str, end_date: str) -> list[dict]:
        """Descarga eventos de un conjunto de datos para una lista de buques, sin repetir `id`."""
        ids = list(vessel_ids)
        events: dict[str, dict] = {}
        for i in range(0, len(ids), self._batch_size):
            batch = ids[i : i + self._batch_size]
            for page in self._event_pages(dataset, batch, start_date, end_date):
                for event in page:
                    events.setdefault(_event_key(event), event)
        return list(events.values())

    def _event_pages(self, dataset: str, batch: list[str], start_date: str, end_date: str) -> Iterator[list[dict]]:
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
            yield page.get("entries", [])
            next_offset = page.get("nextOffset")
            # Se sigue sólo si hay próxima página y el offset avanza: un offset
            # trabado (o en 0) no puede hacer girar el ciclo para siempre.
            if next_offset is None or next_offset <= offset:
                return
            offset = next_offset
        raise self._page_limit_error(f"Eventos de {dataset}")
