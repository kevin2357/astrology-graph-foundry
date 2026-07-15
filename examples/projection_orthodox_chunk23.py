"""Run from the repository root:

    python examples/projection_orthodox_chunk23.py

Projects a tiny canonical natal graph through the real orthodox reference
profile. This is structured semantic output, not a report.
"""
from __future__ import annotations

import json

from semantic_projection import (
    ProjectionContext,
    ProjectionOptions,
    ProjectionProfileRegistry,
    ProjectionRequest,
    project,
    projection_request_id,
)
from semantic_projection.profiles.orthodox_astrology import (
    OrthodoxAstrologyProfile,
)

context = ProjectionContext(
    context_id="orthodox.natal.general.v1",
    context_version="1.0.0",
    subject_scope="individual",
    target_domain="orthodox_astrology.v1",
    application_context="natal_interpretation",
    audience="adult_general",
).to_dict()
options = ProjectionOptions(
    unmapped_policy="diagnostic",
    include_audit=True,
    include_diagnostics=True,
).to_dict()
source_identity = {
    "source_chart_id": "fixture:orthodox_chunk23",
    "source_chart_ids": ["fixture:orthodox_chunk23"],
    "sensor_instance_id": "fixture:orthodox_chunk23",
}
source_graph = {
    "graph_type": "canonical_astrology_graph",
    "graph_version": "1.3.0",
    "objects": [
        {
            "id": "natal:Mars",
            "name": "Mars",
            "object_type": "planet_or_point",
            "sign": "Libra",
            "house": 8,
            "operator_hints": [{"operator": "act"}, {"operator": "assert"}],
            "structural_strength_score": 0.86,
        },
        {
            "id": "natal:Venus",
            "name": "Venus",
            "object_type": "planet_or_point",
            "sign": "Scorpio",
            "house": 8,
            "operator_hints": [{"operator": "value"}, {"operator": "bond"}],
            "structural_strength_score": 0.91,
        },
        {
            "id": "natal:MinorPoint",
            "name": "MinorPoint",
            "object_type": "calculated_point",
            "structural_strength_score": 0.4,
        },
    ],
    "relationships": [
        {
            "id": "aspect:Mars:square:Venus",
            "relationship_type": "ASPECT",
            "source_id": "natal:Mars",
            "target_id": "natal:Venus",
            "source_name": "Mars",
            "target_name": "Venus",
            "aspect": "square",
            "orb": 0.8,
            "operator_hints": [{"operator": "stress"}, {"operator": "develop"}],
            "structural_strength_score": 0.79,
        }
    ],
}
request = ProjectionRequest(
    request_id=projection_request_id(
        profile_id="orthodox_astrology.v1",
        profile_version="1.0.0",
        source_identity=source_identity,
        context=context,
        options=options,
    ),
    profile_id="orthodox_astrology.v1",
    profile_version="1.0.0",
    source_graph=source_graph,
    structural_evidence={"graph_version": "1.3.0"},
    source_identity=source_identity,
    context=context,
    options=options,
)
registry = ProjectionProfileRegistry()
registry.register(OrthodoxAstrologyProfile())
result = project(request, registry=registry)
print(json.dumps(result.to_dict(), indent=2))
