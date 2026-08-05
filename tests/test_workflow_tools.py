from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
TOOLS = ROOT / "tools"


def run_tool(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / name), *args],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize(
    "name",
    ("build_natal.py", "build_transit.py", "build_synastry.py", "build_temporal_source.py"),
)
def test_workflow_tools_expose_help(name: str):
    result = run_tool(name, "--help")
    assert result.returncode == 0, result.stderr
    assert "--dry-run" in result.stdout


def test_natal_cached_dry_run_delegates_to_cli(tmp_path: Path):
    person = tmp_path / "person.jsonl"
    person.write_text("", encoding="utf-8")
    result = run_tool(
        "build_natal.py",
        "--provider", "cached",
        "--person-jsonl", str(person),
        "--out-dir", str(tmp_path / "out"),
        "--stem", "sample",
        "--analysis",
        "--dry-run",
    )
    assert result.returncode == 0, result.stderr
    assert "astrology_graph_foundry.cli natal" in result.stdout
    assert "--out-analysis" in result.stdout
    assert "sample.full.json" in result.stdout


def test_transit_dry_run_builds_compact_and_optional_full_paths(tmp_path: Path):
    target = tmp_path / "natal.json"
    target.write_text("{}", encoding="utf-8")
    result = run_tool(
        "build_transit.py",
        "--target", str(target),
        "--start", "2026-01-01",
        "--end", "2026-02-01",
        "--out-dir", str(tmp_path / "out"),
        "--streaming-profile", "compact",
        "--compression", "gzip",
        "--full",
        "--dry-run",
    )
    assert result.returncode == 0, result.stderr
    assert "astrology_graph_foundry.cli transit" in result.stdout
    assert "--out-analysis" in result.stdout
    assert "transit.streaming_index.json.gz" in result.stdout
    assert "--out-full" in result.stdout


def test_synastry_saved_dry_run_uses_two_natal_packages(tmp_path: Path):
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    first.write_text("{}", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")
    result = run_tool(
        "build_synastry.py",
        "--mode", "saved",
        "--person-a-natal", str(first),
        "--person-b-natal", str(second),
        "--out-dir", str(tmp_path / "out"),
        "--non-interactive",
        "--dry-run",
    )
    assert result.returncode == 0, result.stderr
    assert "astrology_graph_foundry.cli synastry" in result.stdout
    assert "--person-a-natal-dataset" in result.stdout
    assert "--person-b-natal-dataset" in result.stdout
    assert "--out-full" not in result.stdout


def test_temporal_source_dry_run_delegates_both_exports(tmp_path: Path):
    source = tmp_path / "transit.json"
    target = tmp_path / "natal.json"
    source.write_text("{}", encoding="utf-8")
    target.write_text("{}", encoding="utf-8")
    result = run_tool(
        "build_temporal_source.py",
        "--source", str(source),
        "--target", str(target),
        "--out-dir", str(tmp_path / "out"),
        "--target-set", "core",
        "--dry-run",
    )
    assert result.returncode == 0, result.stderr
    assert "export-temporal-graph" in result.stdout
    assert "export-temporal-projection-source" in result.stdout
    assert "--transit-target-set core" in result.stdout


def test_unattended_missing_required_input_fails_without_prompt(tmp_path: Path):
    result = run_tool(
        "build_transit.py",
        "--date", "2026-01-01",
        "--out-dir", str(tmp_path / "out"),
        "--non-interactive",
        "--dry-run",
    )
    assert result.returncode == 2
    assert "Target package is required for unattended execution" in result.stderr
