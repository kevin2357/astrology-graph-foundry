from __future__ import annotations

"""Common adapter for chart-like packages that can receive transits.

Natal, composite, and Davison packages retain their distinct package shapes and
provenance.  This module exposes the common chart substrate required by the
transit engine without pretending every chart is natal.
"""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from astrology_graph_foundry.common.chart_graph import build_chart_graph
from astrology_graph_foundry.common.identity import resolve_explicit_source_chart_id
from astrology_graph_foundry.common.io import read_json
from astrology_graph_foundry.common.package_compatibility import require_exact_chart_package

TRANSITABLE_CHART_VERSION = "transitable_chart_v1.0.0"


@runtime_checkable
class TransitableChartProtocol(Protocol):
    chart_id: str
    chart_type: str
    subject_scope: str
    label: str
    chart: dict[str, Any]
    semantic_graph: dict[str, Any]


@dataclass
class TransitableChart:
    chart_id: str
    chart_type: str
    subject_scope: str
    label: str
    chart: dict[str, Any]
    semantic_graph: dict[str, Any]
    construction: dict[str, Any]
    source_package_metadata: dict[str, Any]
    reference_event: dict[str, Any]

    @property
    def semantic_scope(self) -> str:
        return {
            "natal": "individual_climate",
            "composite": "relationship_pattern_climate",
            "davison": "relationship_lifecycle_climate",
        }.get(self.chart_type, "chart_climate")

    def descriptor(self, *, chart_key: str) -> dict[str, Any]:
        return {
            "interface_version": TRANSITABLE_CHART_VERSION,
            "chart_identity": {
                "chart_id": self.chart_id,
                "chart_type": self.chart_type,
                "subject_scope": self.subject_scope,
                "semantic_scope": self.semantic_scope,
                "label": self.label,
            },
            "chart_key": chart_key,
            "construction": self.construction,
            "reference_event": self.reference_event,
            "capabilities": {
                "supports_longitude_aspects": True,
                "supports_house_transits": len(self.chart.get("houses") or {}) == 12,
                "supports_angle_transits": bool(self.chart.get("angles")) or any(
                    key in (self.chart.get("bodies") or {}) for key in ("ASC", "MC", "DSC", "IC")
                ),
                "supports_semantic_graph_activation": True,
                "supports_solar_return": bool(self.reference_event.get("event_utc") or self.reference_event.get("event_local")),
                "supports_lunar_return": bool((self.chart.get("bodies") or {}).get("nMoon") or (self.chart.get("bodies") or {}).get("Moon")),
                "supports_annual_profections": bool(self.reference_event.get("event_utc") or self.reference_event.get("event_local")),
                "supports_lunation_activation": True,
            },
        }


def _load(package_or_path: str | dict[str, Any]) -> dict[str, Any]:
    return read_json(package_or_path) if isinstance(package_or_path, str) else package_or_path


def _detect(package: dict[str, Any]) -> tuple[str, str, str, dict[str, Any]]:
    meta = package.get("metadata", {})
    analysis_type = str(meta.get("analysis_type") or "")
    if analysis_type == "natal_dataset" or "natal" in package:
        chart = package.get("natal")
        if isinstance(chart, dict):
            label = str(meta.get("person") or chart.get("person") or "Natal chart")
            return "natal", "individual", "natal", chart
    if analysis_type == "composite_dataset" or "composite_chart" in package:
        chart = package.get("composite_chart")
        if isinstance(chart, dict):
            label = str(chart.get("person") or f"Composite: {meta.get('person_a', 'A')} + {meta.get('person_b', 'B')}")
            return "composite", "relationship", "composite_chart", chart
    if analysis_type == "davison_relationship_dataset" or "davison_chart" in package:
        chart = package.get("davison_chart")
        if isinstance(chart, dict):
            label = str(chart.get("person") or f"Davison: {meta.get('person_a', 'A')} + {meta.get('person_b', 'B')}")
            return "davison", "relationship", "davison_chart", chart
    raise ValueError(
        "Target package does not expose a supported TransitableChart. "
        "Expected natal_dataset, composite_dataset, or davison_relationship_dataset."
    )


def _reference_event(package: dict[str, Any], chart_type: str, chart: dict[str, Any]) -> dict[str, Any]:
    existing = dict((package.get("transitable_chart") or {}).get("reference_event") or {})
    if existing:
        return existing
    if chart_type == "natal":
        return {
            "event_local": chart.get("birth_local"),
            "timezone": chart.get("birth_timezone"),
            "lat": chart.get("birth_lat"),
            "lon": chart.get("birth_lon"),
            "location_label": chart.get("birth_location_label"),
            "method": "birth_event",
        }
    if chart_type == "davison":
        event = package.get("davison_event") or {}
        return {
            "event_utc": event.get("midpoint_utc"),
            "timezone": "UTC",
            "lat": event.get("midpoint_lat"),
            "lon": event.get("midpoint_lon"),
            "location_label": "Davison midpoint",
            "method": "davison_midpoint_event",
        }
    if chart_type == "composite":
        event = package.get("composite_reference_event") or {}
        return {
            "event_utc": event.get("midpoint_utc"),
            "timezone": event.get("timezone") or "UTC",
            "lat": event.get("midpoint_lat"),
            "lon": event.get("midpoint_lon"),
            "location_label": event.get("location_label") or "Composite reference midpoint",
            "method": "synthetic_midpoint_reference_event",
        }
    return {}

def from_package(package_or_path: str | dict[str, Any]) -> TransitableChart:
    package = _load(package_or_path)
    require_exact_chart_package(package, consumer="TransitableChart")
    chart_type, subject_scope, chart_key, chart = _detect(package)
    graph = package.get("canonical_astrology_graph") or chart.get("semantic_graph") or package.get("semantic_graph") or build_chart_graph(chart)
    chart["semantic_graph"] = graph
    meta = package.get("metadata", {})
    label = str(chart.get("person") or meta.get("person") or f"{chart_type.title()} chart")
    if chart_type in {"composite", "davison"}:
        label = str(chart.get("person") or f"{chart_type.title()}: {meta.get('person_a', 'A')} + {meta.get('person_b', 'B')}")
    canonical = package.get("canonical_astrology_graph") if isinstance(package.get("canonical_astrology_graph"), dict) else {}
    explicit_chart_id = resolve_explicit_source_chart_id(
        (
            ("transitable_chart.chart_identity.chart_id", (package.get("transitable_chart") or {}).get("chart_identity", {}).get("chart_id")),
            ("metadata.source_chart_id", meta.get("source_chart_id")),
            (f"{chart_key}.source_chart_id", chart.get("source_chart_id")),
            ("canonical_astrology_graph.source_chart_id", canonical.get("source_chart_id")),
        )
    )
    chart_id = explicit_chart_id or f"{chart_type}:{label.lower().replace(' ', '_')}"
    construction = dict((package.get("transitable_chart") or {}).get("construction") or {})
    if not construction:
        construction = {
            "natal": {"method": "birth_chart"},
            "composite": {"method": meta.get("composite_method", "midpoint_longitude")},
            "davison": {"method": (package.get("davison_event") or {}).get("method", "midpoint_time_space")},
        }.get(chart_type, {})
    return TransitableChart(
        chart_id=chart_id,
        chart_type=chart_type,
        subject_scope=subject_scope,
        label=label,
        chart=chart,
        semantic_graph=graph,
        construction=construction,
        source_package_metadata=meta,
        reference_event=_reference_event(package, chart_type, chart),
    )


def descriptor_for_package(package: dict[str, Any]) -> dict[str, Any]:
    target = from_package(package)
    _, _, chart_key, _ = _detect(package)
    return target.descriptor(chart_key=chart_key)
