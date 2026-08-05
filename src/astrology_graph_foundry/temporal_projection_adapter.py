from __future__ import annotations

"""Astrology Graph Foundry handoff for Semantic Projection Core temporal projection.

This module prepares the complete Foundry-owned source bundle consumed by
Semantic Projection Core's production temporal route:
a static canonical target graph, structural evidence, and the canonical
temporal activation graph.

The bundle intentionally contains no target-domain projected meanings.
"""

from hashlib import sha256
from copy import deepcopy
from typing import Any

from astrology_graph_foundry.common.temporal_activation import (
    TemporalExportOptions,
    extract_canonical_temporal_activation_graph,
)

from astrology_graph_foundry.pipelines.transit_period import (
    transit_candidate_matches_target_set,
)

TEMPORAL_PROJECTION_SOURCE_BUNDLE_VERSION = "1.0.0"


def _stable_token(*parts: Any) -> str:
    payload = "|".join(str(part if part is not None else "") for part in parts)
    return sha256(payload.encode("utf-8")).hexdigest()[:20]



def _canonical_graph_from_target_package(target_package: dict[str, Any]) -> dict[str, Any]:
    graph = target_package.get("canonical_astrology_graph") or {}
    if not graph:
        raise ValueError(
            "Temporal projection source export requires a nonempty canonical target graph. "
            "Supply a full natal, composite, or Davison package via --target-dataset when "
            "the Transit artifact does not embed canonical_astrology_graph."
        )
    return graph


def _graph_chart_id(graph: dict[str, Any]) -> str | None:
    return graph.get("source_chart_id") or (graph.get("metadata") or {}).get("source_chart_id")


def _filter_temporal_source_package(
    package: dict[str, Any],
    *,
    target_set: str | None,
) -> dict[str, Any]:
    if not target_set or target_set == "all":
        return package
    filtered = deepcopy(package)
    registry = package.get("candidate_registry") or {}
    accepted_ids = {
        candidate_id
        for candidate_id, candidate in registry.items()
        if transit_candidate_matches_target_set(candidate, target_set)
    }

    if package.get("daily_windows"):
        filtered["daily_windows"] = [
            {
                **day,
                "candidates": [
                    candidate
                    for candidate in day.get("candidates", []) or []
                    if transit_candidate_matches_target_set(candidate, target_set)
                ],
            }
            for day in package.get("daily_windows", []) or []
        ]
    if package.get("days"):
        filtered["days"] = [
            {
                **day,
                "candidate_refs": [
                    row
                    for row in day.get("candidate_refs", []) or []
                    if str(row.get("candidate_id") or "") in accepted_ids
                ],
            }
            for day in package.get("days", []) or []
        ]
        filtered["candidate_registry"] = {
            candidate_id: registry[candidate_id]
            for candidate_id in sorted(accepted_ids)
        }
    if package.get("days_by_date"):
        filtered["days_by_date"] = {
            date: {
                **day,
                "contacts": [
                    row
                    for row in day.get("contacts", []) or []
                    if str(row.get("candidate_id") or "") in accepted_ids
                ],
            }
            for date, day in (package.get("days_by_date") or {}).items()
        }
        filtered["candidate_registry"] = {
            candidate_id: registry[candidate_id]
            for candidate_id in sorted(accepted_ids)
        }

    arcs_key = "transit_arcs" if package.get("transit_arcs") is not None else "arcs"
    if package.get(arcs_key) is not None:
        filtered[arcs_key] = [
            arc
            for arc in package.get(arcs_key, []) or []
            if str(arc.get("candidate_id") or "") in accepted_ids
        ]
    return filtered


def build_temporal_projection_source_bundle(
    transit_package: dict[str, Any],
    *,
    target_package: dict[str, Any] | None = None,
    target_set: str | None = None,
    options: TemporalExportOptions | None = None,
) -> dict[str, Any]:
    """Build the projection-neutral cross-repository timing handoff.

    This is a source adapter, not a projected result or an executable Semantic
    Projection Core request. Core validates and adapts this bundle into its
    temporal request before producing ``projected_temporal_activation_graph.v1``.
    """

    filtered_package = _filter_temporal_source_package(
        transit_package,
        target_set=target_set,
    )
    temporal_graph = extract_canonical_temporal_activation_graph(
        filtered_package,
        options=options,
    )
    target_identity = temporal_graph["target_identity"]
    authoritative_target = target_package or transit_package
    static_graph = _canonical_graph_from_target_package(authoritative_target)
    graph_chart_id = _graph_chart_id(static_graph)
    target_chart_id = target_identity.get("chart_id")
    if graph_chart_id and target_chart_id and graph_chart_id != target_chart_id:
        raise ValueError(
            "Temporal projection source target mismatch: "
            f"temporal target={target_chart_id!r}, canonical graph={graph_chart_id!r}."
        )
    structural_evidence = (
        authoritative_target.get("structural_evidence_graph")
        or transit_package.get("structural_evidence_graph")
        or {}
    )
    source_identity = {
        "source_chart_id": target_identity.get("chart_id"),
        "source_chart_ids": [target_identity.get("chart_id")],
        "sensor_instance_id": (
            f"temporal:{target_identity.get('chart_id')}:"
            f"{temporal_graph.get('period', {}).get('start_at')}:"
            f"{temporal_graph.get('period', {}).get('end_at')}"
        ),
    }
    bundle_id = f"temporal_projection_source:{_stable_token(source_identity, temporal_graph['metadata']['graph_id'])}"
    return {
        "metadata": {
            "package_type": "temporal_projection_source_bundle",
            "contract_version": TEMPORAL_PROJECTION_SOURCE_BUNDLE_VERSION,
            "bundle_id": bundle_id,
            "projection_neutral": True,
            "consumer_status": "reserved_for_semantic_projection_core_temporal_support",
            "transit_target_set": target_set or "all",
            "static_source_graph_authority": (
                "explicit_target_dataset" if target_package is not None else "embedded_transit_package"
            ),
        },
        "source_identity": source_identity,
        "target_identity": target_identity,
        "static_source_graph": static_graph,
        "structural_evidence": structural_evidence,
        "temporal_source_graph": temporal_graph,
        "source_registries": {
            "activated_target_relationship_registry": (
                transit_package.get("activated_target_relationship_registry") or {}
            ),
        },
        "limitations": [
            "This bundle is projection-neutral source material and must be adapted and executed by Semantic Projection Core.",
            "The bundle preserves source timing facts and carries no projected temporal meanings.",
            "The consumer_status value is a frozen version-1.0.0 compatibility token retained for Semantic Projection Core intake validation.",
        ],
    }
