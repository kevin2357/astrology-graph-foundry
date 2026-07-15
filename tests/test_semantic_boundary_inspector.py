import json
import subprocess
import sys
from pathlib import Path


def test_semantic_boundary_inspector_reports_clean_package(tmp_path):
    package = {
        "metadata": {"analysis_type": "test"},
        "semantic_boundary": {"legacy_fields_dual_written": True},
        "canonical_astrology_graph": {
            "objects": [{
                "id": "obj:1",
                "evidence_metadata": {"evidence_tier": "core"},
                "structural_strength_score": 0.8,
            }],
            "relationships": [],
        },
        "structural_evidence_graph": {"independence_group_count": 1},
        "projection_views": {
            "orthodox_astrology.v1": {
                "theme_metrics": [],
                "claim_candidates": [],
            }
        },
    }
    source = tmp_path / "package.json"
    source.write_text(json.dumps(package), encoding="utf-8")
    script = Path(__file__).parents[1] / "scripts" / "inspect_semantic_boundary.py"
    result = subprocess.run(
        [sys.executable, str(script), str(source)],
        check=True,
        capture_output=True,
        text=True,
    )
    output = json.loads(result.stdout)
    assert output["package_count"] == 1
    assert output["all_materialized_canonical_graphs_theme_clean"] is True
    assert output["all_materialized_canonical_rows_have_evidence_metadata"] is True
    assert output["all_materialized_canonical_rows_have_structural_strength"] is True
