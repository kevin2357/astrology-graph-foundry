from __future__ import annotations

import json
from pathlib import Path

import semantic_projection
from astro_analysis_sdk import project_dataset
from semantic_projection import ProjectionContext


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
    assert not (Path(__file__).parents[1] / "src" / "astro_analysis_sdk" / "projection").exists()
