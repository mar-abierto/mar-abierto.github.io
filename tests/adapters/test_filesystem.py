import json

import pytest

from openmar.adapters.filesystem import LocalRawStore, load_token, save_raw


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


def test_token_entre_comillas_o_con_export(monkeypatch, tmp_path):
    monkeypatch.delenv("GFW_API_TOKEN", raising=False)
    env = tmp_path / ".env"
    env.write_text('export GFW_API_TOKEN="con-comillas"\n')

    assert load_token(env) == "con-comillas"


def test_token_ausente_da_error_claro(monkeypatch, tmp_path):
    monkeypatch.delenv("GFW_API_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="GFW_API_TOKEN"):
        load_token(tmp_path / ".env")


def test_local_raw_store_guarda_y_lee_relativo_a_su_carpeta(tmp_path):
    store = LocalRawStore(tmp_path / "bronze")

    store.save("rfp/pagina.html", "<table/>", source="https://ejemplo.org")

    assert store.read_text("rfp/pagina.html") == "<table/>"
    assert store.path("rfp/pagina.html") == tmp_path / "bronze" / "rfp" / "pagina.html"


def test_local_raw_store_avisa_si_falta_el_archivo(tmp_path):
    with pytest.raises(FileNotFoundError, match="openmar descargar"):
        LocalRawStore(tmp_path).read_text("nada.json")
