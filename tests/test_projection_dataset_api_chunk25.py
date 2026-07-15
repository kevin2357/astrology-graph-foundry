from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from astrology_graph_foundry import (
    enforce_unmapped_threshold,
    project_dataset,
    projection_summary_view,
)
from semantic_projection import ProjectionContext


def package_fixture() -> dict:
    return {
        "metadata": {
            "analysis_type": "natal_dataset",
            "source_chart_id": "natal:fixture",
            "source_chart_ids": ["natal:fixture"],
            "sensor_instance_id": "natal:fixture",
        },
        "canonical_astrology_graph": {
            "graph_type": "canonical_astrology_graph",
            "graph_version": "1.3.0",
            "objects": [
                {
                    "id": "natal:Mars",
                    "name": "Mars",
                    "object_type": "planet_or_point",
                    "structural_strength_score": 0.8,
                },
                {
                    "id": "natal:Venus",
                    "name": "Venus",
                    "object_type": "planet_or_point",
                    "structural_strength_score": 0.9,
                },
                {
                    "id": "natal:Unsupported",
                    "name": "Unsupported",
                    "object_type": "calculated_point",
                },
            ],
            "relationships": [{
                "id": "aspect:Mars:square:Venus",
                "relationship_type": "ASPECT",
                "source_id": "natal:Mars",
                "target_id": "natal:Venus",
                "aspect": "square",
                "orb": 1.0,
                "structural_strength_score": 0.75,
            }],
        },
        "structural_evidence_graph": {"graph_version": "1.3.0"},
        "projection_views": {"orthodox_astrology.v1": {"theme_metrics": []}},
    }


def test_project_dataset_needs_no_calculation_pipeline():
    source = package_fixture()
    before = json.dumps(source, sort_keys=True)
    result = project_dataset(source)
    assert result["metadata"]["profile_id"] == "orthodox_astrology.v1"
    assert result["metadata"]["source_dataset_analysis_type"] == "natal_dataset"
    assert len(result["objects"]) == 2
    assert len(result["relationships"]) == 1
    assert json.dumps(source, sort_keys=True) == before


def test_project_dataset_accepts_explicit_context():
    context = ProjectionContext(
        context_id="orthodox.general.v1",
        context_version="1.0.0",
        subject_scope="individual",
        target_domain="orthodox_astrology.v1",
        application_context="general_interpretation",
    )
    result = project_dataset(package_fixture(), context=context)
    assert result["metadata"]["context_id"] == "orthodox.general.v1"


def test_summary_view_omits_graph_and_mapping_execution_payloads():
    projected = project_dataset(package_fixture())
    summary = projection_summary_view(projected)
    assert "objects" not in summary
    assert "relationships" not in summary
    assert "audit" not in summary
    assert summary["coverage"]["source_object_count"] == 3
    assert summary["diagnostics_summary"]["unmapped_source_count"] == 1


def test_unmapped_threshold_enforcement():
    projected = project_dataset(package_fixture())
    with pytest.raises(ValueError, match="exceeds threshold"):
        enforce_unmapped_threshold(projected, 0.1)
    enforce_unmapped_threshold(projected, 0.5)


def test_analysis_view_is_rejected_as_source():
    with pytest.raises(ValueError, match="canonical_astrology_graph"):
        project_dataset({"metadata": {"analysis_type": "natal_analysis"}})


def test_cli_projects_saved_dataset_and_writes_summary(tmp_path: Path):
    source = tmp_path / "source.json"
    output = tmp_path / "projection.summary.json"
    source.write_text(json.dumps(package_fixture()), encoding="utf-8")

    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "astrology_graph_foundry.cli",
            "project",
            "--source-dataset",
            str(source),
            "--projection-profile",
            "orthodox_astrology.v1",
            "--output-mode",
            "summary",
            "--out",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert run.returncode == 0, run.stderr
    value = json.loads(output.read_text(encoding="utf-8"))
    assert value["metadata"]["profile_id"] == "orthodox_astrology.v1"
    assert "objects" not in value


def test_cli_unknown_profile_errors_clearly(tmp_path: Path):
    source = tmp_path / "source.json"
    output = tmp_path / "projection.json"
    source.write_text(json.dumps(package_fixture()), encoding="utf-8")

    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "astrology_graph_foundry.cli",
            "project",
            "--source-dataset",
            str(source),
            "--projection-profile",
            "unknown.v1",
            "--out",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert run.returncode != 0
    assert "Unknown projection profile" in run.stderr


def test_cli_invalid_context_errors_clearly(tmp_path: Path):
    source = tmp_path / "source.json"
    context = tmp_path / "context.json"
    output = tmp_path / "projection.json"
    source.write_text(json.dumps(package_fixture()), encoding="utf-8")
    context.write_text(json.dumps({"context_id": "broken"}), encoding="utf-8")

    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "astrology_graph_foundry.cli",
            "project",
            "--source-dataset",
            str(source),
            "--projection-context",
            str(context),
            "--out",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert run.returncode != 0
    assert "Projection failed" in run.stderr
