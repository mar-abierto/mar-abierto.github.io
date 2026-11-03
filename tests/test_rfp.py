from openmar.sources.rfp import parse_registry_html

HTML = """
<html><body><table>
<tr><th>Nombre embarcación</th><th>Matricula</th><th>Datos técnicos /Arte de peca/eslora</th>
<th>Tipo de flota</th><th>Propietario/armador</th><th>Permiso</th><th>Fecha</th>
<th>Autorización</th><th>Sanciones</th><th>Fecha sanción</th><th>CITC</th><th></th></tr>
<tr><td>Nº 75 TAE BAEK</td><td>2364</td><td>POTEROS / 60.0</td><td>CONGELADOR</td>
<td>ILLEX FISHING S.A.</td><td>Res.514/09</td><td>01/09/2024</td>
<td>AUTORIZA UNICAMENTE LA CAPTURA DE CALAMAR CON SISTEMA DE POTERAS</td><td></td><td></td><td></td><td></td></tr>
<tr><td>ESTHER 153</td><td>2058</td><td>POTEROS / 55.0</td><td>CONGELADOR</td>
<td>ARMADORES PESQUEROS PATAGONICOS M.C.I. S.A.</td><td>Res.514/09</td><td>01/01/2020</td>
<td>CALAMAR</td><td>193; 180</td><td>15/11/2021; 22/07/2022</td><td></td><td></td></tr>
<tr><td>MERLUCERO &amp; CIA</td><td>9999</td><td>ARRASTRE / 40.0</td><td>FRESQUERO</td>
<td>OTRA S.A.</td><td></td><td></td><td>MERLUZA</td><td></td><td></td><td>SI</td><td></td></tr>
<tr><td></td><td></td></tr>
</table></body></html>
"""


def test_lee_una_entrada_por_buque_y_omite_encabezado_y_filas_vacias():
    entries = parse_registry_html(HTML)

    assert [e.vessel for e in entries] == ["Nº 75 TAE BAEK", "ESTHER 153", "MERLUCERO & CIA"]


def test_conserva_armador_matricula_y_sanciones():
    esther = parse_registry_html(HTML)[1]

    assert esther.registration == "2058"
    assert esther.owner == "ARMADORES PESQUEROS PATAGONICOS M.C.I. S.A."
    assert esther.sanctions == "193; 180"
    assert esther.sanction_dates == "15/11/2021; 22/07/2022"


def test_detecta_poteros():
    flags = [e.is_squid_jigger for e in parse_registry_html(HTML)]

    assert flags == [True, True, False]


def test_nombre_normalizado_para_cruzar():
    assert parse_registry_html(HTML)[0].normalized_name == "TAE BAEK 75"
