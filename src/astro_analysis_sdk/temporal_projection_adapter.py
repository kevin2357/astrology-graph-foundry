from __future__ import annotations

"""Astrology Graph Foundry handoff for future temporal projection.

Semantic Projection Core does not yet execute temporal projection.  This module
prepares the complete Foundry-owned source bundle it will eventually consume:
a static canonical target graph, structural evidence, and the canonical
temporal activation graph.

The bundle intentionally contains no target-domain projected meanings.
"""

from hashlib import sha256
from typing import Any

from astro_analysis_sdk.common.temporal_activation import (
    TemporalExportOptions,
    extract_canonical_temporal_activation_graph,
)

TEMPORAL_PROJECTION_SOURCE_BUNDLE_VERSION = "1.0.0"


def _stable_token(*parts: Any) -> str:
    payload = "|".join(str(part if part is not None else "") for part in parts)
    return sha256(payload.encode("utf-8")).hexdigest()[:20]


def build_temporal_projection_source_bundle(
    transit_package: dict[str, Any],
    *,
    options: TemporalExportOptions | None = None,
) -> dict[str, Any]:
    """Build the projection-neutral cross-repository timing handoff.

    This is a source adapter, not a projected result and not an executable
    Semantic Projection Core request.  Core will define the final temporal
    request contract when ``projected_temporal_activation_graph.v1`` is
    implemented.
    """

    temporal_graph = extract_canonical_temporal_activation_graph(
        transit_package,
        options=options,
    )
    target_identity = temporal_graph["target_identity"]
    static_graph = transit_package.get("canonical_astrology_graph") or {}
    structural_evidence = transit_package.get("structural_evidence_graph") or {}
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
            "Semantic Projection Core does not yet execute this bundle.",
            "The bundle preserves source timing facts and carries no projected temporal meanings.",
        ],
    }
