"""Caso de uso: CSV para periodistas, una fila por barco, desde site/data/fichas.json.

Se corre después de `publicar` (que vacía site/data) o solo con `openmar exportar`.
El CSV va en UTF-8 con BOM para que Excel muestre bien los acentos y la Ñ.
"""

import csv
import json
from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.parse import quote

CSV_NAME = "buques.csv"
PUBLICATION_NAME = "publicacion.json"
FICHAS_NAME = "fichas.json"

# Dominio público del sitio, a decidir: reemplazar cuando haya dominio
# (ver docs/pendientes-lanzamiento.md).
SITE_URL = "https://mar-abierto.github.io"

SOURCE = (
    "Viajes y observadores: INIDEP; cortes de señal y escalas: Global Fishing Watch; "
    "matrícula y armador: Registro de Flota Pesquera (CPA y Sin Azul No Hay Verde)"
)

_Getter = Callable[[dict, str], object]


def _field(key: str) -> _Getter:
    return lambda datos, _season: datos.get(key, "")


def _trips_without_observer(datos: dict, _season: str) -> object:
    trips, with_observer = datos.get("mareas_temporada"), datos.get("mareas_con_observador")
    if trips in (None, "") or with_observer in (None, ""):
        return ""
    return int(trips) - int(with_observer)


def _profile_url(datos: dict, _season: str) -> str:
    return f"{SITE_URL}/buque.html?b={quote(str(datos.get('buque', '')), safe='')}"


COLUMNS: tuple[tuple[str, _Getter], ...] = (
    ("barco", _field("buque")),
    ("matricula", _field("matricula")),
    ("armador", _field("armador")),
    ("temporada", lambda _datos, season: season),
    ("viajes_temporada", _field("mareas_temporada")),
    ("viajes_con_observador", _field("mareas_con_observador")),
    ("viajes_sin_observador", _trips_without_observer),
    ("cortes_de_senal", _field("apagones")),
    ("cortes_en_viaje_sin_observador", _field("en_marea_sin_observador")),
    ("cortes_en_viaje_con_observador", _field("en_marea_con_observador")),
    ("cortes_fuera_de_viaje", _field("fuera_de_marea")),
    ("cortes_sin_viajes_informados", _field("sin_mareas_del_buque")),
    ("cortes_cerca_milla_200", _field("franja_milla_200")),
    ("horas_sin_senal", _field("horas_sin_ais")),
    ("semaforo", _field("semaforo")),
    ("semaforo_texto", _field("semaforo_texto")),
    ("captura_t", _field("captura_t")),
    ("viajes_2021_2024", _field("viajes_2021_2024")),
    ("viajes_con_observador_2021_2024", _field("viajes_con_observador_2021_2024")),
    ("escalas", _field("escalas")),
    ("escalas_exterior", _field("escalas_exterior")),
    ("ficha", _profile_url),
    ("fuente", lambda _datos, _season: SOURCE),
)


def vessel_rows(fichas: dict) -> list[dict]:
    """Una fila por barco, ordenadas por nombre, con las columnas de COLUMNS."""
    vessels = fichas.get("buques")
    if not isinstance(vessels, dict):
        raise ValueError("fichas.json no trae el bloque 'buques'.")
    season = fichas.get("temporada", "")
    rows = [
        {name: getter(entry.get("datos", {}), season) for name, getter in COLUMNS}
        for entry in vessels.values()
    ]
    return sorted(rows, key=lambda row: str(row["barco"]))


def write_csv(rows: list[dict], target: Path) -> None:
    """CSV separado por comas, UTF-8 con BOM y fin de línea CRLF (RFC 4180)."""
    with Path(target).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[name for name, _ in COLUMNS], lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def openmar_version() -> str:
    """La versión de pyproject.toml, vía los metadatos del paquete instalado."""
    try:
        return version("openmar")
    except PackageNotFoundError:  # pragma: no cover - sólo si se corre sin instalar
        return "0.0.0"


def export_site(site_data_dir: Path, version: str | None = None) -> dict:
    """Escribe buques.csv y publicacion.json (versión y fecha para citar)."""
    site_data_dir = Path(site_data_dir)
    source = site_data_dir / FICHAS_NAME
    if not source.exists():
        raise FileNotFoundError(f"Falta {source}: corré antes `openmar gold` y `openmar publicar`.")
    fichas = json.loads(source.read_text(encoding="utf-8"))
    rows = vessel_rows(fichas)
    target = site_data_dir / CSV_NAME
    write_csv(rows, target)
    publication = {
        "version": version or openmar_version(),
        "generado": fichas.get("generado", ""),
        "temporada": fichas.get("temporada", ""),
        "csv": CSV_NAME,
        "barcos": len(rows),
    }
    (site_data_dir / PUBLICATION_NAME).write_text(
        json.dumps(publication, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"barcos": len(rows), "archivo": str(target)}
