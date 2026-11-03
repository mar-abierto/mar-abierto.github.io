"""Registro de Flota Pesquera (registroflotapesquera.org).

Base pública del Círculo de Políticas Ambientales y Sin Azul No Hay Verde, armada
con pedidos de acceso a la información pública. openMar no la redistribuye: cada
usuario la descarga del sitio y se cita como fuente.
"""

import html
import re
from dataclasses import dataclass

from openmar.normalize import normalize_vessel_name

URL = "https://registroflotapesquera.org/datos-de-pesca/"

_FILA = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
_CELDA = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
_ETIQUETA = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class RegistryEntry:
    vessel: str
    registration: str
    technical: str
    fleet_type: str
    owner: str
    permit: str
    permit_date: str
    authorization: str
    sanctions: str
    sanction_dates: str
    citc: str

    @property
    def normalized_name(self) -> str:
        return normalize_vessel_name(self.vessel)

    @property
    def is_squid_jigger(self) -> bool:
        return "POTER" in self.technical.upper() or "CALAMAR" in self.authorization.upper()


def _cell_text(raw: str) -> str:
    return html.unescape(_ETIQUETA.sub("", raw)).strip()


def parse_registry_html(page: str) -> list[RegistryEntry]:
    """Extrae una entrada por buque de la tabla de datos del registro."""
    entries: list[RegistryEntry] = []
    for index, row in enumerate(_FILA.findall(page)):
        cells = [_cell_text(c) for c in _CELDA.findall(row)]
        if index == 0 or len(cells) < 11 or not cells[0]:
            continue
        entries.append(RegistryEntry(*cells[:11]))
    return entries
