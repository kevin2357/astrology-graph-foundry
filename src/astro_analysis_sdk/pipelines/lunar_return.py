from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from astro_analysis_sdk.common.transitable_chart import from_package
from astro_analysis_sdk.common.semantic_layers import finalize_package_semantic_boundary
from astro_analysis_sdk.common.return_location import resolve_return_location
from astro_analysis_sdk.pipelines.return_charts import (
    cast_return_chart,
    find_longitude_returns_in_range,
    require_swe,
)

SCHEMA_VERSION = "2.0.0"
PIPELINE_VERSION = "lunar_return_pipeline_v2.0.0_transitable_chart_range"



def build(
    *,
    target_dataset: str | dict[str, Any],
    start: str,
    end: str,
    return_location_policy: str,
    location_timezone: str | None = None,
    location_lat: float | None = None,
    location_lon: float | None = None,
    location_label: str | None = None,
    ephe_path: str = ".",
    house_system: str = "P",
) -> dict[str, Any]:
    target = from_package(target_dataset)
    moon = target.chart.get("bodies", {}).get("nMoon") or target.chart.get("bodies", {}).get("Moon")
    if not moon or moon.get("lon") is None:
        raise ValueError("Lunar return requires a target Moon longitude in the TransitableChart.")

    start_dt = datetime.fromisoformat(start[:10] + "T00:00:00+00:00").astimezone(timezone.utc)
    end_dt = datetime.fromisoformat(end[:10] + "T23:59:59+00:00").astimezone(timezone.utc)
    if end_dt < start_dt:
        raise ValueError("lunar-return --end must not precede --start")

    swe = require_swe(ephe_path)
    events = find_longitude_returns_in_range(
        swe, swe.MOON, float(moon["lon"]), start_dt, end_dt, step_hours=6
    )
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
    semantic_scope = {
        "natal": "individual_monthly_climate",
        "composite": "relationship_pattern_monthly_climate",
        "davison": "relationship_lifecycle_monthly_climate",
    }.get(target.chart_type, "chart_monthly_climate")

    returns = []
    for index, event_dt in enumerate(events, 1):
        chart_pkg = cast_return_chart(
            f"Lunar Return {index}: {target.label}",
            event_dt,
            tz,
            lat,
            lon,
            label,
            ephe_path,
            house_system,
            compact=True,
        )
        returns.append({
            "return_id": f"lunar_return:{target.chart_id}:{event_dt.strftime('%Y%m%dT%H%M%SZ')}",
            "sequence": index,
            "return_event": {
                "event_utc": event_dt.astimezone(timezone.utc).isoformat(),
                "event_local": event_dt.astimezone(ZoneInfo(tz)).isoformat(),
                "target_moon_longitude": float(moon["lon"]),
                "method": "exact transiting Moon return to TransitableChart Moon longitude via bracketed Swiss Ephemeris root search",
            },
            "return_chart": chart_pkg.get("natal", chart_pkg),
            "semantic_graph": chart_pkg.get("natal", {}).get("semantic_graph"),
        })

    package = {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "analysis_type": "lunar_return_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "target_label": target.label,
            "target_chart_id": target.chart_id,
            "target_chart_type": target.chart_type,
            "target_subject_scope": target.subject_scope,
            "semantic_scope": semantic_scope,
            "start": start,
            "end": end,
            "return_count": len(returns),
            "return_chart_profile": "core_semantic_v1",
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
        "period": {"start": start, "end": end},
        "returns": returns,
        "indexes": {
            "returns_by_id": {row["return_id"]: i for i, row in enumerate(returns)},
            "returns_by_month": {
                month: [row["return_id"] for row in returns if row["return_event"]["event_utc"][:7] == month]
                for month in sorted({row["return_event"]["event_utc"][:7] for row in returns})
            },
        },
        "report_materials": {
            "recommended_sections": [
                "Monthly Emotional Weather",
                "Return Moon House",
                "Return Ascendant",
                "Dominant Aspects",
                "Month-to-Month Arc",
                "Practical Timing Notes",
            ],
            "return_refs": [row["return_id"] for row in returns],
        },
    } 
    return finalize_package_semantic_boundary(package)
