from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from astrology_graph_foundry.common.temporal_activation import TemporalExportOptions
from astrology_graph_foundry.temporal_projection_adapter import (
    build_temporal_projection_source_bundle,
)


def _package() -> dict:
    return {
        "metadata": {
            "analysis_type": "transit_period_dataset",
            "target_label": "Relationship",
            "target_chart_id": "composite:a:b",
            "target_chart_type": "composite",
            "target_subject_scope": "relationship",
            "semantic_scope": "relationship_pattern_climate",
            "start_date": "2026-01-01",
            "end_date": "2026-01-03",
        },
        "period": {
            "start_date": "2026-01-01",
            "end_date": "2026-01-03",
            "day_count": 3,
        },
        "daily_windows": [
            {
                "date": "2026-01-01",
                "transit_datetime": "2026-01-01T12:00:00-07:00",
                "positions": {},
                "candidates": [
                    {
                        "candidate_id": "tc:Saturn:trine:composite_Sun",
                        "transit_body": "Saturn",
                        "aspect": "trine",
                        "target": "Sun",
                        "target_id": "composite:Sun",
                        "target_type": "planet_or_point",
                        "orb": 0.8,
                    }
                ],
            },
            {
                "date": "2026-01-02",
                "transit_datetime": "2026-01-02T12:00:00-07:00",
                "positions": {},
                "candidates": [
                    {
                        "candidate_id": "tc:Saturn:trine:composite_Sun",
                        "transit_body": "Saturn",
                        "aspect": "trine",
                        "target": "Sun",
                        "target_id": "composite:Sun",
                        "target_type": "planet_or_point",
                        "orb": 0.1,
                    }
                ],
            },
            {
                "date": "2026-01-03",
                "transit_datetime": "2026-01-03T12:00:00-07:00",
                "positions": {},
                "candidates": [
                    {
                        "candidate_id": "tc:Saturn:trine:composite_Sun",
                        "transit_body": "Saturn",
                        "aspect": "trine",
                        "target": "Sun",
                        "target_id": "composite:Sun",
                        "target_type": "planet_or_point",
                        "orb": 0.5,
                    }
                ],
            },
        ],
        "transit_arcs": [
            {
                "arc_id": "arc:tc:Saturn:trine:composite_Sun",
                "candidate_id": "tc:Saturn:trine:composite_Sun",
                "transit_body": "Saturn",
                "aspect": "trine",
                "target": "Sun",
                "target_id": "composite:Sun",
                "target_type": "planet_or_point",
                "start_date": "2026-01-01",
                "end_date": "2026-01-03",
                "closest_orb": 0.1,
            }
        ],
        "canonical_astrology_graph": {
            "graph_type": "canonical_astrology_graph",
            "graph_version": "1.3.0",
            "metadata": {"graph_id": "canonical:composite:a:b"},
            "objects": [],
            "relationships": [],
        },
        "structural_evidence_graph": {
            "graph_type": "structural_evidence_graph",
            "graph_version": "1.3.0",
        },
        "activated_target_relationship_registry": {
            "relationship:1": {"relationship_type": "ASPECT"}
        },
    }


def test_temporal_projection_source_bundle_preserves_all_source_layers():
    result = build_temporal_projection_source_bundle(
        _package(),
        options=TemporalExportOptions(sampled_exact_orb=0.01),
    )
    assert result["metadata"]["package_type"] == "temporal_projection_source_bundle"
    assert result["metadata"]["projection_neutral"] is True
    assert result["target_identity"]["chart_type"] == "composite"
    assert result["source_identity"]["source_chart_id"] == "composite:a:b"
    assert result["static_source_graph"]["graph_type"] == "canonical_astrology_graph"
    assert result["structural_evidence"]["graph_type"] == "structural_evidence_graph"
    assert result["temporal_source_graph"]["summary"]["activation_count"] == 1
    assert (
        result["source_registries"]["activated_target_relationship_registry"][
            "relationship:1"
        ]["relationship_type"]
        == "ASPECT"
    )


def test_temporal_projection_source_bundle_schema_validates():
    result = build_temporal_projection_source_bundle(_package())
    schema_root = (
        Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "schemas"
    )
    schema = json.loads(
        (schema_root / "temporal_projection_source_bundle_v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    temporal_schema = json.loads(
        (schema_root / "canonical_temporal_activation_graph_v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    registry = Registry().with_resource(
        schema_root.as_uri() + "/canonical_temporal_activation_graph_v1.schema.json",
        Resource.from_contents(temporal_schema),
    ).with_resource(
        "canonical_temporal_activation_graph_v1.schema.json",
        Resource.from_contents(temporal_schema),
    )
    errors = sorted(
        Draft202012Validator(schema, registry=registry).iter_errors(result),
        key=lambda error: list(error.path),
    )
    assert not errors, [error.message for error in errors]
