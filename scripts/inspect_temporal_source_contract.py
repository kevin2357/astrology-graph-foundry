from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


def _compact_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    parser.add_argument("--schema-root", default="src/astrology_graph_foundry/schemas")
    parser.add_argument("--out")
    args = parser.parse_args()

    artifact_path = Path(args.artifact)
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    package_type = str((data.get("metadata") or {}).get("package_type") or "")
    schema_name = {
        "canonical_temporal_activation_graph": "canonical_temporal_activation_graph_v1.schema.json",
        "temporal_projection_source_bundle": "temporal_projection_source_bundle_v1.schema.json",
    }.get(package_type)
    if schema_name is None:
        raise SystemExit(f"Unsupported temporal artifact package_type={package_type!r}")

    schema_root = Path(args.schema_root).resolve()
    schema = json.loads((schema_root / schema_name).read_text(encoding="utf-8"))
    registry = Registry()
    temporal_schema_path = schema_root / "canonical_temporal_activation_graph_v1.schema.json"
    if temporal_schema_path.exists():
        temporal_schema = json.loads(temporal_schema_path.read_text(encoding="utf-8"))
        registry = registry.with_resource(
            schema_root.as_uri() + "/canonical_temporal_activation_graph_v1.schema.json",
            Resource.from_contents(temporal_schema),
        ).with_resource(
            "canonical_temporal_activation_graph_v1.schema.json",
            Resource.from_contents(temporal_schema),
        )
    errors = sorted(
        Draft202012Validator(schema, registry=registry).iter_errors(data),
        key=lambda error: list(error.path),
    )

    temporal = (
        data
        if package_type == "canonical_temporal_activation_graph"
        else data.get("temporal_source_graph") or {}
    )
    activations = temporal.get("activations") or []
    single_observation_count = sum(
        1 for row in activations if int(row.get("observation_count") or 0) == 1
    )
    warning_count = int((temporal.get("summary") or {}).get("warning_count") or 0)
    normalization_diagnostics: list[dict[str, Any]] = []
    if activations and single_observation_count == len(activations):
        normalization_diagnostics.append(
            {
                "severity": "error",
                "code": "temporal_normalization_degenerated_to_single_observation_events",
                "message": (
                    "Every activation contains exactly one observation state; "
                    "the source observation series may not have joined to arc rows."
                ),
            }
        )
    if activations and warning_count == len(activations):
        normalization_diagnostics.append(
            {
                "severity": "error",
                "code": "every_activation_uses_arc_summary_fallback",
                "message": (
                    "Every activation emitted an observation-join warning; inspect "
                    "candidate identity and source-shape normalization."
                ),
            }
        )

    result = {
        "artifact": str(artifact_path),
        "package_type": package_type,
        "schema": schema_name,
        "schema_valid": not errors,
        "schema_errors": [
            {"path": list(error.path), "message": error.message} for error in errors
        ],
        "graph_id": (temporal.get("metadata") or {}).get("graph_id"),
        "summary": temporal.get("summary") or {},
        "activation_hash": _compact_hash(activations),
        "activation_ids_unique": len({row.get("id") for row in activations})
        == len(activations),
        "sequence_passes": {
            sequence: sorted(
                int(row.get("pass_index") or 0)
                for row in activations
                if row.get("sequence_id") == sequence
            )
            for sequence in sorted(
                {str(row.get("sequence_id")) for row in activations}
            )
        },
        "missing_directionality": [
            row.get("id")
            for row in activations
            if not row.get("activator_ref") or not row.get("target_ref")
        ],
        "false_exactness_risk": [
            row.get("id")
            for row in activations
            if row.get("exact_at")
            and (row.get("exactness") or {}).get("status") != "sampled_exact"
        ],
        "normalization_health": {
            "single_observation_activation_count": single_observation_count,
            "multi_observation_activation_count": len(activations) - single_observation_count,
            "warning_count": warning_count,
            "diagnostics": normalization_diagnostics,
        },
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(rendered)

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
