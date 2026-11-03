import pytest

from openmar.normalize import normalize_vessel_name


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("ARBUMASA XXVIII", "ARBUMASA XXVIII"),
        ('" XIN SHI DAI 28 "', "XIN SHI DAI 28"),
        ("## NANINA ##", "NANINA"),
        ("* ARBUMASA XXIX *", "ARBUMASA XXIX"),
        ("75 TAE BAEK", "TAE BAEK 75"),
        ("Nº 75 TAE BAEK", "TAE BAEK 75"),
        ("MISHIMA MARU N°8", "MISHIMA MARU 8"),
        ("MISHIMA MARU N8", "MISHIMA MARU 8"),
        ("HU YU 908", "HUYU 908"),
        ("Natalia", "NATALIA"),
        ("  lu   qing yuan yu 288 ", "LU QING YUAN YU 288"),
    ],
)
def test_normaliza_variantes_de_un_mismo_buque(raw, expected):
    assert normalize_vessel_name(raw) == expected


@pytest.mark.parametrize("raw", [None, "", "   ", "##"])
def test_nombre_vacio_devuelve_cadena_vacia(raw):
    assert normalize_vessel_name(raw) == ""
