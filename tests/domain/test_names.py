import pytest

from openmar.domain.names import normalize_vessel_name


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
        ("SHU YU 12", "SHU YU 12"),
        ("Natalia", "NATALIA"),
        ("  lu   qing yuan yu 288 ", "LU QING YUAN YU 288"),
    ],
)
def test_normaliza_variantes_de_un_mismo_buque(raw, expected):
    assert normalize_vessel_name(raw) == expected


@pytest.mark.parametrize("raw", [None, "", "   ", "##"])
def test_nombre_vacio_devuelve_cadena_vacia(raw):
    assert normalize_vessel_name(raw) == ""


from openmar.domain.names import vessel_key


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("VIEIRASA DIECIOCHO", "VIEIRASA 18"),
        ("VIEIRASA DIECISIETE", "VIEIRASA 17"),
        ("DON FRANCISCO I", "DON FRANCISCO 1"),
        ("ARBUMASA XXVIII", "ARBUMASA 28"),
        ("ESTRELLA 11", "ESTRELLA N 11"),
        ("TAISEI MARU 8", "TAISEI MARU N 8"),
        ("LU QING YUAN YU 278", "LUQING YUAN YU 278"),
    ],
)
def test_clave_de_comparacion_une_variantes(a, b):
    assert vessel_key(a) == vessel_key(b)


def test_clave_no_confunde_buques_distintos():
    assert vessel_key("ARBUMASA XXVIII") != vessel_key("ARBUMASA XXVII")
    assert vessel_key("MINTA") != vessel_key("MINTA I")
    assert vessel_key("ORION 3") != vessel_key("ORION 5")


def test_clave_solo_convierte_el_ultimo_numero():
    # "VIEIRASA" no tiene numeral romano; "MIX" al final sí se lee como 1009 sin querer
    assert vessel_key("DOMAIO") == "DOMAIO"
    assert vessel_key("HUYU 908") == "HUYU 908"


@pytest.mark.parametrize(("a", "b"), [("CÓNDOR", "CONDOR"), ("NIÑO", "NINO"), ("Dieciséis", "DIECISEIS")])
def test_acentos_y_enie_no_parten_el_nombre(a, b):
    assert normalize_vessel_name(a) == normalize_vessel_name(b)


def test_numero_en_letras_con_tilde():
    assert vessel_key("ESTRELLA DIECISÉIS") == "ESTRELLA 16"
