from __future__ import annotations

import gzip
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
from astrology_graph_foundry.pipelines import solar_return, transit  # noqa: E402


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _find_fixture(preferred: str, fallback: str) -> Path:
    candidate = INPUT_DIR / preferred
    if candidate.exists():
        return candidate
    fallback_path = ROOT / "scripts" / "outputs" / "kevin_bre_test" / fallback
    if fallback_path.exists():
        return fallback_path
    raise FileNotFoundError(
        f"Missing fixture {candidate}. Also checked historical fallback {fallback_path}."
    )


def _run_pytest() -> dict[str, Any]:
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


def _validate(view: dict[str, Any]) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return ["jsonschema is not installed"]
    schema = read_json(
        ROOT
        / "src"
        / "astrology_graph_foundry"
        / "schemas"
        / "transit_streaming_index_v2.schema.json"
    )
    return [error.message for error in Draft202012Validator(schema).iter_errors(view)]


def main() -> int:
    # Clear only generated QA outputs, retaining the directory.
    for path in OUTPUT_DIR.iterdir():
        if path.name == ".gitkeep":
            continue
        if path.is_file():
            path.unlink()

    summary: dict[str, Any] = {"qa_contract": "foundry_one_command_qa.v1"}
    summary["pytest"] = _run_pytest()

    transit_path = _find_fixture(
        "transit.full.json",
        "kevin_2026-01-01_to_2026-02-01_transit.full.json",
    )
    package = read_json(transit_path)
    summary["fixture"] = str(transit_path.relative_to(ROOT))

    profile_results: dict[str, Any] = {}
    for profile in ("standard", "compact", "game"):
        view = transit.streaming_index(package, profile=profile)
        out = OUTPUT_DIR / f"transit.{profile}.json"
        write_json(out, view)
        gz = OUTPUT_DIR / f"transit.{profile}.json.gz"
        write_json(gz, view)
        errors = _validate(view)
        profile_results[profile] = {
            "json_bytes": out.stat().st_size,
            "gzip_bytes": gz.stat().st_size,
            "compression_ratio": round(gz.stat().st_size / out.stat().st_size, 6),
            "candidate_registry_count": len(view.get("candidate_registry", {})),
            "day_count": len(view.get("days_by_date", view.get("days", []))),
            "schema_valid": not errors,
            "schema_errors": errors[:20],
        }
    summary["profiles"] = profile_results

    game = transit.streaming_index(package, profile="game")
    run1 = OUTPUT_DIR / "game_run1.json"
    run2 = OUTPUT_DIR / "game_run2.json"
    gz1 = OUTPUT_DIR / "game_run1.json.gz"
    gz2 = OUTPUT_DIR / "game_run2.json.gz"
    write_json(run1, game)
    write_json(run2, game)
    write_json(gz1, game)
    write_json(gz2, game)
    determinism = {
        "json_byte_identical": run1.read_bytes() == run2.read_bytes(),
        "json_sha256_run1": _sha(run1),
        "json_sha256_run2": _sha(run2),
        "gzip_byte_identical": gz1.read_bytes() == gz2.read_bytes(),
        "gzip_sha256_run1": _sha(gz1),
        "gzip_sha256_run2": _sha(gz2),
    }
    write_json(OUTPUT_DIR / "determinism_result.json", determinism)
    summary["determinism"] = determinism

    negative: dict[str, Any]
    try:
        transit.streaming_index(package, profile="not-a-profile")
        negative = {"passed": False, "error": "invalid profile unexpectedly accepted"}
    except ValueError as exc:
        negative = {"passed": True, "exception_type": type(exc).__name__, "message": str(exc)}
    write_json(OUTPUT_DIR / "negative_test.json", negative)
    summary["negative_test"] = negative

    try:
        solar_path = _find_fixture("solar_return.full.json", "kevin_2026_solar_return.json")
        solar_package = read_json(solar_path)
        solar_view = solar_return.analysis_view(solar_package)
        write_json(OUTPUT_DIR / "solar_return.analysis.json", solar_view)
        families: dict[str, int] = {}
        for row in solar_view.get("top_relationships", []):
            family = str((row.get("evidence_metadata") or {}).get("derivation_family") or "unknown")
            families[family] = families.get(family, 0) + 1
        summary["solar_return"] = {
            "fixture": str(solar_path.relative_to(ROOT)),
            "output_bytes": (OUTPUT_DIR / "solar_return.analysis.json").stat().st_size,
            "relationship_family_distribution": dict(sorted(families.items())),
        }
    except FileNotFoundError as exc:
        summary["solar_return"] = {"skipped": True, "reason": str(exc)}

    summary["passed"] = bool(
        summary["pytest"]["exit_code"] == 0
        and all(row["schema_valid"] for row in profile_results.values())
        and all(determinism[key] for key in ("json_byte_identical", "gzip_byte_identical"))
        and negative["passed"]
    )
    write_json(OUTPUT_DIR / "artifact_profile.json", profile_results)
    write_json(OUTPUT_DIR / "qa_summary.json", summary)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
