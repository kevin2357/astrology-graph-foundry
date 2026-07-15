from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from astrology_graph_foundry.common.io import read_json
from semantic_projection.ids import stable_hash


def json_size(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def profile(path: Path) -> dict[str, Any]:
    started = perf_counter()
    data = read_json(path)
    elapsed = perf_counter() - started
    audit = data.get("audit") or {}
    diagnostics = data.get("diagnostics") or {}
    registry = data.get("projected_term_registry") or {}
    scope = (data.get("summary") or {}).get("profile_scope_coverage") or {}
    return {
        "path": str(path),
        "bytes_on_disk": path.stat().st_size,
        "json_compact_bytes": json_size(data),
        "read_seconds": round(elapsed, 6),
        "materialization_mode": (data.get("metadata") or {}).get("materialization_mode", "legacy_or_full"),
        "object_count": len(data.get("objects") or []),
        "relationship_count": len(data.get("relationships") or []),
        "registry_term_count": len(registry.get("terms") or {}),
        "mapping_execution_count": len(audit.get("mapping_executions") or []),
        "unmapped_source_ref_count": len(audit.get("unmapped_source_refs") or diagnostics.get("unmapped_source_refs") or []),
        "eligible_object_coverage": (scope.get("objects") or {}).get("declared_scope_coverage"),
        "eligible_relationship_coverage": (scope.get("relationships") or {}).get("declared_scope_coverage"),
        "object_hash": stable_hash(data.get("objects") or []),
        "relationship_hash": stable_hash(data.get("relationships") or []),
        "audit_bytes": json_size(audit),
        "diagnostics_bytes": json_size(diagnostics),
        "registry_bytes": json_size(registry),
        "graph_rows_bytes": json_size({
            "objects": data.get("objects") or [],
            "relationships": data.get("relationships") or [],
        }),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()

    resolved_paths: list[Path] = []
    for value in args.paths:
        path = Path(value)
        if path.is_dir():
            pattern = "**/*.json" if args.recursive else "*.json"
            resolved_paths.extend(sorted(path.glob(pattern)))
        else:
            resolved_paths.append(path)

    out_path = Path(args.out).resolve() if args.out else None
    resolved_paths = [
        path for path in resolved_paths
        if path.is_file()
        and (out_path is None or path.resolve() != out_path)
        and not path.name.endswith(".generation_result.json")
        and path.name != "chunk27_projection_generation_results.json"
    ]
    rows = [profile(path) for path in resolved_paths]
    result = {
        "report_type": "projection_artifact_profile.v1",
        "artifact_count": len(rows),
        "artifacts": rows,
    }
    text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
