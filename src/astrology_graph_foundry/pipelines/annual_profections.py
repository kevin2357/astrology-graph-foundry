from __future__ import annotations

from datetime import date, datetime
from typing import Any

from astrology_graph_foundry.common.geometry import deg_to_sign
from astrology_graph_foundry.common.constants import SIGN_RULERS_TRADITIONAL
from astrology_graph_foundry.common.transitable_chart import from_package
from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary

SCHEMA_VERSION = "2.0.0"
PIPELINE_VERSION = "annual_profections_pipeline_v2.0.0_transitable_chart"


def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value[:10]).date()


def _reference_date(target, explicit: str | None = None) -> date:
    if explicit:
        return _parse_date(explicit)
    ref = target.reference_event
    for key in ("event_local", "event_utc"):
        if ref.get(key):
            return _parse_date(str(ref[key]))
    raise ValueError(
        "Annual profections require a dated TransitableChart reference event "
        "or an explicit --reference-date."
    )


def _age_on(origin: date, target: date) -> int:
    return target.year - origin.year - ((target.month, target.day) < (origin.month, origin.day))


def build(
    *,
    target_dataset: str | dict[str, Any],
    target_date: str,
    reference_date: str | None = None,
) -> dict[str, Any]:
    target_chart = from_package(target_dataset)
    origin = _reference_date(target_chart, reference_date)
    target = _parse_date(target_date)
    age = _age_on(origin, target)
    if age < 0:
        raise ValueError("Annual profection target date precedes the target chart reference event.")

    house = (age % 12) + 1
    houses = target_chart.chart.get("houses") or {}
    cusp = houses.get(str(house), {})
    sign = cusp.get("cusp_sign") or cusp.get("sign")
    if not sign and cusp.get("lon") is not None:
        sign = deg_to_sign(float(cusp["lon"]))["sign"]
    lord = (
        cusp.get("traditional_ruler")
        or cusp.get("ruler")
        or cusp.get("modern_ruler")
        or SIGN_RULERS_TRADITIONAL.get(sign)
    )
    semantic_scope = {
        "natal": "individual_annual_profection",
        "composite": "relationship_pattern_annual_profection",
        "davison": "relationship_lifecycle_annual_profection",
    }.get(target_chart.chart_type, "chart_annual_profection")

    experimental = target_chart.chart_type != "natal"
    interpretation_note = (
        "Traditional annual profection from the natal birth event."
        if target_chart.chart_type == "natal"
        else (
            "Experimental relationship-entity profection: completed years are counted from "
            "the chart's reference event. Davison uses its real midpoint event; Composite uses "
            "its explicitly labeled synthetic midpoint reference event."
        )
    )
    package = {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "analysis_type": "annual_profections_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "target_label": target_chart.label,
            "target_chart_id": target_chart.chart_id,
            "target_chart_type": target_chart.chart_type,
            "target_subject_scope": target_chart.subject_scope,
            "semantic_scope": semantic_scope,
            "target_date": target_date,
            "experimental_relationship_entity_technique": experimental,
        },
        "target": {
            "chart_identity": {
                "chart_id": target_chart.chart_id,
                "chart_type": target_chart.chart_type,
                "subject_scope": target_chart.subject_scope,
                "label": target_chart.label,
            },
            "construction": target_chart.construction,
            "reference_event": target_chart.reference_event,
        },
        "profection": {
            "completed_years": age,
            "activated_house": house,
            "activated_sign": sign,
            "time_lord": lord,
            "reference_date": origin.isoformat(),
            "target_date": target.isoformat(),
            "method": "whole-sign annual profection house by completed years from TransitableChart reference event; house ruler taken from chart house-cusp metadata when available, with traditional sign-ruler fallback",
            "interpretation_note": interpretation_note,
        },
        "report_materials": {
            "recommended_sections": [
                "Year Lord",
                "Activated House",
                "Activated Sign",
                "Target Chart Context",
                "Transit Integration Notes",
            ],
            "summary_hints": [
                f"Completed year {age} activates house {house}.",
                f"The year is routed through {sign or 'unknown sign'} and its time lord {lord or 'unknown'}.",
                interpretation_note,
            ],
        },
    } 
    return finalize_package_semantic_boundary(package)
