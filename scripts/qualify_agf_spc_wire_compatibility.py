"""External integration harness for independently installed AGF/SPC artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

from semantic_projection import ProjectionOptions, ProjectionRequest, project_with_builtin_profiles, projection_request_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-package", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    package = json.loads(args.source_package.read_text(encoding="utf-8"))
    graph = deepcopy(package["canonical_astrology_graph"])
    metadata = package.get("metadata") or {}
    identity = {
        "source_chart_id": metadata.get("source_chart_id"),
        "source_chart_ids": metadata.get("source_chart_ids") or [],
        "sensor_instance_id": metadata.get("sensor_instance_id"),
    }
    context = {
        "context_id": "woofmapped.doghouse.general.v0",
        "context_version": "0.1.0",
        "subject_scope": "dog",
        "target_domain": "woofmapped_astrology.v0",
        "application_context": "woofmapped_natal_projection",
        "audience": "handler_general",
        "output_intent": "structured_semantic_model",
        "constraints": {"house_mapping_policy": "doghouse"},
        "parameters": {},
        "extensions": {},
    }
    options = ProjectionOptions().to_dict()
    request = ProjectionRequest(
        request_id=projection_request_id(
            profile_id="woofmapped_astrology.v0",
            profile_version="0.1.0",
            source_identity=identity,
            context=context,
            options=options,
        ),
        profile_id="woofmapped_astrology.v0",
        profile_version="0.1.0",
        source_graph=graph,
        structural_evidence=deepcopy(package.get("structural_evidence_graph") or {}),
        source_identity=identity,
        context=context,
        source_registries={
            "theme_registry": deepcopy(package.get("theme_registry") or {}),
            "operator_registry": deepcopy(package.get("operator_registry") or {}),
            "object_registries": deepcopy(package.get("object_registries") or {}),
            "natal_context_registries": deepcopy(package.get("natal_context_registries") or {}),
        },
        options=options,
    )
    projected = project_with_builtin_profiles(request).to_dict()
    if projected["source_identity"]["source_chart_id"] != identity["source_chart_id"]:
        raise SystemExit("SPC did not preserve source_chart_id")
    source_ids = {str(row["id"]) for row in graph.get("objects") or []} | {
        str(row["id"]) for row in graph.get("relationships") or []
    }
    projected_refs = {
        str(ref).removeprefix("canonical:object:").removeprefix("canonical:relationship:")
        for row in (projected.get("objects") or []) + (projected.get("relationships") or [])
        for ref in row.get("source_refs") or []
    }
    result = {
        "status": "passed",
        "source_chart_id": identity["source_chart_id"],
        "source_graph_version": graph.get("graph_version"),
        "source_object_count": len(graph.get("objects") or []),
        "source_relationship_count": len(graph.get("relationships") or []),
        "projected_object_count": len(projected.get("objects") or []),
        "projected_relationship_count": len(projected.get("relationships") or []),
        "projected_source_ref_count": len(projected_refs),
        "all_projected_refs_resolve": projected_refs <= source_ids,
        "source_package_sha256": hashlib.sha256(args.source_package.read_bytes()).hexdigest(),
    }
    if not result["all_projected_refs_resolve"]:
        raise SystemExit("SPC emitted an unresolved source reference")
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
