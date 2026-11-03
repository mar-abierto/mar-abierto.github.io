from openmar import cli


def test_cruzar_llama_al_pipeline_con_las_carpetas(monkeypatch, tmp_path, capsys):
    called = {}

    def fake_build(raw_dir, out_dir):
        called["args"] = (raw_dir, out_dir)
        return {"mareas": 3, "apagones": 2, "buques_con_apagones": 1}

    monkeypatch.setattr(cli, "build_outputs", fake_build)

    code = cli.main(["--datos", str(tmp_path), "cruzar"])

    assert code == 0
    assert called["args"] == (tmp_path / "raw", tmp_path / "processed")
    assert "apagones: 2" in capsys.readouterr().out


def test_error_conocido_sale_con_codigo_1_y_mensaje(monkeypatch, tmp_path, capsys):
    def fake_build(raw_dir, out_dir):
        raise FileNotFoundError("Falta raw/gfw/apagones.json")

    monkeypatch.setattr(cli, "build_outputs", fake_build)

    code = cli.main(["--datos", str(tmp_path), "cruzar"])

    assert code == 1
    assert "Falta raw/gfw/apagones.json" in capsys.readouterr().err


def test_fecha_invalida_la_rechaza_argparse(tmp_path):
    import pytest

    with pytest.raises(SystemExit):
        cli.main(["--datos", str(tmp_path), "descargar", "gfw", "--desde", "2025-13-01"])


def test_datos_malformados_salen_con_error_claro(monkeypatch, tmp_path, capsys):
    def fake_build(raw_dir, out_dir):
        raise KeyError("start")

    monkeypatch.setattr(cli, "build_outputs", fake_build)

    assert cli.main(["--datos", str(tmp_path), "cruzar"]) == 1
    assert "start" in capsys.readouterr().err


def test_descargar_gfw_filtra_buques_activos_desde_la_fecha(monkeypatch, tmp_path):
    class FakeClient:
        def __init__(self, token):
            self.token = token

        def search_vessels(self, where):
            return [
                {"selfReportedInfo": [{"id": "activo", "transmissionDateTo": "2025-06-01T00:00:00Z"}]},
                {"selfReportedInfo": [{"id": "viejo", "transmissionDateTo": "2020-01-01T00:00:00Z"}]},
                {"selfReportedInfo": [{"id": "sin-fecha", "transmissionDateTo": None}]},
            ]

        def get_events(self, dataset, vessel_ids, start, end):
            self.ids = list(vessel_ids)
            return [{"id": "g1"}]

    created = {}

    def factory(token):
        created["client"] = FakeClient(token)
        return created["client"]

    monkeypatch.setattr(cli, "GFWClient", factory)
    monkeypatch.setattr(cli, "load_token", lambda: "tok")

    code = cli.main(["--datos", str(tmp_path), "descargar", "gfw", "--desde", "2025-01-01", "--hasta", "2025-12-31"])

    assert code == 0
    assert created["client"].ids == ["activo", "sin-fecha"]
    assert (tmp_path / "raw" / "gfw" / "apagones.json").exists()
    assert (tmp_path / "raw" / "gfw" / "buques.json.meta.json").exists()
