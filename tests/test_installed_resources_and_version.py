from __future__ import annotations

import hashlib
import json
import sys
from importlib import metadata
from pathlib import Path

import pytest

from astrology_graph_foundry import __version__
from astrology_graph_foundry.cli import cli_entry as primary_cli_entry
from astrology_graph_foundry.cli import main as cli_main
from astrology_graph_foundry.ephemeris.generate_daily_ephemeris import cli_entry as ephemeris_cli_entry
from astrology_graph_foundry.ephemeris.generate_daily_ephemeris import main as ephemeris_main
from astrology_graph_foundry.resources import (
    RUNTIME_PACKAGE_MANIFEST_TYPE,
    build_runtime_package_manifest,
    read_schema,
    read_schema_bytes,
    schema_names,
)


def test_project_metadata_uses_runtime_version_as_single_source():
    pyproject = (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    assert 'dynamic = ["version"]' in pyproject
    assert 'version = {attr = "astrology_graph_foundry._version.__version__"}' in pyproject
    assert 'version = "0.6.0"' not in pyproject


def test_installed_distribution_and_runtime_versions_agree():
    assert metadata.version("astrology-graph-foundry") == __version__


def test_packaged_schema_api_is_complete_and_rejects_unknown_names():
    names = schema_names()
    assert len(names) == 33
    assert names == tuple(sorted(names))
    assert "birth_data_v1.schema.json" in names
    assert "canonical_astrology_graph_v1.schema.json" in names
    assert read_schema("canonical_astrology_graph_v1.schema.json")["title"]
    with pytest.raises(FileNotFoundError, match="Unknown packaged schema"):
        read_schema("missing.schema.json")


def test_runtime_package_manifest_matches_packaged_bytes():
    manifest = build_runtime_package_manifest()
    assert manifest["manifest_type"] == RUNTIME_PACKAGE_MANIFEST_TYPE
    assert manifest["package_version"] == __version__
    assert manifest["resource_count"] == 33
    paths = [resource["path"] for resource in manifest["resources"]]
    assert paths == sorted(paths)
    for resource in manifest["resources"]:
        name = resource["path"].rsplit("/", 1)[-1]
        content = read_schema_bytes(name)
        assert resource["size_bytes"] == len(content)
        assert resource["sha256"] == hashlib.sha256(content).hexdigest()
        json.loads(content)


def test_primary_cli_exposes_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["astro-package", "--version"])
    with pytest.raises(SystemExit) as exc:
        cli_main()
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"astro-package {__version__}"


def test_ephemeris_cli_exposes_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["generate-daily-ephemeris", "--version"])
    with pytest.raises(SystemExit) as exc:
        ephemeris_main()
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"generate-daily-ephemeris {__version__}"


def test_primary_cli_emits_runtime_manifest(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["astro-package", "runtime-manifest"])
    cli_main()
    manifest = json.loads(capsys.readouterr().out)
    assert manifest["package_version"] == __version__
    assert manifest["resource_count"] == 33


def test_console_entries_render_optional_dependency_failures(monkeypatch):
    def missing_dependency():
        raise ImportError("missing optional dependency")

    monkeypatch.setattr("astrology_graph_foundry.cli.main", missing_dependency)
    with pytest.raises(SystemExit, match="ERROR: missing optional dependency"):
        primary_cli_entry()

    monkeypatch.setattr(
        "astrology_graph_foundry.ephemeris.generate_daily_ephemeris.main",
        missing_dependency,
    )
    with pytest.raises(SystemExit, match="ERROR: missing optional dependency"):
        ephemeris_cli_entry()
