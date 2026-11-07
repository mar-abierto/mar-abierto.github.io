import json

from openmar.adapters.filesystem import LocalRawStore
from openmar.application.download import (
    BRONZE,
    active_vessel_ids,
    download_eez,
    download_gfw,
    download_registry,
)


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

    assert stats == {
        "buques": 3,
        "activos": 2,
        "identidades": 2,
        "apagones": 1,
        "eventos_de_pesca": 1,
        "escalas_en_puerto": 1,
    }
    assert all(ids == ["activo", "sin-fecha"] for _, ids in client.requested)
    assert json.loads(store.read_text(BRONZE["gfw_gaps"])) == [{"id": "public-global-gaps-events:latest"}]
    assert store.path(BRONZE["gfw_fishing"] + ".meta.json").exists()
    assert json.loads(store.read_text(BRONZE["gfw_port_visits"])) == [{"id": "public-global-port-visits-events:latest"}]


def identity(vid, desde, hasta):
    return {"id": vid, "transmissionDateFrom": desde, "transmissionDateTo": hasta}


class MultiIdentityClient(FakeClient):
    """Como ESTRELLA 6: la identidad nueva figura primero, pero la vieja transmitió en 2025."""

    def search_vessels(self, where):
        return [
            {
                "selfReportedInfo": [
                    identity("nueva", "2017-04-11T01:00:58Z", "2026-09-08T13:32:09Z"),
                    identity("vieja-2025", "2012-01-26T00:19:50Z", "2025-06-09T14:21:58Z"),
                    identity("muerta", "2010-01-01T00:00:00Z", "2016-12-31T00:00:00Z"),
                    identity("futura", "2026-02-01T00:00:00Z", None),
                ]
            },
            {"selfReportedInfo": [identity("nueva", "2017-04-11T01:00:58Z", "2026-09-08T13:32:09Z")]},
        ]


def test_gfw_consulta_todas_las_identidades_que_se_solapan_con_el_periodo(tmp_path):
    store, client = LocalRawStore(tmp_path), MultiIdentityClient()

    stats = download_gfw(store, client, "2025-01-01", "2025-12-31")

    assert all(ids == ["nueva", "vieja-2025"] for _, ids in client.requested)
    assert stats["activos"] == 2
    assert stats["identidades"] == 2


def test_vessel_ids_activos_ignora_identidades_sin_id_y_fuera_de_periodo():
    entry = {
        "selfReportedInfo": [
            identity("", "2020-01-01", None),
            identity("antes", "2020-01-01", "2024-12-31T23:59:59Z"),
            identity("despues", "2026-01-01T00:00:00Z", "2026-05-01"),
            identity("borde", "2025-12-31T10:00:00Z", None),
            {"id": "sin-fechas"},
        ]
    }

    assert active_vessel_ids(entry, "2025-01-01", "2025-12-31") == ["borde", "sin-fechas"]
    assert active_vessel_ids({}, "2025-01-01", "2025-12-31") == []


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
