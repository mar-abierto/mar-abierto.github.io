import pytest

from openmar import cli


def test_gold_llama_al_caso_de_uso_con_las_carpetas(monkeypatch, tmp_path, capsys):
    called = {}

    def fake_gold(silver, gold):
        called["args"] = (silver, gold)
        return {"buques": 3, "apagones": 2}

    monkeypatch.setattr(cli, "build_gold", fake_gold)

    assert cli.main(["--datos", str(tmp_path), "gold"]) == 0
    assert called["args"] == (tmp_path / "silver", tmp_path / "gold")
    assert "apagones: 2" in capsys.readouterr().out


def test_error_conocido_sale_con_codigo_1_y_mensaje(monkeypatch, tmp_path, capsys):
    def fake_gold(silver, gold):
        raise FileNotFoundError("Falta silver/mareas.csv")

    monkeypatch.setattr(cli, "build_gold", fake_gold)

    assert cli.main(["--datos", str(tmp_path), "gold"]) == 1
    assert "Falta silver/mareas.csv" in capsys.readouterr().err


def test_datos_malformados_salen_con_error_claro(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "build_silver", lambda store, silver: (_ for _ in ()).throw(KeyError("start")))

    assert cli.main(["--datos", str(tmp_path), "silver"]) == 1
    assert "start" in capsys.readouterr().err


def test_fecha_invalida_la_rechaza_argparse(tmp_path):
    with pytest.raises(SystemExit):
        cli.main(["--datos", str(tmp_path), "descargar", "gfw", "--desde", "2025-13-01"])


def test_descargar_todo_recorre_las_cuatro_fuentes(monkeypatch, tmp_path):
    seen = []
    monkeypatch.setattr(cli, "_download", lambda store, source, start, end: seen.append(source) or {"ok": 1})

    assert cli.main(["--datos", str(tmp_path), "descargar", "todo"]) == 0
    assert seen == ["gfw", "inidep", "rfp", "zee"]


def test_publicar_usa_la_carpeta_del_sitio(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "publish_site", lambda gold, site: [site / "a", site / "b"])
    monkeypatch.setattr(cli, "export_site", lambda site: {"barcos": 0})

    assert cli.main(["--datos", str(tmp_path), "publicar", "--sitio", str(tmp_path / "web")]) == 0
    assert "publicados 2 archivos" in capsys.readouterr().out


def test_publicar_tambien_exporta_el_csv(monkeypatch, tmp_path, capsys):
    exported = {}

    def fake_export(site):
        exported["site"] = site
        return {"barcos": 3}

    monkeypatch.setattr(cli, "publish_site", lambda gold, site: [site / "fichas.json"])
    monkeypatch.setattr(cli, "export_site", fake_export)

    assert cli.main(["--datos", str(tmp_path), "publicar", "--sitio", str(tmp_path / "web")]) == 0
    assert exported["site"] == tmp_path / "web"
    assert "barcos: 3" in capsys.readouterr().out


def test_exportar_solo_genera_el_csv_sobre_lo_publicado(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "export_site", lambda site: {"barcos": 7, "archivo": str(site / "buques.csv")})

    assert cli.main(["exportar", "--sitio", str(tmp_path)]) == 0
    assert "barcos: 7" in capsys.readouterr().out


def test_exportar_sin_fichas_sale_con_error(tmp_path, capsys):
    assert cli.main(["exportar", "--sitio", str(tmp_path)]) == 1
    assert "fichas.json" in capsys.readouterr().err
