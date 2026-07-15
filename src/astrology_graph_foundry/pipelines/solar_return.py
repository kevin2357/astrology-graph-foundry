from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from astrology_graph_foundry.common.transitable_chart import from_package
from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary
from astrology_graph_foundry.common.return_location import resolve_return_location
from astrology_graph_foundry.pipelines.return_charts import cast_return_chart, find_longitude_return, require_swe

SCHEMA_VERSION = "2.0.0"
PIPELINE_VERSION = "solar_return_pipeline_v2.0.0_transitable_chart"


def _reference_datetime(target) -> datetime:
    ref = target.reference_event
    if ref.get("event_utc"):
        return datetime.fromisoformat(str(ref["event_utc"]).replace("Z", "+00:00")).astimezone(timezone.utc)
    if ref.get("event_local"):
        tz = ZoneInfo(str(ref.get("timezone") or "UTC"))
        return datetime.fromisoformat(str(ref["event_local"])).replace(tzinfo=tz)
    raise ValueError(
        f"Solar return requires a reference event for target chart type {target.chart_type!r}. "
        "Natal and Davison charts provide real events; composite packages must include composite_reference_event."
    )


def build(
    *,
    target_dataset: str | dict[str, Any],
    return_year: int,
    return_location_policy: str,
    location_timezone: str | None = None,
    location_lat: float | None = None,
    location_lon: float | None = None,
    location_label: str | None = None,
    ephe_path: str = ".",
    house_system: str = "P",
) -> dict[str, Any]:
    target = from_package(target_dataset)
    swe = require_swe(ephe_path)
    sun = target.chart.get("bodies", {}).get("nSun") or target.chart.get("bodies", {}).get("Sun")
    if not sun or sun.get("lon") is None:
        raise ValueError("Solar return requires a target Sun longitude in the TransitableChart.")

    reference_dt = _reference_datetime(target)
    try:
        guess = reference_dt.replace(year=int(return_year))
    except ValueError:
        guess = reference_dt.replace(year=int(return_year), day=28)
    event_dt = find_longitude_return(swe, swe.SUN, float(sun["lon"]), guess, search_days=4)

    resolved_location = resolve_return_location(
        target=target,
        return_location_policy=return_location_policy,
        location_timezone=location_timezone,
        location_lat=location_lat,
        location_lon=location_lon,
        location_label=location_label,
    )
    tz = resolved_location["timezone"]
    lat = resolved_location["lat"]
    lon = resolved_location["lon"]
    label = resolved_location["location_label"]
    chart_pkg = cast_return_chart(
        f"Solar Return {return_year}: {target.label}",
        event_dt,
        tz,
        lat,
        lon,
        str(label),
        ephe_path,
        house_system,
    )
    semantic_scope = {
        "natal": "individual_annual_climate",
        "composite": "relationship_pattern_annual_climate",
        "davison": "relationship_lifecycle_annual_climate",
    }.get(target.chart_type, "chart_annual_climate")
    package = {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "analysis_type": "solar_return_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "target_label": target.label,
            "target_chart_id": target.chart_id,
            "target_chart_type": target.chart_type,
            "target_subject_scope": target.subject_scope,
            "semantic_scope": semantic_scope,
            "return_year": return_year,
            "return_location_policy": return_location_policy,
        },
        "target": {
            "chart_identity": {
                "chart_id": target.chart_id,
                "chart_type": target.chart_type,
                "subject_scope": target.subject_scope,
                "label": target.label,
            },
            "construction": target.construction,
            "reference_event": target.reference_event,
        },
        "return_location": resolved_location,
        "return_event": {
            "event_utc": event_dt.astimezone(timezone.utc).isoformat(),
            "event_local": event_dt.astimezone(ZoneInfo(tz)).isoformat(),
            "target_sun_longitude": float(sun["lon"]),
            "method": "exact transiting Sun return to TransitableChart Sun longitude via Swiss Ephemeris root search",
            "interpretive_note": {
                "natal": (
                    "The birth event anchors the annual recurrence. The transiting Sun is returned exactly "
                    "to the natal Sun longitude; return-chart houses depend on the selected return location."
                ),
                "composite": (
                    "The explicitly labeled synthetic midpoint reference event anchors the annual recurrence. "
                    "The transiting Sun is returned exactly to the composite Sun longitude; return-chart houses "
                    "depend on the selected return location."
                ),
                "davison": (
                    "The real Davison midpoint event anchors the annual recurrence. The transiting Sun is returned "
                    "exactly to the Davison Sun longitude; return-chart houses depend on the selected return location."
                ),
            }.get(
                target.chart_type,
                "The target reference event anchors the annual recurrence; return-chart houses depend on the selected return location.",
            ),
        },
        "return_chart": chart_pkg.get("natal", chart_pkg),
        "semantic_graph": (
            chart_pkg.get("canonical_astrology_graph")
            or chart_pkg.get("natal", {}).get("semantic_graph")
        ),
        "report_materials": {
            "recommended_sections": [
                "Solar Return Executive Summary",
                "Target Chart Context",
                "Return Ascendant and Chart Ruler",
                "Return Sun House",
                "Return Moon",
                "Dominant Aspects",
                "Annual Climate Synthesis",
            ]
        },
    } 
    return finalize_package_semantic_boundary(package)
