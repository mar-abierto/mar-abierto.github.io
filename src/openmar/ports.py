"""Puertos: contratos que la aplicación necesita, sin decir cómo se cumplen (ADR 0005)."""

from pathlib import Path
from typing import Protocol


class RawStore(Protocol):
    """Capa bronze: guarda datos crudos con su procedencia y los devuelve tal cual."""

    def save(self, relative: str, content: str | bytes, source: str, **details: str) -> Path: ...

    def read_text(self, relative: str) -> str: ...

    def path(self, relative: str) -> Path: ...
