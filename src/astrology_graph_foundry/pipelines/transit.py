from __future__ import annotations

"""Unified transit pipeline.

A one-day transit package is the same package shape as a date-range transit
package with start == end.  This module intentionally delegates to the modern
transit_period implementation so GraphCompiler, compact views, registries, and
logging stay in one place.
"""

from typing import Any

from astrology_graph_foundry.pipelines import transit_period

SCHEMA_VERSION = transit_period.SCHEMA_VERSION
PIPELINE_VERSION = "transit_pipeline_v3_transitable_chart"


def build(
    *,
    date: str | None = None,
    start: str | None = None,
    end: str | None = None,
    provider: str = "cached",
    person_jsonl: str | None = None,
    target_dataset: str | None = None,
    global_jsonl: str | None = None,
    snapshot_timezone: str = "America/Denver",
    snapshot_time: str = "12:00",
    ephe_path: str = ".",
    top_n_per_day: int = 20,
    min_arc_days: int = 1,
) -> dict[str, Any]:
    if date:
        start = end = date
    if not start or not end:
        raise ValueError("transit.build requires either --date or both --start and --end")
    package = transit_period.build(
        start=start,
        end=end,
        provider=provider,
        person_jsonl=person_jsonl,
        target_dataset=target_dataset,
        global_jsonl=global_jsonl,
        snapshot_timezone=snapshot_timezone,
        snapshot_time=snapshot_time,
        ephe_path=ephe_path,
        top_n_per_day=top_n_per_day,
        min_arc_days=min_arc_days,
    )
    package["metadata"] = {
        **package.get("metadata", {}),
        "analysis_type": "transit_dataset" if start == end else "transit_range_dataset",
        "pipeline_version": PIPELINE_VERSION,
        "public_pipeline_name": "transit",
        "unified_transit_api": True,
    }
    return package


def analysis_view(package: dict[str, Any]) -> dict[str, Any]:
    view = transit_period.analysis_view(package)
    view["metadata"] = {**view.get("metadata", {}), "public_pipeline_name": "transit"}
    return view


def streaming_index(
    package: dict[str, Any],
    *,
    profile: str = "standard",
    target_set: str | None = None,
) -> dict[str, Any]:
    view = transit_period.streaming_index(package, profile=profile, target_set=target_set)
    view["metadata"] = {**view.get("metadata", {}), "public_pipeline_name": "transit"}
    return view
