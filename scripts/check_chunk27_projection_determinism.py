from __future__ import annotations

import hashlib
import json
from pathlib import Path

from astro_analysis_sdk.common.io import read_json
from semantic_projection.contracts import ProjectionContext
from astro_analysis_sdk.projection_adapter import project_dataset, projection_materialization_view

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "scripts" / "outputs" / "chunk27_projection_qa" / "determinism"


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    source = read_json(ROOT / "scripts/outputs/kevin_bre_test/kevin_natal_dataset.json")
    context = ProjectionContext.from_dict(
        read_json(ROOT / "examples/contexts/cognitive_architecture_general_context.json")
    )
    paths = []
    for run_number in (1, 2):
        full = project_dataset(
            source,
            profile_id="cognitive_architecture_demo.v0",
            profile_version="0.2.0",
            context=context,
        )
        standard = projection_materialization_view(full, "standard")
        path = OUTPUT_DIR / f"kevin_natal_cognitive.standard.run{run_number}.json"
        write(path, standard)
        paths.append(path)

    first = paths[0].read_bytes()
    second = paths[1].read_bytes()
    result = {
        "report_type": "projection_determinism_check.v1",
        "byte_identical": first == second,
        "bytes": len(first),
        "sha256_run1": hashlib.sha256(first).hexdigest(),
        "sha256_run2": hashlib.sha256(second).hexdigest(),
        "run1": str(paths[0].relative_to(ROOT)),
        "run2": str(paths[1].relative_to(ROOT)),
    }
    write(OUTPUT_DIR / "chunk27_determinism_result.json", result)
    print(json.dumps(result, indent=2))
    if not result["byte_identical"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
