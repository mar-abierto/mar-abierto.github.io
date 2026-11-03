"""Almacenamiento en disco de la capa bronze y lectura de credenciales."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

TOKEN_VAR = "GFW_API_TOKEN"


def save_raw(path: Path, content: str | bytes, source: str, **details: str) -> Path:
    """Guarda un dato crudo y, al lado, un `.meta.json` con de dónde salió y cuándo."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    meta = {"source": source, "downloaded": datetime.now(timezone.utc).isoformat(), **details}
    path.with_name(f"{path.name}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


class LocalRawStore:
    """Implementa `RawStore` sobre una carpeta (por defecto `data/bronze`)."""

    def __init__(self, root: Path):
        self._root = Path(root)

    def path(self, relative: str) -> Path:
        return self._root / relative

    def save(self, relative: str, content: str | bytes, source: str, **details: str) -> Path:
        return save_raw(self.path(relative), content, source, **details)

    def read_text(self, relative: str) -> str:
        target = self.path(relative)
        if not target.exists():
            raise FileNotFoundError(f"Falta {target}. Corré primero `openmar descargar`.")
        return target.read_text(encoding="utf-8")


def load_token(env_file: Path = Path(".env")) -> str:
    """Lee el token de GFW de la variable de entorno o, si no está, del archivo `.env`."""
    token = os.environ.get(TOKEN_VAR, "").strip()
    if token:
        return token
    env_file = Path(env_file)
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key, sep, value = line.removeprefix("export ").partition("=")
            value = value.strip().strip("\"'")
            if sep and key.strip() == TOKEN_VAR and value:
                return value
    raise RuntimeError(f"Falta {TOKEN_VAR}: definilo en el entorno o en {env_file} (ver .env.example).")
