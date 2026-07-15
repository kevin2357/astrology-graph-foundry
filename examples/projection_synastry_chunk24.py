"""Run from the repository root:

    python examples/projection_synastry_chunk24.py

Produces two projections of the same canonical Synastry source:
general relationship context and professional relationship context.
"""
from __future__ import annotations

import json

from astro_analysis_sdk.projection_adapter import project_synastry_package


package = {
    "metadata": {
        "analysis_type": "synastry_relationship_dataset",
        "source_chart_id": "natal:person_a",
        "source_chart_ids": ["natal:person_a", "natal:person_b"],
        "sensor_instance_id": "synastry:natal:person_a:natal:person_b",
    },
    "canonical_astrology_graph": {
        "graph_type": "canonical_astrology_graph",
        "graph_version": "1.3.0",
        "objects": [
            {
                "id": "synastry:person_a:natal:Venus",
                "name": "Venus",
                "object_type": "planet_or_point",
                "subject_owner": "person_a",
                "structural_strength_score": 0.90,
            },
            {
                "id": "synastry:person_b:natal:Mercury",
                "name": "Mercury",
                "object_type": "planet_or_point",
                "subject_owner": "person_b",
                "structural_strength_score": 0.85,
            },
            {
                "id": "synastry:person_b:house:3",
                "name": "person_b house 3",
                "object_type": "house_cusp",
                "subject_owner": "person_b",
                "facts": {"house": 3},
                "structural_strength_score": 0.70,
            },
        ],
        "relationships": [
            {
                "id": "syn:venus:trine:mercury",
                "relationship_type": "SYNASTRY_ASPECT",
                "direction": "a_to_b",
                "source_person": "Person A",
                "target_person": "Person B",
                "source_id": "synastry:person_a:natal:Venus",
                "target_id": "synastry:person_b:natal:Mercury",
                "aspect": "trine",
                "orb": 0.4,
                "theme_key": "communication|ease_support|home_family",
                "operator_key": "connect|interpret",
                "structural_strength_score": 0.88,
            },
            {
                "id": "overlay:venus:house3",
                "relationship_type": "HOUSE_OVERLAY",
                "direction": "a_to_b",
                "source_person": "Person A",
                "target_person": "Person B",
                "source_id": "synastry:person_a:natal:Venus",
                "target_id": "synastry:person_b:house:3",
                "target_house": 3,
                "theme_key": "communication|values_resources",
                "operator_key": "connect",
                "structural_strength_score": 0.76,
            },
        ],
        "summary": {"object_count": 3, "relationship_count": 2},
    },
    "structural_evidence_graph": {"graph_version": "1.3.0"},
    "theme_registry": {
        "communication|ease_support|home_family": [
            "communication", "ease_support", "home_family"
        ],
        "communication|values_resources": [
            "communication", "values_resources"
        ],
    },
    "operator_registry": {
        "connect|interpret": [
            {"operator": "connect"}, {"operator": "interpret"}
        ],
        "connect": [{"operator": "connect"}],
    },
    "object_registries": {},
    "natal_context_registries": {},
    "projection_views": {
        "orthodox_astrology.v1": {"theme_metrics": []}
    },
}

print(json.dumps({
    "general": project_synastry_package(package, professional=False),
    "professional": project_synastry_package(package, professional=True),
}, indent=2))
