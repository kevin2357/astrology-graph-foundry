"""Project one canonical Natal fixture through three different ontologies.

Run from the repository root:

    python examples/projection_cross_profile_chunk26.py
"""
from __future__ import annotations

import json

from astrology_graph_foundry import project_dataset
from semantic_projection import ProjectionContext


package = {
    "metadata": {
        "analysis_type": "natal_dataset",
        "source_chart_id": "natal:cross_profile_fixture",
        "source_chart_ids": ["natal:cross_profile_fixture"],
        "sensor_instance_id": "natal:cross_profile_fixture",
    },
    "canonical_astrology_graph": {
        "graph_type": "canonical_astrology_graph",
        "graph_version": "1.3.0",
        "objects": [
            {
                "id": "natal:Mars",
                "name": "Mars",
                "object_type": "planet_or_point",
                "sign": "Leo",
                "house": 6,
                "operator_hints": [{"operator": "act"}],
                "structural_strength_score": 0.8,
            },
            {
                "id": "natal:Venus",
                "name": "Venus",
                "object_type": "planet_or_point",
                "sign": "Scorpio",
                "house": 8,
                "operator_hints": [{"operator": "value"}],
                "structural_strength_score": 0.9,
            },
            {
                "id": "natal:ASC",
                "name": "ASC",
                "object_type": "angle",
                "sign": "Aquarius",
                "house": 1,
                "structural_strength_score": 0.95,
            },
            {
                "id": "house:8",
                "name": "House 8",
                "object_type": "house_cusp",
                "facts": {"house": 8},
                "structural_strength_score": 0.7,
            },
        ],
        "relationships": [
            {
                "id": "aspect:Mars:square:Venus",
                "relationship_type": "ASPECT",
                "source_id": "natal:Mars",
                "target_id": "natal:Venus",
                "aspect": "square",
                "operator_hints": [{"operator": "stress"}],
                "structural_strength_score": 0.75,
            },
            {
                "id": "aspect:Venus:quincunx:ASC",
                "relationship_type": "ASPECT",
                "source_id": "natal:Venus",
                "target_id": "natal:ASC",
                "aspect": "quincunx",
                "structural_strength_score": 0.62,
            },
        ],
    },
    "structural_evidence_graph": {"graph_version": "1.3.0"},
}

cognitive_context = ProjectionContext(
    context_id="cognitive_architecture.general.v0",
    context_version="0.2.0",
    subject_scope="individual",
    target_domain="cognitive_architecture_demo.v0",
    application_context="cognitive_architecture_demo",
    constraints={
        "experimental": True,
        "clinical_use": False,
        "diagnostic_use": False,
    },
)

woof_context = ProjectionContext(
    context_id="woofmapped.doghouse.general.v0",
    context_version="0.1.0",
    subject_scope="dog",
    target_domain="woofmapped_astrology.v0",
    application_context="woofmapped_natal_projection",
    audience="handler_general",
    constraints={
        "playful_experimental_projection": True,
        "veterinary_advice": False,
        "behavioral_diagnosis": False,
        "house_mapping_policy": "doghouse",
    },
)

print(json.dumps({
    "orthodox": project_dataset(package),
    "cognitive": project_dataset(
        package,
        profile_id="cognitive_architecture_demo.v0",
        profile_version="0.2.0",
        context=cognitive_context,
    ),
    "woofmapped": project_dataset(
        package,
        profile_id="woofmapped_astrology.v0",
        profile_version="0.1.0",
        context=woof_context,
    ),
}, indent=2))
