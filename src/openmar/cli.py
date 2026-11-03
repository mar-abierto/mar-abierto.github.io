"""Línea de comandos de openMar.

    openmar descargar gfw --desde 2025-01-01 --hasta 2025-12-31
    openmar descargar inidep
    openmar descargar rfp
    openmar cruzar
"""

import argparse
import json
import sys
from pathlib import Path

import requests

from openmar.pipeline import RAW_FILES, build_outputs
from openmar.sources import inidep, rfp
from openmar.sources.gfw import BASE_URL, GAPS_DATASET, GFWClient, GFWError
from openmar.storage import load_token, save_raw

SQUID_FLEET_QUERY = "flag='ARG' AND geartypes='SQUID_JIGGER'"


def _vessel_id(entry: dict) -> tuple[str, str]:
    info = (entry.get("selfReportedInfo") or [{}])[0]
    return info.get("id", ""), info.get("transmissionDateTo") or ""


def download_gfw(raw_dir: Path, start: str, end: str) -> None:
    client = GFWClient(load_token())
    vessels = client.search_vessels(SQUID_FLEET_QUERY)
    save_raw(raw_dir / "gfw" / "buques.json", json.dumps(vessels), source=f"{BASE_URL}/vessels/search", query=SQUID_FLEET_QUERY)
    active = [vid for vid, last in map(_vessel_id, vessels) if vid and last[:10] >= start]
    gaps = client.get_events(GAPS_DATASET, active, start, end)
    save_raw(raw_dir / RAW_FILES["gaps"], json.dumps(gaps), source=f"{BASE_URL}/events", dataset=GAPS_DATASET, period=f"{start}/{end}")
    print(f"GFW: {len(vessels)} buques, {len(active)} activos desde {start}, {len(gaps)} apagones.")


def _fetch(url: str) -> requests.Response:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    return response


def download_inidep(raw_dir: Path) -> None:
    for name, url in inidep.REPORTS.items():
        pdf = save_raw(raw_dir / "inidep" / f"{name}.pdf", _fetch(url).content, source=url)
        pdf.with_suffix(".txt").write_text(inidep.pdf_to_text(pdf), encoding="utf-8")
        print(f"INIDEP: {name}")


def download_rfp(raw_dir: Path) -> None:
    save_raw(raw_dir / RAW_FILES["registry"], _fetch(rfp.URL).text, source=rfp.URL)
    print("Registro de Flota Pesquera: descargado. Fuente: CPA y Sin Azul No Hay Verde.")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openmar", description="Observatorio pesquero del Mar Argentino")
    parser.add_argument("--datos", type=Path, default=Path("data"), help="carpeta de datos (default: data)")
    sub = parser.add_subparsers(dest="comando", required=True)
    descargar = sub.add_parser("descargar", help="baja los datos crudos de una fuente")
    descargar.add_argument("fuente", choices=["gfw", "inidep", "rfp"])
    descargar.add_argument("--desde", default="2025-01-01")
    descargar.add_argument("--hasta", default="2025-12-31")
    sub.add_parser("cruzar", help="cruza las fuentes y genera los CSV")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    raw_dir, out_dir = args.datos / "raw", args.datos / "processed"
    try:
        if args.comando == "descargar":
            if args.fuente == "gfw":
                download_gfw(raw_dir, args.desde, args.hasta)
            elif args.fuente == "inidep":
                download_inidep(raw_dir)
            else:
                download_rfp(raw_dir)
        else:
            stats = build_outputs(raw_dir, out_dir)
            print(", ".join(f"{k}: {v}" for k, v in stats.items()))
            print(f"Resultados en {out_dir}")
    except (FileNotFoundError, RuntimeError, GFWError, requests.RequestException) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
