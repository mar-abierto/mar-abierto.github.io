from datetime import datetime, timezone

import pytest

from openmar.adapters.gfw import GFWClient, GFWError, parse_gap_event, parse_port_visit


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload


class FakeSession:
    """Devuelve respuestas en orden y registra cada pedido."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": params, "headers": headers})
        return self._responses.pop(0)


def vessel_entry(vessel_id, name):
    return {"selfReportedInfo": [{"id": vessel_id, "shipname": name, "ssvid": "701", "flag": "ARG"}]}


def test_busqueda_de_buques_pagina_y_descarta_repetidos():
    session = FakeSession(
        [
            FakeResponse({"entries": [vessel_entry("a", "UNO"), vessel_entry("b", "DOS")], "since": "p2"}),
            FakeResponse({"entries": [vessel_entry("b", "DOS"), vessel_entry("c", "TRES")], "since": None}),
        ]
    )
    client = GFWClient("token", session=session, page_size=2)

    entries = client.search_vessels("flag='ARG'")

    assert [e["selfReportedInfo"][0]["id"] for e in entries] == ["a", "b", "c"]
    assert session.calls[1]["params"]["since"] == "p2"
    assert session.calls[0]["headers"]["Authorization"] == "Bearer token"


def test_busqueda_corta_cuando_una_pagina_no_trae_buques_nuevos():
    # La API real devuelve páginas llenas con `since` aunque repita buques.
    repeated = {"entries": [vessel_entry("a", "UNO"), vessel_entry("b", "DOS")], "since": "otra"}
    session = FakeSession([FakeResponse(repeated)] * 5)
    client = GFWClient("token", session=session, page_size=2)

    entries = client.search_vessels("flag='ARG'")

    assert len(entries) == 2
    assert len(session.calls) == 2


def test_busqueda_tiene_un_tope_de_paginas():
    pages = [
        FakeResponse({"entries": [vessel_entry(f"{i}a", "X"), vessel_entry(f"{i}b", "Y")], "since": "s"})
        for i in range(10)
    ]
    session = FakeSession(pages)
    client = GFWClient("token", session=session, page_size=2, max_pages=3)

    entries = client.search_vessels("flag='ARG'")

    assert len(session.calls) == 3
    assert len(entries) == 6


def test_eventos_se_piden_en_lotes_y_siguen_next_offset():
    session = FakeSession(
        [
            FakeResponse({"entries": [{"id": "e1"}], "nextOffset": 1}),
            FakeResponse({"entries": [{"id": "e2"}], "nextOffset": None}),
            FakeResponse({"entries": [{"id": "e3"}], "nextOffset": None}),
        ]
    )
    client = GFWClient("token", session=session, batch_size=2)

    events = client.get_events("public-global-gaps-events:latest", ["v1", "v2", "v3"], "2025-01-01", "2025-12-31")

    assert [e["id"] for e in events] == ["e1", "e2", "e3"]
    assert session.calls[0]["params"]["vessels[0]"] == "v1"
    assert session.calls[0]["params"]["vessels[1]"] == "v2"
    assert session.calls[2]["params"]["vessels[0]"] == "v3"


def test_eventos_cortan_si_el_offset_no_avanza():
    session = FakeSession(
        [
            FakeResponse({"entries": [{"id": "e1"}], "nextOffset": 500}),
            FakeResponse({"entries": [{"id": "e2"}], "nextOffset": 500}),
            FakeResponse({"entries": [{"id": "e3"}], "nextOffset": 500}),
        ]
    )
    client = GFWClient("token", session=session)

    events = client.get_events("ds", ["v1"], "2025-01-01", "2025-12-31")

    assert [e["id"] for e in events] == ["e1", "e2"]
    assert len(session.calls) == 2


def test_parse_gap_sin_distancias_deja_none():
    gap = parse_gap_event({"id": "g", "start": "2025-01-01T00:00:00Z", "end": "2025-01-01T13:00:00Z"})

    assert gap.start_km_from_shore is None
    assert gap.lat is None


def test_error_http_se_informa_sin_mostrar_el_token():
    client = GFWClient("secreto", session=FakeSession([FakeResponse({}, status=401)]))

    with pytest.raises(GFWError) as err:
        client.search_vessels("flag='ARG'")

    assert "401" in str(err.value)
    assert "secreto" not in str(err.value)


def test_token_vacio_falla_al_crear_el_cliente():
    with pytest.raises(GFWError):
        GFWClient("")


def test_parse_gap_event():
    raw = {
        "id": "g1",
        "start": "2025-01-12T15:19:03.000Z",
        "end": "2025-01-13T04:57:54.000Z",
        "position": {"lat": -47.0, "lon": -63.7},
        "distances": {"startDistanceFromShoreKm": 204, "endDistanceFromShoreKm": 112},
        "vessel": {"id": "v1", "name": "DON LUIS I", "ssvid": "701000940"},
        "gap": {"durationHours": 13.6, "intentionalDisabling": True},
    }

    gap = parse_gap_event(raw)

    assert gap.event_id == "g1"
    assert gap.vessel_name == "DON LUIS I"
    assert gap.mmsi == "701000940"
    assert gap.start == datetime(2025, 1, 12, 15, 19, 3, tzinfo=timezone.utc)
    assert gap.hours == 13.6
    assert gap.start_km_from_shore == 204
    assert gap.end_km_from_shore == 112
    assert gap.intentional is True


PORT_VISIT = {
    "id": "pv1",
    "start": "2025-02-10T11:00:00.000Z",
    "end": "2025-02-12T23:00:00.000Z",
    "position": {"lat": -34.9, "lon": -56.2},
    "vessel": {"id": "v", "name": "LU QING YUAN YU 279", "ssvid": "701155000", "flag": "ARG"},
    "port_visit": {
        "confidence": "4",
        "durationHrs": 60.0,
        "startAnchorage": {"id": "ury-montevideo", "name": "MONTEVIDEO", "flag": "URY"},
        "endAnchorage": {"id": "ury-montevideo", "name": "MONTEVIDEO", "flag": "URY"},
    },
}


def test_parse_port_visit_toma_puerto_pais_y_confianza():
    visit = parse_port_visit(PORT_VISIT)

    assert visit.event_id == "pv1"
    assert visit.vessel_name == "LU QING YUAN YU 279"
    assert visit.port_name == "MONTEVIDEO"
    assert visit.port_country == "URY"
    assert visit.confidence == 4
    assert visit.port_id == "ury-montevideo"
    assert visit.hours == 60.0
    assert visit.start == datetime(2025, 2, 10, 11, tzinfo=timezone.utc)


def test_parse_port_visit_sin_puerto_deja_vacio():
    raw = {**PORT_VISIT, "port_visit": {"confidence": "2", "durationHrs": 3}}

    visit = parse_port_visit(raw)

    assert (visit.port_name, visit.port_country, visit.confidence) == ("", "", 2)


def test_parse_port_visit_tolera_campos_faltantes():
    raw = {"id": "pv2", "start": "2025-02-10T11:00:00Z", "end": "2025-02-10T12:00:00Z",
           "port_visit": {"durationHrs": None, "startAnchorage": {"id": "arg-x"}}}

    visit = parse_port_visit(raw)

    assert (visit.hours, visit.port_id, visit.vessel_name, visit.lat) == (0.0, "arg-x", "", 0.0)
