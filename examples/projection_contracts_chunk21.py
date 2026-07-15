"""Build and validate a tiny Chunk 2.1 projection request.

This example intentionally does not execute a projection. The generic engine
begins in Chunk 2.2.
"""

from semantic_projection import (
    ProjectionContext,
    ProjectionRequest,
    projection_request_id,
    validate_projection_request,
)

source_identity = {
    "source_chart_id": "natal:example",
    "source_chart_ids": ["natal:example"],
    "sensor_instance_id": "natal:example",
}
context = ProjectionContext(
    context_id="orthodox.general.v1",
    context_version="1.0.0",
    subject_scope="individual",
    target_domain="orthodox_astrology",
    application_context="general_interpretation",
).to_dict()
source_graph = {
    "graph_type": "canonical_astrology_graph",
    "graph_version": "1.3.0",
    "objects": [],
    "relationships": [],
}
request_id = projection_request_id(
    profile_id="orthodox_astrology.v1",
    profile_version="1.0.0",
    source_identity=source_identity,
    context=context,
)
request = ProjectionRequest(
    request_id=request_id,
    profile_id="orthodox_astrology.v1",
    profile_version="1.0.0",
    source_graph=source_graph,
    structural_evidence={},
    source_identity=source_identity,
    context=context,
)
validate_projection_request(request.to_dict())
print(request_id)
