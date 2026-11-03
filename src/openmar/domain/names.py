"""Normalización de nombres de buques para cruzar fuentes.

Cada fuente escribe el mismo barco de forma distinta: "75 TAE BAEK" en el AIS,
"Nº 75 TAE BAEK" en el registro y "TAE BAEK 75" en el INIDEP. Esta función los
lleva a una única forma comparable.
"""

import re
import unicodedata

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
    # "Nº" se quita antes de normalizar: NFKD convierte "º" en "o".
    text = _NUMERO_PREFIJO.sub("", name.upper())
    # Sin tildes ni eñe: CÓNDOR y CONDOR son el mismo buque en distintas fuentes.
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = _NO_ALFANUMERICO.sub(" ", text)
    text = _NUMERO_PEGADO.sub(r"\1", text)
    text = _ESPACIOS.sub(" ", text).strip()
    for pattern, replacement in _ALIAS:
        text = pattern.sub(replacement, text)
    match = _NUMERO_ADELANTE.match(text)
    if match:
        text = f"{match.group(2)} {match.group(1)}"
    return text


_NUMEROS_EN_LETRAS = {
    "UNO": 1, "DOS": 2, "TRES": 3, "CUATRO": 4, "CINCO": 5, "SEIS": 6, "SIETE": 7, "OCHO": 8,
    "NUEVE": 9, "DIEZ": 10, "ONCE": 11, "DOCE": 12, "TRECE": 13, "CATORCE": 14, "QUINCE": 15,
    "DIECISEIS": 16, "DIECISIETE": 17, "DIECIOCHO": 18, "DIECINUEVE": 19, "VEINTE": 20,
}
_ROMANO = re.compile(r"^(X{0,3})(IX|IV|V?I{0,3})$")
_ROMANO_VALOR = {"I": 1, "V": 5, "X": 10}
_N_SUELTA = re.compile(r"\bN (\d+)\b")
# Variantes que sólo importan para comparar, no para mostrar.
_ALIAS_CLAVE = ((re.compile(r"\bLUQING\b"), "LU QING"),)


def _roman_to_int(token: str) -> int | None:
    if not token or not _ROMANO.match(token):
        return None
    total, previous = 0, 0
    for char in reversed(token):
        value = _ROMANO_VALOR[char]
        total, previous = (total - value, previous) if value < previous else (total + value, value)
    return total


def vessel_key(name: str | None) -> str:
    """Clave para cruzar fuentes: el número final siempre en dígitos.

    No sirve para mostrar: "ARBUMASA XXVIII" queda "ARBUMASA 28". Para mostrar se usa
    `normalize_vessel_name`.
    """
    text = _N_SUELTA.sub(r"\1", normalize_vessel_name(name))
    for pattern, replacement in _ALIAS_CLAVE:
        text = pattern.sub(replacement, text)
    head, _, last = text.rpartition(" ")
    if not head:
        return text
    number = _NUMEROS_EN_LETRAS.get(last) or _roman_to_int(last)
    return f"{head} {number}" if number else text
