from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class BirthData:
    name: str
    birth_local: str
    birth_timezone: str
    birth_lat: float
    birth_lon: float
    birth_location_label: str = ""

@dataclass(frozen=True)
class DailySnapshot:
    date_local: str
    local_datetime: str | None
    utc_datetime: str | None
    jd_ut: float | None
    positions: dict[str, dict[str, Any]]
    transit_to_transit_aspects: list[dict[str, Any]]
    transit_to_natal_aspects: list[dict[str, Any]]
    reverse_read_candidates: list[dict[str, Any]]

    def as_person_daily_snapshot(self, person: str | None = None, global_source: str | None = None) -> dict[str, Any]:
        return {
            "type": "person_daily_snapshot",
            "person": person,
            "date_local": self.date_local,
            "global_transit_source": global_source,
            "transit_to_natal_aspects": self.transit_to_natal_aspects,
            "reverse_read_candidates": self.reverse_read_candidates,
        }

@dataclass(frozen=True)
class ProviderConfig:
    start: str | None = None
    end: str | None = None
    snapshot_timezone: str = "America/Denver"
    snapshot_time: str = "12:00"
    ephe_path: str = "."
    house_system: str = "P"
    include_minor: bool = True
    top_n_candidates: int = 25
    include_declinations: bool = True
    include_dignities: bool = True
    include_sect: bool = True
    include_antiscia: bool = True
    include_harmonics: bool = True
    harmonic_numbers: tuple[int, ...] = (2, 3, 4, 5, 7, 9)
    include_optional_points: bool = True
    include_asteroids: bool = False
    asteroid_ids: tuple[int, ...] = ()
    include_fixed_stars: bool = False
    fixed_star_names: tuple[str, ...] = ()
