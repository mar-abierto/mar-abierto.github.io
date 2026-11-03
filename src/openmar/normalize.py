"""Normalización de nombres de buques para cruzar fuentes.

Cada fuente escribe el mismo barco de forma distinta: "75 TAE BAEK" en el AIS,
"Nº 75 TAE BAEK" en el registro y "TAE BAEK 75" en el INIDEP. Esta función los
lleva a una única forma comparable.
"""

import re

_NUMERO_PREFIJO = re.compile(r"\bN\s*[º°]\s*")
_NUMERO_PEGADO = re.compile(r"\bN(\d+)\b")
_NO_ALFANUMERICO = re.compile(r"[^A-Z0-9 ]")
_ESPACIOS = re.compile(r"\s+")
_NUMERO_ADELANTE = re.compile(r"^(\d+) (.+)$")

# Variantes de escritura conocidas entre fuentes.
_ALIAS = ((re.compile(r"\bHU YU\b"), "HUYU"),)


def normalize_vessel_name(name: str | None) -> str:
    """Devuelve el nombre en mayúsculas, sin símbolos y con el número al final."""
    if not name:
        return ""
    text = name.upper()
    text = _NUMERO_PREFIJO.sub("", text)
    text = _NO_ALFANUMERICO.sub(" ", text)
    text = _NUMERO_PEGADO.sub(r"\1", text)
    text = _ESPACIOS.sub(" ", text).strip()
    for pattern, replacement in _ALIAS:
        text = pattern.sub(replacement, text)
    match = _NUMERO_ADELANTE.match(text)
    if match:
        text = f"{match.group(2)} {match.group(1)}"
    return text
