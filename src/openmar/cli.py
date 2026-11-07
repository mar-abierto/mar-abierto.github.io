"""Línea de comandos de openMar: el adaptador de entrada (ADR 0005).

    openmar descargar todo --desde 2025-01-01 --hasta 2025-12-31
    openmar silver
    openmar gold
    openmar publicar
    openmar exportar
"""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

import requests

from openmar.adapters.filesystem import LocalRawStore, load_token
from openmar.adapters.gfw import GFWClient, GFWError
from openmar.application import download
from openmar.application.exportar import export_site
from openmar.application.gold import build_gold, publish_site
from openmar.application.silver import build_silver

SOURCES = ("gfw", "inidep", "rfp", "zee")
MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024
KNOWN_ERRORS = (
    FileNotFoundError,
    RuntimeError,
    GFWError,
    requests.RequestException,
    subprocess.SubprocessError,
    KeyError,
    ValueError,
)


def fetch(url: str) -> bytes:
    """Descarga con tiempo límite y tope de tamaño."""
    with requests.get(url, timeout=120, stream=True, headers={"User-Agent": "openMar"}) as response:
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_content(chunk_size=65536):
            content.extend(chunk)
            if len(content) > MAX_DOWNLOAD_BYTES:
                raise RuntimeError(f"La descarga de {url} supera {MAX_DOWNLOAD_BYTES // 2**20} MB.")
    return bytes(content)


def _iso_date(text: str) -> str:
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"fecha inválida: {text} (formato AAAA-MM-DD)") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openmar", description="Observatorio pesquero del Mar Argentino")
    parser.add_argument("--datos", type=Path, default=Path("data"), help="carpeta de datos (default: data)")
    sub = parser.add_subparsers(dest="comando", required=True)
    descargar = sub.add_parser("descargar", help="baja datos crudos a data/bronze")
    descargar.add_argument("fuente", choices=[*SOURCES, "todo"])
    descargar.add_argument("--desde", type=_iso_date, default="2025-01-01")
    descargar.add_argument("--hasta", type=_iso_date, default="2025-12-31")
    sub.add_parser("silver", help="limpia y unifica: data/bronze → data/silver")
    sub.add_parser("gold", help="cruza y arma el mapa: data/silver → data/gold")
    publicar = sub.add_parser("publicar", help="copia el mapa de data/gold al sitio")
    publicar.add_argument("--sitio", type=Path, default=Path("site/data"))
    exportar = sub.add_parser("exportar", help="arma site/data/buques.csv desde las fichas publicadas")
    exportar.add_argument("--sitio", type=Path, default=Path("site/data"))
    return parser


def _download(store: LocalRawStore, source: str, start: str, end: str) -> dict:
    if source == "gfw":
        return download.download_gfw(store, GFWClient(load_token()), start, end)
    if source == "inidep":
        return download.download_inidep(store, fetch)
    if source == "rfp":
        return download.download_registry(store, fetch)
    return download.download_eez(store, fetch)


def _print(title: str, stats: dict) -> None:
    print(f"{title}: " + ", ".join(f"{k}: {v}" for k, v in stats.items() if not isinstance(v, (dict, list))))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    bronze, silver, gold = args.datos / "bronze", args.datos / "silver", args.datos / "gold"
    try:
        if args.comando == "descargar":
            store = LocalRawStore(bronze)
            for source in SOURCES if args.fuente == "todo" else (args.fuente,):
                _print(source, _download(store, source, args.desde, args.hasta))
        elif args.comando == "silver":
            _print("silver", build_silver(LocalRawStore(bronze), silver))
        elif args.comando == "gold":
            _print("gold", build_gold(silver, gold))
        elif args.comando == "exportar":
            _print("csv", export_site(args.sitio))
        else:
            copied = publish_site(gold, args.sitio)
            print(f"publicados {len(copied)} archivos en {args.sitio}")
            _print("csv", export_site(args.sitio))
    except KNOWN_ERRORS as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
