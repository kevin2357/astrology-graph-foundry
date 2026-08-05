from __future__ import annotations

import json
import sys

import pytest

from astrology_graph_foundry import cli


def _report(*, ready: bool) -> dict:
    return {
        "foundry": {"version_metadata_matches_runtime": ready},
        "runtime_resources": {"resource_count": 34},
        "semantic_projection_core": {
            "available": True,
            "version_metadata_matches_engine": True,
            "compatible_with_foundry": True,
        },
        "swiss_ephemeris": {"available": True},
    }


def test_doctor_cli_required_mode_success(monkeypatch, capsys):
    monkeypatch.setattr(cli, "build_doctor_report", lambda: _report(ready=True))
    monkeypatch.setattr(sys, "argv", ["astro-package", "doctor", "--require-mode", "projection", "--json"])
    cli.main()
    output = json.loads(capsys.readouterr().out)
    assert output["required_mode_assertion"] == {
        "failure_codes": [],
        "mode": "projection",
        "ready": True,
    }


def test_doctor_cli_required_mode_failure_exits_two(monkeypatch, capsys):
    monkeypatch.setattr(cli, "build_doctor_report", lambda: _report(ready=False))
    monkeypatch.setattr(sys, "argv", ["astro-package", "doctor", "--require-mode", "saved", "--json"])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
    output = json.loads(capsys.readouterr().out)
    assert output["required_mode_assertion"]["failure_codes"] == ["foundry_version_mismatch"]
