import pytest

from openmar.domain.matching import STATUS_NO_TRIP, STATUS_WITH_OBSERVER, STATUS_WITHOUT_OBSERVER
from openmar.domain.signals import GREEN, RED, YELLOW, classify


def counts(total=0, without=0, with_obs=0, no_trip=0):
    return {
        "apagones": total,
        STATUS_WITHOUT_OBSERVER: without,
        STATUS_WITH_OBSERVER: with_obs,
        STATUS_NO_TRIP: no_trip,
    }


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (counts(), GREEN),
        (counts(total=1, without=1), YELLOW),
        (counts(total=2, without=1, no_trip=1), YELLOW),
        (counts(total=4, with_obs=4), YELLOW),
        (counts(total=3, without=3), RED),
        (counts(total=18, without=13, no_trip=5), RED),
        (counts(total=3, without=2, no_trip=1), RED),
    ],
)
def test_semaforo_segun_apagones_sin_observador(data, expected):
    assert classify(data) == expected


def test_buque_sin_resumen_es_verde():
    assert classify({}) == GREEN
