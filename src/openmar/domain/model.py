"""Modelo del dominio: conceptos del mar, independientes de cualquier fuente."""

from dataclasses import dataclass
from datetime import date, datetime

from openmar.domain.names import normalize_vessel_name


@dataclass(frozen=True)
class Trip:
    """Una marea (viaje de pesca) de un buque."""

    vessel: str
    trip: int
    observer: bool
    start: date
    end: date
    days: int
    catch_kg: int
    rate_t_per_day: float


@dataclass(frozen=True)
class Coverage:
    """Viajes de un buque con y sin observador en un período."""

    vessel: str
    trips: int
    with_observer: int
    without_observer: int
    pct_with_observer: float


@dataclass(frozen=True)
class YearlyCoverage:
    """Viajes de un buque con y sin observador en un año."""

    vessel: str
    year: int
    with_observer: int
    without_observer: int


@dataclass(frozen=True)
class AisGap:
    """Un apagón de AIS: el buque dejó de transmitir su posición."""

    event_id: str
    vessel_id: str
    vessel_name: str
    mmsi: str
    start: datetime
    end: datetime
    hours: float
    start_km_from_shore: float | None
    end_km_from_shore: float | None
    lat: float | None
    lon: float | None
    intentional: bool


@dataclass(frozen=True)
class FishingEvent:
    """Un tramo en el que el comportamiento del buque indica pesca."""

    event_id: str
    vessel_name: str
    mmsi: str
    start: datetime
    lat: float
    lon: float


@dataclass(frozen=True)
class RegistryRecord:
    """Un buque en el registro de la flota: matrícula, armador, permiso y sanciones."""

    vessel: str
    registration: str
    technical: str
    fleet_type: str
    owner: str
    permit: str
    permit_date: str
    authorization: str
    sanctions: str
    sanction_dates: str
    citc: str

    @property
    def normalized_name(self) -> str:
        return normalize_vessel_name(self.vessel)

    @property
    def is_squid_jigger(self) -> bool:
        return "POTER" in self.technical.upper() or "CALAMAR" in self.authorization.upper()


@dataclass(frozen=True)
class PortVisit:
    """Una escala en puerto detectada por AIS. No dice qué se hizo ahí."""

    event_id: str
    vessel_name: str
    mmsi: str
    start: datetime
    end: datetime
    hours: float
    port_name: str
    port_country: str
    confidence: int
    lat: float
    lon: float
    port_id: str = ""
