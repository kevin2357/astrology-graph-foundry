"""Run from the repository root:

    python examples/projection_engine_chunk22.py

This is a deliberately domain-neutral projection. Orthodox astrology arrives
in Chunk 2.3.
"""
from __future__ import annotations

import json

from semantic_projection import (
    ProjectionContext,
    ProjectionProfileRegistry,
    ProjectionRequest,
    project,
    projection_request_id,
)
from semantic_projection.profiles.demo import DemonstrationProjectionProfile

context = ProjectionContext(
    context_id="demonstration.general.v0",
    context_version="0.1.0",
    subject_scope="system",
    target_domain="demonstration_semantics.v0",
    application_context="concrete_contract_example",
).to_dict()
source_identity = {
    "source_chart_id": "fixture:chunk22",
    "source_chart_ids": ["fixture:chunk22"],
    "sensor_instance_id": "fixture:chunk22",
}
options = {
    "retain_unmapped_sources": True,
    "include_audit": True,
    "include_diagnostics": True,
    "unmapped_policy": "diagnostic",
}
request = ProjectionRequest(
    request_id=projection_request_id(
        profile_id="demonstration_projection.v0",
        profile_version="0.1.0",
        source_identity=source_identity,
        context=context,
        options=options,
    ),
    profile_id="demonstration_projection.v0",
    profile_version="0.1.0",
    source_graph={
        "graph_type": "canonical_astrology_graph",
        "graph_version": "1.3.0",
        "objects": [
            {"id": "source:a", "name": "Input A", "demo_category": "shared_process", "operator_hints": ["initiate"]},
            {"id": "source:b", "name": "Input B", "demo_category": "shared_process", "operator_hints": ["sustain"]},
            {"id": "source:unmapped", "name": "Intentionally unmapped", "project_demo": False},
        ],
        "relationships": [
            {"id": "source:relation", "relationship_type": "DEMO", "source_id": "source:a", "target_id": "source:b", "demo_relation": "coordinates_with"}
        ],
    },
    structural_evidence={"graph_version": "1.3.0"},
    source_identity=source_identity,
    context=context,
    options=options,
)
registry = ProjectionProfileRegistry()
registry.register(DemonstrationProjectionProfile())
result = project(request, registry=registry)
print(json.dumps(result.to_dict(), indent=2))
