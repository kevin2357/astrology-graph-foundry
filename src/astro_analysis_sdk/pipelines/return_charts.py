from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Callable
from zoneinfo import ZoneInfo

from astro_analysis_sdk.common.geometry import angular_distance, normalize
from astro_analysis_sdk.ephemeris.live_natal import datetime_to_jd_ut, planet_position, build_live_natal_chart
from astro_analysis_sdk.ephemeris.models import BirthData, ProviderConfig
from astro_analysis_sdk.pipelines.natal import build as build_natal
from astro_analysis_sdk.common.chart_graph import build_chart_graph


def require_swe(ephe_path: str):
    try:
        import swisseph as swe
    except ImportError as exc:
        raise ImportError("This return/lunation pipeline requires pyswisseph (`pip install pyswisseph`).") from exc
    swe.set_ephe_path(ephe_path)
    return swe


def _body_lon(swe, jd_ut: float, swe_id: int) -> float:
    return float(planet_position(swe, jd_ut, swe_id)["lon"])


def _signed_angle(a: float, b: float) -> float:
    return ((a - b + 180.0) % 360.0) - 180.0


def find_longitude_return(swe, swe_id: int, target_lon: float, guess_dt: datetime, *, search_days: int = 30) -> datetime:
    """Find moment near guess_dt when body returns to target longitude."""
    # Coarse scan finds minimal longitude distance; then local binary/secant-ish refinement.
    best_dt = guess_dt
    best_dist = 999.0
    start = guess_dt - timedelta(days=search_days)
    steps = search_days * 2 * 8
    prev_dt = start
    prev_val = None
    bracket = None
    for i in range(steps + 1):
        dt = start + timedelta(hours=3 * i)
        jd, _ = datetime_to_jd_ut(swe, dt)
        lon = _body_lon(swe, jd, swe_id)
        dist = angular_distance(lon, target_lon)
        if dist < best_dist:
            best_dt, best_dist = dt, dist
        val = _signed_angle(lon, target_lon)
        if prev_val is not None and val * prev_val <= 0 and abs(val - prev_val) < 90:
            bracket = (prev_dt, dt)
            break
        prev_dt, prev_val = dt, val
    if bracket is None:
        # Fall back to the best coarse time; enough for a first-pass pipeline.
        return best_dt
    lo, hi = bracket
    for _ in range(50):
        mid = lo + (hi - lo) / 2
        jd_lo, _ = datetime_to_jd_ut(swe, lo)
        jd_mid, _ = datetime_to_jd_ut(swe, mid)
        v_lo = _signed_angle(_body_lon(swe, jd_lo, swe_id), target_lon)
        v_mid = _signed_angle(_body_lon(swe, jd_mid, swe_id), target_lon)
        if v_lo * v_mid <= 0:
            hi = mid
        else:
            lo = mid
    return lo + (hi - lo) / 2


def find_longitude_returns_in_range(
    swe,
    swe_id: int,
    target_lon: float,
    start_dt: datetime,
    end_dt: datetime,
    *,
    step_hours: int = 6,
) -> list[datetime]:
    """Find every exact longitude return in an inclusive UTC-aware range.

    The scan brackets signed-longitude zero crossings and refines each crossing
    by bisection.  A stable timestamp-based deduplication guard prevents a
    crossing that lands on a scan boundary from being emitted twice.
    """
    if end_dt < start_dt:
        raise ValueError("end_dt must not precede start_dt")
    step = timedelta(hours=step_hours)
    scan_start = start_dt - step
    prev_dt = scan_start
    prev_jd, _ = datetime_to_jd_ut(swe, prev_dt)
    prev_val = _signed_angle(_body_lon(swe, prev_jd, swe_id), target_lon)
    current = scan_start + step
    found: list[datetime] = []
    while current <= end_dt + step:
        jd, _ = datetime_to_jd_ut(swe, current)
        value = _signed_angle(_body_lon(swe, jd, swe_id), target_lon)
        # Ignore the artificial +/-180 discontinuity; true return crossings
        # have a small signed-angle change across the bracket.
        if prev_val * value <= 0 and abs(value - prev_val) < 90:
            lo, hi = prev_dt, current
            for _ in range(50):
                mid = lo + (hi - lo) / 2
                jd_lo, _ = datetime_to_jd_ut(swe, lo)
                jd_mid, _ = datetime_to_jd_ut(swe, mid)
                v_lo = _signed_angle(_body_lon(swe, jd_lo, swe_id), target_lon)
                v_mid = _signed_angle(_body_lon(swe, jd_mid, swe_id), target_lon)
                if v_lo * v_mid <= 0:
                    hi = mid
                else:
                    lo = mid
            event = lo + (hi - lo) / 2
            if start_dt <= event <= end_dt:
                if not found or abs((event - found[-1]).total_seconds()) > 60:
                    found.append(event)
        prev_dt, prev_val = current, value
        current += step
    return found

def cast_return_chart(
    name: str,
    event_dt: datetime,
    timezone: str,
    lat: float,
    lon: float,
    location_label: str,
    ephe_path: str,
    house_system: str,
    *,
    compact: bool = False,
) -> dict[str, Any]:
    local = event_dt.astimezone(ZoneInfo(timezone))
    birth_local = local.replace(tzinfo=None).isoformat(timespec="seconds")
    if not compact:
        return build_natal(
            provider="live",
            name=name,
            birth_local=birth_local,
            birth_timezone=timezone,
            birth_lat=lat,
            birth_lon=lon,
            birth_location_label=location_label,
            ephe_path=ephe_path,
            house_system=house_system,
        )

    # Range-based lunar-return packages may contain ~20 charts per target.
    # Use a core chart profile so the package remains practical while still
    # preserving planets, angles, houses, aspects, dignities, sect, and a
    # compact semantic graph.
    chart = build_live_natal_chart(
        BirthData(
            name=name,
            birth_local=birth_local,
            birth_timezone=timezone,
            birth_lat=lat,
            birth_lon=lon,
            birth_location_label=location_label,
        ),
        ProviderConfig(
            ephe_path=ephe_path,
            house_system=house_system,
            include_minor=True,
            include_declinations=True,
            include_dignities=True,
            include_sect=True,
            include_antiscia=False,
            include_harmonics=False,
            include_optional_points=True,
            include_fixed_stars=False,
        ),
    )
    graph = build_chart_graph(chart)
    chart["semantic_graph"] = graph
    return {
        "metadata": {
            "analysis_type": "compact_return_chart",
            "person": name,
            "return_chart_profile": "core_semantic_v1",
        },
        "natal": chart,
        "semantic_graph": graph,
    }
