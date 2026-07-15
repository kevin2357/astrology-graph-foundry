from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from astro_analysis_sdk.common.io import read_json
from semantic_projection.contracts import ProjectionContext
from astro_analysis_sdk.projection_adapter import (
    project_dataset,
    projection_materialization_view,
)

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "scripts" / "outputs" / "kevin_bre_test"
OUTPUT_DIR = ROOT / "scripts" / "outputs" / "chunk27_projection_qa"

FIXTURES: dict[str, dict[str, str]] = {
    "kevin_natal_orthodox": {
        "source": "kevin_natal_dataset.json",
        "profile_id": "orthodox_astrology.v1",
        "profile_version": "1.0.0",
        "context": "examples/contexts/orthodox_general_context.json",
    },
    "kevin_natal_cognitive": {
        "source": "kevin_natal_dataset.json",
        "profile_id": "cognitive_architecture_demo.v0",
        "profile_version": "0.2.0",
        "context": "examples/contexts/cognitive_architecture_general_context.json",
    },
    "kevin_natal_woofmapped": {
        "source": "kevin_natal_dataset.json",
        "profile_id": "woofmapped_astrology.v0",
        "profile_version": "0.1.0",
        "context": "examples/contexts/woofmapped_doghouse_general_context.json",
    },
    "bre_kevin_synastry_general": {
        "source": "bre_kevin_synastry_dataset.full.json",
        "profile_id": "orthodox_astrology.v1",
        "profile_version": "1.0.0",
        "context": "examples/contexts/orthodox_relationship_general_context.json",
    },
    "bre_kevin_synastry_professional": {
        "source": "bre_kevin_synastry_dataset.full.json",
        "profile_id": "orthodox_astrology.v1",
        "profile_version": "1.0.0",
        "context": "examples/contexts/orthodox_relationship_professional_context.json",
    },
    "kevin_bre_composite_orthodox": {
        "source": "kevin_bre_composite_dataset.json",
        "profile_id": "orthodox_astrology.v1",
        "profile_version": "1.0.0",
        "context": "examples/contexts/orthodox_general_context.json",
    },
    "kevin_bre_davison_orthodox": {
        "source": "kevin_bre_davison.json",
        "profile_id": "orthodox_astrology.v1",
        "profile_version": "1.0.0",
        "context": "examples/contexts/orthodox_general_context.json",
    },
}

MODES = ("full", "standard", "summary", "forensic")


def verify_transit_rejection() -> dict[str, Any]:
    source_path = SOURCE_DIR / "kevin_2026-01-01_to_2026-02-01_transit.full.json"
    if not source_path.exists():
        return {
            "fixture": "kevin_one_month_transit_orthodox",
            "expected_rejection": True,
            "status": "source_missing",
            "source": str(source_path.relative_to(ROOT)),
        }
    source = read_json(source_path)
    try:
        project_dataset(source, profile_id="orthodox_astrology.v1", profile_version="1.0.0")
    except NotImplementedError as exc:
        return {
            "fixture": "kevin_one_month_transit_orthodox",
            "expected_rejection": True,
            "status": "rejected_as_expected",
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }
    raise AssertionError("Transit package unexpectedly projected as a static graph")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate_fixture(label: str) -> dict[str, Any]:
    spec = FIXTURES[label]
    source_path = SOURCE_DIR / spec["source"]
    context_path = ROOT / spec["context"]
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    source = read_json(source_path)
    context = ProjectionContext.from_dict(read_json(context_path))

    started = perf_counter()
    full = project_dataset(
        source,
        profile_id=spec["profile_id"],
        profile_version=spec["profile_version"],
        context=context,
    )
    projection_seconds = perf_counter() - started

    fixture_dir = OUTPUT_DIR / label
    sizes: dict[str, int] = {}
    for mode in MODES:
        materialized = projection_materialization_view(full, mode)
        path = fixture_dir / f"{label}.{mode}.json"
        write_json(path, materialized)
        sizes[mode] = path.stat().st_size

    return {
        "fixture": label,
        "source": str(source_path.relative_to(ROOT)),
        "profile_id": spec["profile_id"],
        "profile_version": spec["profile_version"],
        "context": spec["context"],
        "projection_seconds": round(projection_seconds, 6),
        "object_count": len(full.get("objects") or []),
        "relationship_count": len(full.get("relationships") or []),
        "mapping_execution_count": len((full.get("audit") or {}).get("mapping_executions") or []),
        "output_bytes": sizes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", choices=sorted(FIXTURES))
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        print("\n".join(sorted(FIXTURES)))
        return

    labels = [args.fixture] if args.fixture else list(FIXTURES)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_results = []
    for index, label in enumerate(labels, start=1):
        print(f"[{index}/{len(labels)}] {label}", flush=True)
        result = generate_fixture(label)
        run_results.append(result)
        write_json(OUTPUT_DIR / f"{label}.generation_result.json", result)
        print(
            f"  {result['object_count']} objects, "
            f"{result['relationship_count']} relationships, "
            f"{result['projection_seconds']:.3f}s"
        )

    if not args.fixture:
        transit_result = verify_transit_rejection()
        run_results.append(transit_result)
        write_json(OUTPUT_DIR / "chunk27_transit_rejection_result.json", transit_result)
        write_json(OUTPUT_DIR / "chunk27_projection_generation_results.json", run_results)


if __name__ == "__main__":
    main()
