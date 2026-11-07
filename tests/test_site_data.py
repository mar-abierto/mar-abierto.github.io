"""Los datos publicados en site/data dan la misma cifra de cortes en todas las páginas."""

import json
from pathlib import Path

import pytest

from openmar.domain.coherence import gap_count_problems

SITE_DATA = Path(__file__).resolve().parents[1] / "site" / "data"


@pytest.mark.skipif(not (SITE_DATA / "resumen.json").exists(), reason="sitio sin datos publicados")
def test_site_data_cifra_de_cortes_coherente():
    summary = json.loads((SITE_DATA / "resumen.json").read_text(encoding="utf-8"))
    fichas = json.loads((SITE_DATA / "fichas.json").read_text(encoding="utf-8"))

    assert gap_count_problems(summary, fichas) == []
