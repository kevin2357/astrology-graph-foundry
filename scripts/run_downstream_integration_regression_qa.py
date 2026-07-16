from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "outputs" / "fixture_test_files"
OUTPUT_DIR = ROOT / "outputs" / "fixture_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.environ["ASTROLOGY_FOUNDRY_LOG_FILE"] = str(OUTPUT_DIR / "foundry.log")

from astrology_graph_foundry.common.io import read_json, write_json  # noqa: E402
from astrology_graph_foundry.pipelines import transit  # noqa: E402
from astrology_graph_foundry.temporal_projection_adapter import (  # noqa: E402
    build_temporal_projection_source_bundle,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(preferred: str, fallback: str) -> Path:
    candidate = INPUT_DIR / preferred
    if candidate.exists():
        return candidate
    fallback_path = ROOT / "outputs" / "kevin_bre_test" / fallback
    if fallback_path.exists():
        return fallback_path
    fallback_path = ROOT / "scripts" / "outputs" / "kevin_bre_test" / fallback
    if fallback_path.exists():
        return fallback_path
    raise FileNotFoundError(f"Missing fixture {preferred}; checked canonical and historical locations.")


def _pytest() -> dict[str, Any]:
    log = OUTPUT_DIR / "pytest.log"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log.write_text(proc.stdout, encoding="utf-8")
    return {"exit_code": proc.returncode, "log": str(log.relative_to(ROOT))}


def _assert_game(view: dict[str, Any], expected_days: int | None = None) -> dict[str, Any]:
    days = view.get("days_by_date") or {}
    registry = view.get("candidate_registry") or {}
    unresolved = []
    contact_count = 0
    for date, day in days.items():
        for contact in day.get("contacts", []) or []:
            contact_count += 1
            if contact.get("candidate_id") not in registry:
                unresolved.append({"date": date, "candidate_id": contact.get("candidate_id")})
    mean_node_ids = [candidate_id for candidate_id in registry if "Mean_Node" in candidate_id]
    true_node_ids = [candidate_id for candidate_id in registry if "True_Node" in candidate_id]
    return {
        "day_count": len(days),
        "candidate_registry_count": len(registry),
        "contact_count": contact_count,
        "unresolved_contacts": unresolved,
        "expected_day_count": expected_days,
        "period_complete": expected_days is None or len(days) == expected_days,
        "mean_node_candidate_ids": mean_node_ids,
        "true_node_candidate_count": len(true_node_ids),
        "daily_sky_nonempty_days": sum(
            bool((day.get("daily_sky") or {}).get("positions"))
            for day in days.values()
        ),
    }


def main() -> int:
    for path in OUTPUT_DIR.iterdir():
        if path.name in {".gitkeep", "qa_runner.log"}:
            continue
        if path.is_file():
            path.unlink()

    summary: dict[str, Any] = {
        "qa_contract": "foundry_downstream_integration_regression.v1",
        "pytest": _pytest(),
    }

    full_path = _fixture(
        "transit.full.json",
        "kevin_2026-01-01_to_2026-02-01_transit.full.json",
    )
    natal_path = _fixture("natal.full.json", "kevin_natal_dataset.json")
    full = read_json(full_path)
    natal = read_json(natal_path)

    standard = transit.streaming_index(full, profile="standard")
    write_json(OUTPUT_DIR / "transit.standard.json", standard)

    game1 = transit.streaming_index(standard, profile="game", target_set="gameplay")
    game2 = transit.streaming_index(standard, profile="game", target_set="gameplay")
    write_json(OUTPUT_DIR / "transit.game.run1.json", game1)
    write_json(OUTPUT_DIR / "transit.game.run2.json", game2)
    write_json(OUTPUT_DIR / "transit.game.run1.json.gz", game1)
    write_json(OUTPUT_DIR / "transit.game.run2.json.gz", game2)

    expected_days = (full.get("period") or {}).get("day_count")
    game_health = _assert_game(game1, expected_days=expected_days)
    summary["game_materialization"] = {
        **game_health,
        "json_byte_identical": (
            (OUTPUT_DIR / "transit.game.run1.json").read_bytes()
            == (OUTPUT_DIR / "transit.game.run2.json").read_bytes()
        ),
        "gzip_byte_identical": (
            (OUTPUT_DIR / "transit.game.run1.json.gz").read_bytes()
            == (OUTPUT_DIR / "transit.game.run2.json.gz").read_bytes()
        ),
        "json_sha256": _sha(OUTPUT_DIR / "transit.game.run1.json"),
        "gzip_sha256": _sha(OUTPUT_DIR / "transit.game.run1.json.gz"),
    }

    bundle1 = build_temporal_projection_source_bundle(
        standard,
        target_package=natal,
        target_set="gameplay",
    )
    bundle2 = build_temporal_projection_source_bundle(
        standard,
        target_package=natal,
        target_set="gameplay",
    )
    write_json(OUTPUT_DIR / "temporal_projection_source.run1.json", bundle1)
    write_json(OUTPUT_DIR / "temporal_projection_source.run2.json", bundle2)
    static_graph = bundle1.get("static_source_graph") or {}
    target_id = (bundle1.get("target_identity") or {}).get("chart_id")
    summary["temporal_bundle"] = {
        "static_graph_nonempty": bool(static_graph),
        "static_graph_object_count": len(static_graph.get("objects", []) or []),
        "static_graph_relationship_count": len(static_graph.get("relationships", []) or []),
        "static_graph_chart_id": static_graph.get("source_chart_id"),
        "target_chart_id": target_id,
        "identity_matches": static_graph.get("source_chart_id") == target_id,
        "activation_count": len(
            ((bundle1.get("temporal_source_graph") or {}).get("activations") or [])
        ),
        "mean_node_activation_count": sum(
            "Mean_Node" in str(row.get("target_ref") or "")
            for row in ((bundle1.get("temporal_source_graph") or {}).get("activations") or [])
        ),
        "target_set": (bundle1.get("metadata") or {}).get("transit_target_set"),
        "byte_identical": (
            (OUTPUT_DIR / "temporal_projection_source.run1.json").read_bytes()
            == (OUTPUT_DIR / "temporal_projection_source.run2.json").read_bytes()
        ),
    }

    negative: dict[str, Any]
    try:
        build_temporal_projection_source_bundle(standard)
        negative = {"passed": False, "message": "Missing target dataset unexpectedly accepted."}
    except ValueError as exc:
        negative = {
            "passed": True,
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }
    write_json(OUTPUT_DIR / "negative_test.json", negative)
    summary["negative_test"] = negative

    checks = [
        summary["pytest"]["exit_code"] == 0,
        game_health["period_complete"],
        game_health["candidate_registry_count"] > 0,
        game_health["contact_count"] > 0,
        not game_health["unresolved_contacts"],
        not game_health["mean_node_candidate_ids"],
        summary["game_materialization"]["json_byte_identical"],
        summary["game_materialization"]["gzip_byte_identical"],
        summary["temporal_bundle"]["static_graph_nonempty"],
        summary["temporal_bundle"]["identity_matches"],
        summary["temporal_bundle"]["activation_count"] > 0,
        summary["temporal_bundle"]["mean_node_activation_count"] == 0,
        summary["temporal_bundle"]["byte_identical"],
        negative["passed"],
    ]
    summary["passed"] = all(checks)
    write_json(OUTPUT_DIR / "qa_summary.json", summary)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
