"""Informes del INIDEP: mareas por buque y cobertura de observadores.

Los informes se publican en PDF en el repositorio Mar Abierto del INIDEP. Se
convierten a texto con `pdftotext -layout` (poppler) y se leen las tablas.

Los informes incluyen nombres de observadores. Estos lectores no los extraen.
"""

import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from openmar.normalize import normalize_vessel_name

# Informes usados por el demo de la flota potera.
REPORTS = {
    "observadores-2024": "https://marabiertonew.inidep.edu.ar/server/api/core/bitstreams/"
    "93efad8f-7689-43e1-a855-a584d7928eb0/content",
    "ito-026-2025": "https://marabiertonew.inidep.edu.ar/server/api/core/bitstreams/"
    "9044a37b-4fa1-4c1d-9eca-ff2fc3ecad1b/content",
}

_FECHA = r"\d{1,2}/\d{1,2}/\d{4}"
_FILA_MAREA = re.compile(
    rf"^\s*(?P<buque>[A-Z][A-Z0-9 ]*?)?\s+(?P<marea>\d+)(?P<obs>\*?)\s+"
    rf"(?P<desde>{_FECHA})\s+(?P<hasta>{_FECHA})\s+(?P<dias>\d+)\s+"
    r"(?P<captura>[\d.]+)\s+(?P<rend>[\d,]+)"
)
_FILA_COBERTURA = re.compile(r"^\s(?P<buque>[A-Z][A-Z0-9 ]+?)\s{2,}(?P<numeros>[\d\s.]+)$")


@dataclass(frozen=True)
class Trip:
    vessel: str
    trip: int
    observer: bool
    start: date
    end: date
    days: int
    catch_kg: int
    rate_t_per_day: float


@dataclass(frozen=True)
class Coverage:
    vessel: str
    trips: int
    with_observer: int
    without_observer: int
    pct_with_observer: float


def _parse_date(text: str) -> date:
    return datetime.strptime(text, "%d/%m/%Y").date()


def parse_trips_annex(text: str) -> list[Trip]:
    """Lee el Anexo 1 (detalle de mareas por buque) de un informe de temporada."""
    start = text.find("Anexo 1.")
    if start < 0:
        return []
    trips: list[Trip] = []
    current = ""
    for line in text[start:].splitlines():
        match = _FILA_MAREA.match(line)
        if not match:
            continue
        if match["buque"]:
            current = normalize_vessel_name(match["buque"])
        trips.append(
            Trip(
                vessel=current,
                trip=int(match["marea"]),
                observer=match["obs"] == "*",
                start=_parse_date(match["desde"]),
                end=_parse_date(match["hasta"]),
                days=int(match["dias"]),
                catch_kg=int(match["captura"].replace(".", "")),
                rate_t_per_day=float(match["rend"].replace(",", ".")),
            )
        )
    return trips


def parse_observer_coverage(text: str) -> list[Coverage]:
    """Lee la Tabla 9 (viajes con y sin observador por buque, 2021-2024)."""
    start = text.find("Tabla 9.")
    if start < 0:
        return []
    rows: list[Coverage] = []
    for line in text[start:].splitlines():
        if line.strip().startswith("TOTAL"):
            break
        match = _FILA_COBERTURA.match(line)
        if not match:
            continue
        numbers = match["numeros"].split()
        if len(numbers) < 5:
            continue
        with_obs, without_obs, total, pct_with, _ = numbers[-5:]
        rows.append(
            Coverage(
                vessel=normalize_vessel_name(match["buque"]),
                trips=int(total),
                with_observer=int(with_obs),
                without_observer=int(without_obs),
                pct_with_observer=float(pct_with),
            )
        )
    return rows


def pdf_to_text(pdf_path: Path) -> str:
    """Convierte un PDF a texto conservando columnas. Requiere poppler-utils."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Falta pdftotext: instalá poppler-utils (apt install poppler-utils).") from exc
    return result.stdout
