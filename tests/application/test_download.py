import json

from openmar.adapters.filesystem import LocalRawStore
from openmar.application.download import BRONZE, download_eez, download_gfw, download_registry


class FakeClient:
    def __init__(self):
        self.requested = []

    def search_vessels(self, where):
        return [
            {"selfReportedInfo": [{"id": "activo", "transmissionDateTo": "2025-06-01T00:00:00Z"}]},
            {"selfReportedInfo": [{"id": "viejo", "transmissionDateTo": "2020-01-01T00:00:00Z"}]},
            {"selfReportedInfo": [{"id": "sin-fecha", "transmissionDateTo": None}]},
        ]

    def get_events(self, dataset, vessel_ids, start, end):
        self.requested.append((dataset, list(vessel_ids)))
        return [{"id": dataset}]


def test_gfw_baja_apagones_y_pesca_de_buques_activos(tmp_path):
    store, client = LocalRawStore(tmp_path), FakeClient()

    stats = download_gfw(store, client, "2025-01-01", "2025-12-31")

    assert stats == {"buques": 3, "activos": 2, "apagones": 1, "eventos_de_pesca": 1, "escalas_en_puerto": 1}
    assert all(ids == ["activo", "sin-fecha"] for _, ids in client.requested)
    assert json.loads(store.read_text(BRONZE["gfw_gaps"])) == [{"id": "public-global-gaps-events:latest"}]
    assert store.path(BRONZE["gfw_fishing"] + ".meta.json").exists()
    assert json.loads(store.read_text(BRONZE["gfw_port_visits"])) == [{"id": "public-global-port-visits-events:latest"}]


def test_registro_y_zee_se_guardan_con_su_fuente(tmp_path):
    store = LocalRawStore(tmp_path)
    fetched = []

    def fake_fetch(url):
        fetched.append(url)
        return b"<html/>" if "registro" in url else b'{"type":"FeatureCollection","features":[]}'

    download_registry(store, fake_fetch)
    download_eez(store, fake_fetch)

    assert store.read_text(BRONZE["registry"]) == "<html/>"
    meta = json.loads(store.path(BRONZE["eez"] + ".meta.json").read_text())
    assert "marineregions" in meta["source"].lower() or "vliz" in meta["source"]
    assert len(fetched) == 2
