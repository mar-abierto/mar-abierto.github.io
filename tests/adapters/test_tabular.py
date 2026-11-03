from datetime import date, datetime, timezone

from openmar.adapters.tabular import read_gaps, read_trips, write_items, write_rows, read_rows
from openmar.domain.model import AisGap, Trip


def test_mareas_ida_y_vuelta_conservan_tipos(tmp_path):
    trips = [Trip("NANINA", 2, True, date(2025, 1, 1), date(2025, 1, 20), 20, 400_000, 20.5)]

    write_items(tmp_path / "mareas.csv", trips)

    assert read_trips(tmp_path / "mareas.csv") == trips


def test_apagones_ida_y_vuelta_con_valores_desconocidos(tmp_path):
    gaps = [
        AisGap(
            "g1", "v", "NANINA", "701",
            datetime(2025, 1, 1, 10, tzinfo=timezone.utc), datetime(2025, 1, 1, 23, tzinfo=timezone.utc),
            13.0, None, 120.5, None, -60.0, True,
        )
    ]

    write_items(tmp_path / "apagones.csv", gaps)

    assert read_gaps(tmp_path / "apagones.csv") == gaps


def test_tabla_vacia_se_puede_escribir_y_leer(tmp_path):
    assert write_rows(tmp_path / "vacio.csv", []) == 0
    assert read_rows(tmp_path / "vacio.csv") == []
