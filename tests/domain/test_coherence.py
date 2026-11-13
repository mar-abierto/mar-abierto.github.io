"""La misma cifra de cortes por barco en todas las páginas (auditoría, punto 5)."""

import copy

from openmar.domain.coherence import gap_count_problems


def vessel(name, owner, total, sin=0, con=0, fuera=0, sin_mareas=0):
    return {
        "buque": name, "armador": owner, "apagones": total, "en_marea_sin_observador": sin,
        "en_marea_con_observador": con, "fuera_de_marea": fuera, "sin_mareas_del_buque": sin_mareas,
    }


def data():
    tae = vessel("BARCO UNO 75", "ARMADOR A", 18, sin=13, fuera=5)
    arb = vessel("BARCO DOS XXVIII", "ARMADOR B", 14, sin=7, con=7)
    fichas = {"buques": {"BARCO UNO 75": {"datos": tae}, "BARCO DOS 28": {"datos": arb}}}
    summary = {
        "apagones": 32,
        "apagones_por_estado": {"en_marea_sin_observador": 20, "en_marea_con_observador": 7, "fuera_de_marea": 5,
                                "sin_mareas_del_buque": 0},
        "relato": {"senales_repetidas": [dict(tae), dict(arb)]},
        "tablero": {"por_armador": [
            {"armador": "ARMADOR A", "apagones": 18, "en_marea_sin_observador": 13, "en_marea_con_observador": 0,
             "fuera_de_marea": 5, "sin_mareas_del_buque": 0},
            {"armador": "ARMADOR B", "apagones": 14, "en_marea_sin_observador": 7, "en_marea_con_observador": 7,
             "fuera_de_marea": 0, "sin_mareas_del_buque": 0},
        ]},
    }
    return summary, fichas


def test_datos_coherentes_no_tienen_problemas():
    summary, fichas = data()

    assert gap_count_problems(summary, fichas) == []


def test_detecta_un_desglose_que_no_suma_el_total():
    summary, fichas = data()
    fichas["buques"]["BARCO UNO 75"]["datos"]["fuera_de_marea"] = 0

    problems = gap_count_problems(summary, fichas)

    assert any("BARCO UNO 75" in p and "desglose" in p for p in problems)


def test_detecta_un_barco_con_otra_cifra_en_la_historia():
    summary, fichas = data()
    summary["relato"]["senales_repetidas"][0]["apagones"] = 13

    assert any("historia" in p and "BARCO UNO 75" in p for p in gap_count_problems(summary, fichas))


def test_detecta_una_empresa_que_no_suma_sus_barcos():
    summary, fichas = data()
    summary["tablero"]["por_armador"][0]["apagones"] = 13

    assert any("ARMADOR A" in p for p in gap_count_problems(summary, fichas))


def test_detecta_un_desglose_de_empresa_distinto_de_sus_barcos():
    summary, fichas = data()
    summary["tablero"]["por_armador"][0]["en_marea_sin_observador"] = 18
    summary["tablero"]["por_armador"][0]["fuera_de_marea"] = 0

    assert any("ARMADOR A" in p for p in gap_count_problems(summary, fichas))


def test_detecta_un_total_de_flota_distinto_de_la_suma_de_barcos():
    summary, fichas = data()
    summary["apagones"] = 30

    assert any("flota" in p for p in gap_count_problems(summary, fichas))


def test_detecta_un_desglose_de_flota_que_no_suma_el_total():
    summary, fichas = data()
    summary["apagones_por_estado"]["fuera_de_marea"] = 0

    assert any("flota" in p for p in gap_count_problems(summary, fichas))


def test_acepta_tablero_sin_desglose_de_una_version_anterior():
    summary, fichas = data()
    old = copy.deepcopy(summary)
    for owner in old["tablero"]["por_armador"]:
        for key in ("en_marea_con_observador", "fuera_de_marea", "sin_mareas_del_buque"):
            del owner[key]
        owner["apagones_sin_observador"] = owner.pop("en_marea_sin_observador")

    assert gap_count_problems(old, fichas) == []
