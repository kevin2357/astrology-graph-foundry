from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from astrology_graph_foundry.common.aspects import find_aspect
from astrology_graph_foundry.common.geometry import angular_distance, format_zodiac, normalize
from astrology_graph_foundry.common.graph_compiler import GraphCompiler
from astrology_graph_foundry.common.themes import theme_tags
from astrology_graph_foundry.common.transitable_chart import from_package
from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary
from astrology_graph_foundry.ephemeris.live_natal import datetime_to_jd_ut, planet_position
from astrology_graph_foundry.pipelines.return_charts import require_swe

SCHEMA_VERSION = "2.0.0"
PIPELINE_VERSION = "eclipse_lunation_pipeline_v2.0.0_transitable_chart"


def _phase_value(swe, jd: float) -> float:
    sun = planet_position(swe, jd, swe.SUN)["lon"]
    moon = planet_position(swe, jd, swe.MOON)["lon"]
    return normalize(moon - sun)


def _phase_error(value: float, target: float) -> float:
    return ((value - target + 180.0) % 360.0) - 180.0


def _node_distance(swe, jd: float, luminary_lon: float) -> float:
    node = planet_position(swe, jd, swe.TRUE_NODE)["lon"]
    return min(angular_distance(luminary_lon, node), angular_distance(luminary_lon, normalize(node + 180)))


def _refine_phase(swe, lo: datetime, hi: datetime, target: float) -> datetime:
    for _ in range(50):
        mid = lo + (hi - lo) / 2
        jd_lo, _ = datetime_to_jd_ut(swe, lo)
        jd_mid, _ = datetime_to_jd_ut(swe, mid)
        if _phase_error(_phase_value(swe, jd_lo), target) * _phase_error(_phase_value(swe, jd_mid), target) <= 0:
            hi = mid
        else:
            lo = mid
    return lo + (hi - lo) / 2


def _eclipse_classification(event_type: str, node_distance: float) -> dict[str, Any]:
    if node_distance <= 6.0:
        proximity = "strong"
    elif node_distance <= 12.0:
        proximity = "moderate"
    elif node_distance <= 18.0:
        proximity = "near_node"
    else:
        proximity = "ordinary_lunation"
    is_window = node_distance <= 18.0
    eclipse_type = None
    if is_window:
        eclipse_type = "solar_eclipse_window" if event_type == "new_moon" else "lunar_eclipse_window"
    return {
        "is_eclipse_window": is_window,
        "eclipse_type": eclipse_type,
        "eclipse_proximity": proximity,
        "classification_method": "lunation distance to true lunar node; identifies eclipse-season windows but not visibility or exact global eclipse subtype",
    }


def _target_aspects(compiler: GraphCompiler | None, lon: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if compiler is None:
        return [], []
    out: list[dict[str, Any]] = []
    for target in compiler.targets:
        asp = find_aspect("lunation", lon, target.name, target.longitude, include_minor=True)
        if not asp:
            continue
        out.append({
            "target": target.source_key if target.source_key.startswith("n") else f"n{target.name}",
            "target_id": target.id,
            "target_name": target.name,
            "target_type": target.object_type,
            "target_lon": target.longitude,
            "target_house": target.house,
            **asp,
            "theme_tags": theme_tags("lunation", target.name, target.house, aspect=asp.get("aspect")),
        })
    all_rows = sorted(
        out,
        key=lambda r: (
            not bool(r.get("major")),
            float(r.get("orb", 99)),
            str(r.get("target_id")),
            str(r.get("aspect")),
        ),
    )
    return all_rows, all_rows[:30]


def build(
    *,
    start: str,
    end: str,
    target_dataset: str | dict[str, Any] | None = None,
    ephe_path: str = ".",
) -> dict[str, Any]:
    swe = require_swe(ephe_path)
    target = from_package(target_dataset) if target_dataset is not None else None
    compiler = GraphCompiler(target.chart) if target is not None else None

    start_dt = datetime.fromisoformat(start[:10] + "T00:00:00").replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end[:10] + "T23:59:59").replace(tzinfo=timezone.utc)
    if end_dt < start_dt:
        raise ValueError("eclipse-lunation --end must not precede --start")

    events: list[dict[str, Any]] = []
    prev_dt = start_dt
    prev_phase = _phase_value(swe, datetime_to_jd_ut(swe, prev_dt)[0])
    prev_vals = {0.0: _phase_error(prev_phase, 0.0), 180.0: _phase_error(prev_phase, 180.0)}
    dt = start_dt + timedelta(hours=12)

    while dt <= end_dt + timedelta(days=1):
        jd, _ = datetime_to_jd_ut(swe, dt)
        phase = _phase_value(swe, jd)
        for phase_target, event_type in ((0.0, "new_moon"), (180.0, "full_moon")):
            val = _phase_error(phase, phase_target)
            if prev_vals[phase_target] * val <= 0 and abs(prev_vals[phase_target] - val) < 180:
                event_dt = _refine_phase(swe, prev_dt, dt, phase_target)
                if start_dt <= event_dt <= end_dt:
                    event_jd, _ = datetime_to_jd_ut(swe, event_dt)
                    sun = planet_position(swe, event_jd, swe.SUN)
                    moon = planet_position(swe, event_jd, swe.MOON)
                    lunation_lon = moon["lon"] if event_type == "full_moon" else sun["lon"]
                    node_distance = _node_distance(swe, event_jd, lunation_lon)
                    classification = _eclipse_classification(event_type, node_distance)
                    all_aspects, retained_aspects = _target_aspects(compiler, lunation_lon)
                    events.append({
                        "event_id": f"lunation:{event_dt.strftime('%Y%m%dT%H%M%SZ')}:{event_type}",
                        "event_type": event_type,
                        "event_utc": event_dt.isoformat(),
                        "sun_lon": sun["lon"],
                        "moon_lon": moon["lon"],
                        "lunation_lon": lunation_lon,
                        "lunation_pretty": format_zodiac(lunation_lon),
                        "node_distance": node_distance,
                        **classification,
                        "activation_window": {
                            "start_utc": (event_dt - timedelta(days=3)).isoformat(),
                            "peak_utc": event_dt.isoformat(),
                            "end_utc": (event_dt + timedelta(days=3)).isoformat(),
                        },
                        "target_aspects": retained_aspects,
                        "total_activation_count": len(all_aspects),
                        "retained_activation_count": len(retained_aspects),
                        "activation_count": len(all_aspects),
                        "top_themes": [
                            {"theme": theme, "count": count}
                            for theme, count in sorted(
                                Counter(tag for row in all_aspects for tag in row.get("theme_tags", [])).items(),
                                key=lambda kv: (-kv[1], kv[0]),
                            )[:10]
                        ],
                    })
            prev_vals[phase_target] = val
        prev_dt = dt
        dt += timedelta(hours=12)

    events.sort(key=lambda row: (row["event_utc"], row["event_type"]))
    eclipse_windows = [row["event_id"] for row in events if row["is_eclipse_window"]]
    target_meta = None
    if target is not None:
        target_meta = {
            "chart_id": target.chart_id,
            "chart_type": target.chart_type,
            "subject_scope": target.subject_scope,
            "semantic_scope": {
                "natal": "individual_lunation_climate",
                "composite": "relationship_pattern_lunation_climate",
                "davison": "relationship_lifecycle_lunation_climate",
            }.get(target.chart_type, "chart_lunation_climate"),
            "label": target.label,
        }

    package = {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "analysis_type": "eclipse_lunation_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "start": start,
            "end": end,
            "target_chart": target_meta,
            "event_count": len(events),
            "eclipse_window_count": len(eclipse_windows),
        },
        "target": target_meta,
        "period": {"start": start, "end": end},
        "events": events,
        "indexes": {
            "events_by_id": {row["event_id"]: i for i, row in enumerate(events)},
            "eclipse_window_event_refs": eclipse_windows,
            "events_by_month": {
                month: [row["event_id"] for row in events if row["event_utc"][:7] == month]
                for month in sorted({row["event_utc"][:7] for row in events})
            },
        },
        "report_materials": {
            "recommended_sections": [
                "Lunation Calendar",
                "Eclipse-Season Windows",
                "Target Activation Summary",
                "Highest-Activation Lunations",
                "Timeline Integration Notes",
            ],
            "highest_activation_events": sorted(
                events,
                key=lambda row: (
                    -int(row["is_eclipse_window"]),
                    -int(row["total_activation_count"]),
                    float(row["node_distance"]),
                    row["event_utc"],
                ),
            )[:12],
        },
    } 
    return finalize_package_semantic_boundary(package)
