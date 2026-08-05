from __future__ import annotations

import json
from pathlib import Path

import semantic_projection
from semantic_projection import ProjectionContext

from astrology_graph_foundry import project_dataset


def package_fixture() -> dict:
    return {
        "metadata": {
            "analysis_type": "natal_dataset",
            "source_chart_id": "natal:chunk28",
            "source_chart_ids": ["natal:chunk28"],
            "sensor_instance_id": "natal:chunk28",
        },
        "canonical_astrology_graph": {
            "graph_type": "canonical_astrology_graph",
            "graph_version": "1.3.0",
            "objects": [
                {"id": "natal:Sun", "name": "Sun", "object_type": "planet_or_point", "sign": "Libra", "house": 8},
                {"id": "natal:Mars", "name": "Mars", "object_type": "planet_or_point", "sign": "Leo", "house": 6},
            ],
            "relationships": [
                {"id": "aspect:Sun:Mars", "relationship_type": "ASPECT", "source_id": "natal:Sun", "target_id": "natal:Mars", "aspect": "sextile"}
            ],
        },
        "structural_evidence_graph": {"graph_version": "1.3.0"},
    }


def test_foundry_uses_external_semantic_projection_package():
    package = package_fixture()
    before = json.dumps(package, sort_keys=True)
    result = project_dataset(
        package,
        profile_id="cognitive_architecture_demo.v0",
        profile_version="0.2.0",
        context=ProjectionContext(
            context_id="cognitive_architecture.general.v0",
            context_version="0.2.0",
            subject_scope="individual",
            target_domain="cognitive_architecture_demo.v0",
            application_context="cognitive_architecture_demo",
        ),
    )
    assert result["metadata"]["profile_id"] == "cognitive_architecture_demo.v0"
    assert len(result["objects"]) == 2
    assert len(result["relationships"]) == 1
    assert json.dumps(package, sort_keys=True) == before
    assert "semantic_projection" in Path(semantic_projection.__file__).parts
    assert not (Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "projection").exists()


def test_profile_source_selection_excludes_aliases_without_counting_mapping_failures():
    package = package_fixture()
    package["canonical_astrology_graph"]["objects"].extend([
        {"id": "natal:True_Node", "name": "True Node", "object_type": "calculated_point"},
        {"id": "natal:Mean_Node", "name": "Mean Node", "object_type": "calculated_point"},
        {"id": "natal:Part_of_Fortune", "name": "Part of Fortune", "object_type": "lot"},
        {"id": "natal:Fortune", "name": "Fortune", "object_type": "lot"},
    ])
    package["canonical_astrology_graph"]["relationships"].extend([
        {"id": "aspect:Sun:True_Node", "relationship_type": "ASPECT", "source_id": "natal:Sun", "target_id": "natal:True_Node", "aspect": "trine"},
        {"id": "aspect:Sun:Mean_Node", "relationship_type": "ASPECT", "source_id": "natal:Sun", "target_id": "natal:Mean_Node", "aspect": "trine"},
        {"id": "aspect:Sun:Part_of_Fortune", "relationship_type": "ASPECT", "source_id": "natal:Sun", "target_id": "natal:Part_of_Fortune", "aspect": "square"},
        {"id": "aspect:Sun:Fortune", "relationship_type": "ASPECT", "source_id": "natal:Sun", "target_id": "natal:Fortune", "aspect": "square"},
    ])
    result = project_dataset(
        package,
        profile_id="cognitive_architecture_demo.v0",
        profile_version="0.2.0",
        context=ProjectionContext(
            context_id="cognitive_architecture.general.v0",
            context_version="0.2.0",
            subject_scope="individual",
            target_domain="cognitive_architecture_demo.v0",
            application_context="cognitive_architecture_demo",
        ),
    )
    source_refs = {ref for row in result["objects"] for ref in row["source_refs"]}
    assert "canonical:object:natal:True_Node" in source_refs
    assert "canonical:object:natal:Part_of_Fortune" in source_refs
    assert "canonical:object:natal:Mean_Node" not in source_refs
    assert "canonical:object:natal:Fortune" not in source_refs
    coverage = result["summary"]["profile_scope_coverage"]
    assert coverage["objects"]["excluded_by_source_selection_policy_count"] == 2
    assert coverage["relationships"]["excluded_by_source_selection_policy_count"] == 2
    assert coverage["objects"]["eligible_but_unmapped_count"] == 0
    assert coverage["relationships"]["eligible_but_unmapped_count"] == 0


def test_explicit_source_chart_identity_survives_projection_without_context_contamination():
    package = package_fixture()
    source_chart_id = "astrowoof:dog:ABC-123"
    package["metadata"].update(
        {
            "source_chart_id": source_chart_id,
            "source_chart_ids": [source_chart_id],
            "sensor_instance_id": source_chart_id,
        }
    )
    package["canonical_astrology_graph"].update(
        {
            "source_chart_id": source_chart_id,
            "source_chart_ids": [source_chart_id],
            "sensor_instance_id": source_chart_id,
        }
    )
    contexts = (
        ProjectionContext(
            context_id="cognitive_architecture.general.v0",
            context_version="0.2.0",
            subject_scope="individual",
            target_domain="cognitive_architecture_demo.v0",
            application_context="general",
        ),
        ProjectionContext(
            context_id="cognitive_architecture.general.v0",
            context_version="0.2.0",
            subject_scope="individual",
            target_domain="cognitive_architecture_demo.v0",
            application_context="alternate",
        ),
    )

    projected = [
        project_dataset(
            package,
            profile_id="cognitive_architecture_demo.v0",
            profile_version="0.2.0",
            context=context,
        )
        for context in contexts
    ]

    for result in projected:
        assert result["source_identity"]["source_chart_id"] == source_chart_id
        assert result["source_identity"]["source_chart_ids"] == [source_chart_id]
        assert result["source_identity"]["sensor_instance_id"] == source_chart_id
    assert projected[0]["metadata"]["projection_id"] != projected[1]["metadata"]["projection_id"]
    assert (
        projected[0]["metadata"]["runtime_identity"]["context"]["content_sha256"]
        != projected[1]["metadata"]["runtime_identity"]["context"]["content_sha256"]
    )
