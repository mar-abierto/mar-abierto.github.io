import json

import pytest

from openmar.storage import load_token, save_raw


def test_save_raw_guarda_el_archivo_y_su_procedencia(tmp_path):
    path = save_raw(tmp_path / "gfw" / "buques.json", '{"a": 1}', source="https://ejemplo.org/api", query="flag=ARG")

    assert path.read_text() == '{"a": 1}'
    meta = json.loads(path.with_name("buques.json.meta.json").read_text())
    assert meta["source"] == "https://ejemplo.org/api"
    assert meta["query"] == "flag=ARG"
    assert "downloaded" in meta


def test_save_raw_acepta_bytes(tmp_path):
    path = save_raw(tmp_path / "x.pdf", b"%PDF-1.4", source="https://ejemplo.org/x.pdf")

    assert path.read_bytes() == b"%PDF-1.4"


def test_token_desde_variable_de_entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("GFW_API_TOKEN", "desde-entorno")

    assert load_token(tmp_path / ".env") == "desde-entorno"


def test_token_desde_archivo_env(monkeypatch, tmp_path):
    monkeypatch.delenv("GFW_API_TOKEN", raising=False)
    env = tmp_path / ".env"
    env.write_text("# comentario\nOTRA=1\nGFW_API_TOKEN=desde-archivo\n")

    assert load_token(env) == "desde-archivo"


def test_token_ausente_da_error_claro(monkeypatch, tmp_path):
    monkeypatch.delenv("GFW_API_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="GFW_API_TOKEN"):
        load_token(tmp_path / ".env")
