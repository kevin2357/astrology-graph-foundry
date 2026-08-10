from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from astrology_graph_foundry.common.identity import validate_source_chart_id


@dataclass(frozen=True)
class BirthData:
    name: str
    birth_local: str
    birth_timezone: str
    birth_lat: float
    birth_lon: float
    birth_location_label: str = ""
    source_chart_id: str | None = None

    def __post_init__(self) -> None:
        validate_source_chart_id(self.source_chart_id)


BOUNDED_BIRTH_TIME_MAX_HOURS = 48.0
BirthTimeMode = Literal["exact", "bounded", "unknown_time"]


@dataclass(frozen=True)
class BirthTimeBasis:
    mode: BirthTimeMode
    birth_local: str | None = None
    earliest_local: str | None = None
    latest_local: str | None = None
    birth_date: str | None = None
    earliest_utc: str | None = None
    latest_utc: str | None = None


@dataclass(frozen=True)
class NormalizedBirthTimeBasis:
    mode: BirthTimeMode
    supplied: dict[str, str]
    start_local: str
    end_local: str
    start_utc: str
    end_utc: str
    boundary_policy: str
    duration_hours: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "supplied": dict(self.supplied),
            "normalized": {
                "start_local": self.start_local,
                "end_local": self.end_local,
                "start_utc": self.start_utc,
                "end_utc": self.end_utc,
                "boundary_policy": self.boundary_policy,
                "duration_hours": self.duration_hours,
            },
        }


def _parse_naive_local(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a valid local ISO datetime") from exc
    if parsed.tzinfo is not None:
        raise ValueError(f"{field} must not include a UTC offset or timezone")
    return parsed


def _parse_utc(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"{field} must be a valid offset-aware UTC ISO datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _unique_local_instant(local: datetime, zone: ZoneInfo, field: str) -> datetime:
    candidates: dict[datetime, datetime] = {}
    for fold in (0, 1):
        aware = local.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(timezone.utc)
        round_trip = utc.astimezone(zone)
        if round_trip.replace(tzinfo=None) == local:
            candidates[utc] = aware
    if not candidates:
        raise ValueError(f"{field} is a nonexistent local wall time in {zone.key}")
    if len(candidates) > 1:
        raise ValueError(f"{field} is an ambiguous local wall time in {zone.key}; an explicit fold contract is not supported")
    return next(iter(candidates.values()))


def _validate_resolved_utc(supplied: str | None, actual: datetime, field: str) -> None:
    if supplied is None:
        return
    if _parse_utc(supplied, field) != actual.astimezone(timezone.utc):
        raise ValueError(f"{field} does not match the local datetime and IANA timezone")


def normalize_birth_time_basis(
    basis: BirthTimeBasis,
    birth_timezone: str,
    *,
    max_bounded_hours: float = BOUNDED_BIRTH_TIME_MAX_HOURS,
) -> NormalizedBirthTimeBasis:
    try:
        zone = ZoneInfo(birth_timezone)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise ValueError("birth_timezone must be a valid IANA timezone") from exc

    if basis.mode == "exact":
        if not basis.birth_local or any(
            value is not None
            for value in (basis.earliest_local, basis.latest_local, basis.birth_date, basis.earliest_utc, basis.latest_utc)
        ):
            raise ValueError("exact birth_time_basis requires only birth_local")
        local = _parse_naive_local(basis.birth_local, "birth_local")
        aware = _unique_local_instant(local, zone, "birth_local")
        utc = aware.astimezone(timezone.utc)
        return NormalizedBirthTimeBasis(
            mode="exact",
            supplied={"birth_local": basis.birth_local},
            start_local=local.isoformat(),
            end_local=local.isoformat(),
            start_utc=utc.isoformat(),
            end_utc=utc.isoformat(),
            boundary_policy="point",
            duration_hours=0.0,
        )

    if basis.birth_local is not None:
        raise ValueError(f"{basis.mode} birth_time_basis cannot include birth_local")

    if basis.mode == "bounded":
        if not basis.earliest_local or not basis.latest_local or basis.birth_date is not None:
            raise ValueError("bounded birth_time_basis requires earliest_local and latest_local only")
        start_local = _parse_naive_local(basis.earliest_local, "earliest_local")
        end_local = _parse_naive_local(basis.latest_local, "latest_local")
        start = _unique_local_instant(start_local, zone, "earliest_local")
        end = _unique_local_instant(end_local, zone, "latest_local")
        _validate_resolved_utc(basis.earliest_utc, start, "earliest_utc")
        _validate_resolved_utc(basis.latest_utc, end, "latest_utc")
        boundary_policy = "inclusive"
        supplied = {"earliest_local": basis.earliest_local, "latest_local": basis.latest_local}
    elif basis.mode == "unknown_time":
        if not basis.birth_date or any(value is not None for value in (basis.earliest_local, basis.latest_local)):
            raise ValueError("unknown_time birth_time_basis requires only birth_date")
        try:
            local_date = date.fromisoformat(basis.birth_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("birth_date must be a valid ISO calendar date") from exc
        start_local = datetime.combine(local_date, datetime.min.time())
        end_local = datetime.combine(local_date + timedelta(days=1), datetime.min.time())
        start = _unique_local_instant(start_local, zone, "birth_date start")
        end = _unique_local_instant(end_local, zone, "birth_date end")
        _validate_resolved_utc(basis.earliest_utc, start, "earliest_utc")
        _validate_resolved_utc(basis.latest_utc, end, "latest_utc")
        boundary_policy = "local_date_start_inclusive_next_date_start_exclusive"
        supplied = {"birth_date": basis.birth_date}
    else:
        raise ValueError("birth_time_basis mode must be one of: exact, bounded, unknown_time")

    start_utc = start.astimezone(timezone.utc)
    end_utc = end.astimezone(timezone.utc)
    duration_hours = (end_utc - start_utc).total_seconds() / 3600
    if duration_hours <= 0:
        raise ValueError("bounded birth time must have positive duration; use exact mode for one instant")
    if duration_hours > max_bounded_hours:
        raise ValueError(f"bounded birth time cannot exceed {max_bounded_hours:g} elapsed UTC hours")
    return NormalizedBirthTimeBasis(
        mode=basis.mode,
        supplied=supplied,
        start_local=start_local.isoformat(),
        end_local=end_local.isoformat(),
        start_utc=start_utc.isoformat(),
        end_utc=end_utc.isoformat(),
        boundary_policy=boundary_policy,
        duration_hours=duration_hours,
    )


@dataclass(frozen=True)
class BoundedBirthData:
    name: str
    birth_time_basis: BirthTimeBasis
    birth_timezone: str
    birth_lat: float
    birth_lon: float
    birth_location_label: str = ""
    source_chart_id: str | None = None
    resolved_birth_time_basis: NormalizedBirthTimeBasis | None = None

    def __post_init__(self) -> None:
        validate_source_chart_id(self.source_chart_id)
        if not self.name or not self.name.strip():
            raise ValueError("name must not be empty")
        if not math.isfinite(float(self.birth_lat)) or not (-90 <= float(self.birth_lat) <= 90):
            raise ValueError("birth_lat must be between -90 and 90 degrees")
        if not math.isfinite(float(self.birth_lon)) or not (-180 <= float(self.birth_lon) <= 180):
            raise ValueError("birth_lon must be between -180 and 180 degrees")
        if self.birth_time_basis.mode == "exact":
            raise ValueError("BoundedBirthData accepts bounded or unknown_time; use BirthData for exact input")
        normalized = normalize_birth_time_basis(self.birth_time_basis, self.birth_timezone)
        object.__setattr__(self, "resolved_birth_time_basis", normalized)

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
    ephemeris_mode: str = "auto"
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

    def __post_init__(self) -> None:
        if self.ephemeris_mode not in {"auto", "swiss", "moshier"}:
            raise ValueError("ephemeris_mode must be one of: auto, swiss, moshier")
