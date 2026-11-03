"""Lectura y escritura de la capa silver en CSV, con tipos del dominio."""

import csv
from collections.abc import Callable, Iterable
from dataclasses import asdict, fields, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import TypeVar

from openmar.domain.model import AisGap, Coverage, FishingEvent, RegistryRecord, Trip

T = TypeVar("T")


def _to_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def write_rows(path: Path, rows: Iterable[dict]) -> int:
    """Escribe una lista de diccionarios como CSV. Devuelve la cantidad de filas."""
    rows = list(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({k: _to_cell(v) for k, v in row.items()} for row in rows)
    return len(rows)


def write_items(path: Path, items: Iterable) -> int:
    """Escribe dataclasses del dominio como CSV."""
    return write_rows(path, (asdict(i) if is_dataclass(i) else i for i in items))


def read_rows(path: Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Falta {path}. Corré primero `openmar silver`.")
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _optional_float(text: str) -> float | None:
    return float(text) if text != "" else None


_CONVERTERS: dict[type, Callable[[str], object]] = {
    int: int,
    float: float,
    bool: lambda t: t == "True",
    date: date.fromisoformat,
    datetime: datetime.fromisoformat,
    str: str,
    float | None: _optional_float,
}


def _read_items(path: Path, cls: type[T]) -> list[T]:
    types = {f.name: f.type for f in fields(cls)}
    return [cls(**{k: _CONVERTERS[types[k]](v) for k, v in row.items()}) for row in read_rows(path)]


def read_trips(path: Path) -> list[Trip]:
    return _read_items(path, Trip)


def read_coverage(path: Path) -> list[Coverage]:
    return _read_items(path, Coverage)


def read_gaps(path: Path) -> list[AisGap]:
    return _read_items(path, AisGap)


def read_fishing(path: Path) -> list[FishingEvent]:
    return _read_items(path, FishingEvent)


def read_registry(path: Path) -> list[RegistryRecord]:
    return _read_items(path, RegistryRecord)
