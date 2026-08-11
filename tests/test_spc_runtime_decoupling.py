from __future__ import annotations

import ast
from pathlib import Path

from astrology_graph_foundry.doctor import REQUIRED_MODES

ROOT = Path(__file__).parents[1]
PACKAGE_ROOT = ROOT / "src" / "astrology_graph_foundry"


def test_distribution_has_no_spc_dependency():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "semantic-projection-core" not in pyproject


def test_runtime_has_no_semantic_projection_imports():
    offenders = []
    for path in PACKAGE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            if any(name == "semantic_projection" or name.startswith("semantic_projection.") for name in names):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_projection_execution_is_not_an_agf_public_surface():
    import astrology_graph_foundry as agf

    assert not hasattr(agf, "project_dataset")
    assert not (PACKAGE_ROOT / "projection_adapter.py").exists()
    assert REQUIRED_MODES == ("saved", "live")
