from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from astrology_graph_foundry.common.identity import validate_source_chart_id
from astrology_graph_foundry.common.transitable_chart import descriptor_for_package
from astrology_graph_foundry.ephemeris.models import BirthData

SCHEMA_DIR = Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "schemas"


def _birth_data(**overrides):
    values = {
        "name": "Scout",
        "birth_local": "2020-05-01T12:30:00",
        "birth_timezone": "America/Denver",
        "birth_lat": 39.7392,
        "birth_lon": -104.9903,
    }
    values.update(overrides)
    return BirthData(**values)


@pytest.mark.parametrize(
    "value",
    [
        "natal:scout",
        "AstroWoof:dog:123e4567-e89b-12d3-a456-426614174000",
        "tenant/example.chart_1",
        "namespace:",
        "A",
        "a" * 200,
    ],
)
def test_source_chart_id_accepts_and_preserves_namespace_safe_values(value):
    assert validate_source_chart_id(value) == value
    assert _birth_data(source_chart_id=value).source_chart_id == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        " leading",
        "trailing ",
        "contains space",
        "ümlaut",
        "bad?#fragment",
        "a" * 201,
    ],
)
def test_source_chart_id_rejects_invalid_strings(value):
    with pytest.raises(ValueError, match="source_chart_id must be"):
        _birth_data(source_chart_id=value)


@pytest.mark.parametrize("value", [True, 42, b"natal:scout"])
def test_source_chart_id_rejects_non_strings(value):
    with pytest.raises(TypeError, match="source_chart_id must be a string"):
        _birth_data(source_chart_id=value)


def test_source_chart_id_is_optional_for_legacy_callers():
    assert _birth_data().source_chart_id is None


def test_birth_schema_accepts_explicit_identity_and_rejects_invalid_identity():
    schema = json.loads((SCHEMA_DIR / "birth_data_v1.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    valid = {
        "name": "Scout",
        "birth_local": "2020-05-01T12:30:00",
        "birth_timezone": "America/Denver",
        "birth_lat": 39.7392,
        "birth_lon": -104.9903,
        "source_chart_id": "astrowoof:dog:1234",
    }
    assert list(validator.iter_errors(valid)) == []
    assert list(validator.iter_errors({**valid, "source_chart_id": "bad identity"}))


def test_transitable_descriptor_uses_explicit_metadata_identity_without_slugging():
    source_chart_id = "AstroWoof:dog:ABC-123"
    package = {
        "metadata": {
            "analysis_type": "natal_dataset",
            "person": "Scout's Display Name",
            "source_chart_id": source_chart_id,
        },
        "natal": {
            "person": "Scout's Display Name",
            "bodies": {},
            "houses": {},
            "angles": {},
        },
    }

    descriptor = descriptor_for_package(package)

    assert descriptor["chart_identity"]["chart_id"] == source_chart_id
    assert descriptor["chart_identity"]["label"] == "Scout's Display Name"


def test_transitable_descriptor_rejects_conflicting_identity_carriers():
    package = {
        "metadata": {
            "analysis_type": "natal_dataset",
            "person": "Scout",
            "source_chart_id": "astrowoof:dog:A",
        },
        "natal": {
            "person": "Scout",
            "source_chart_id": "astrowoof:dog:B",
            "bodies": {},
            "houses": {},
            "angles": {},
        },
    }

    with pytest.raises(ValueError, match="Conflicting explicit source chart identities"):
        descriptor_for_package(package)


@pytest.mark.parametrize(
    ("command", "expected_flag"),
    [
        ([sys.executable, "-m", "astrology_graph_foundry.cli", "natal", "--help"], "--source-chart-id"),
        (
            [sys.executable, "-m", "astrology_graph_foundry.cli", "synastry", "--help"],
            "--person-a-source-chart-id",
        ),
        (
            [sys.executable, "-m", "astrology_graph_foundry.ephemeris.generate_daily_ephemeris", "--help"],
            "--source-chart-id",
        ),
    ],
)
def test_supported_cli_surfaces_expose_source_chart_identity(command, expected_flag):
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert expected_flag in completed.stdout


def test_live_pair_input_forwards_source_chart_identity(monkeypatch):
    from astrology_graph_foundry.pipelines import composite

    captured = {}

    def fake_build_natal(**kwargs):
        captured.update(kwargs)
        return {"metadata": {}, "natal": {}}

    monkeypatch.setattr(composite, "build_natal", fake_build_natal)
    composite._dataset_from_live(
        "person_a",
        {
            "person_a_provider": "live",
            "person_a_name": "Scout",
            "person_a_birth_local": "2020-05-01T12:30:00",
            "person_a_birth_timezone": "America/Denver",
            "person_a_birth_lat": 39.7392,
            "person_a_birth_lon": -104.9903,
            "person_a_source_chart_id": "astrowoof:dog:1234",
        },
    )

    assert captured["source_chart_id"] == "astrowoof:dog:1234"


def test_natal_live_build_accepts_and_serializes_explicit_identity(monkeypatch):
    from astrology_graph_foundry.pipelines import natal

    captured = {}
    source_chart_id = "astrowoof:dog:1234"
    graph = {
        "graph_type": "canonical_astrology_graph",
        "graph_version": "1.3.0",
        "source_sensor_id": "natal_chart",
        "projection_status": "pre_projection",
        "objects": [{"id": "natal:Sun", "object_type": "planet_or_point", "name": "Sun"}],
        "relationships": [],
    }

    class FakeProvider:
        def person_metadata(self):
            return {
                "person": "Scout",
                "provider": "fake_live",
                "target_chart_id": source_chart_id,
            }

        def natal_chart(self):
            return {
                "person": "Scout",
                "birth_local": "2020-05-01T12:30:00",
                "birth_timezone": "America/Denver",
                "birth_lat": 39.7392,
                "birth_lon": -104.9903,
                "bodies": {},
                "houses": {},
                "angles": {},
                "semantic_graph": graph,
            }

        def iter_days(self):
            return iter(())

    def fake_create_provider(_provider, **kwargs):
        captured.update(kwargs)
        return FakeProvider()

    monkeypatch.setattr(natal, "create_provider", fake_create_provider)
    result = natal.build(
        provider="live",
        name="Scout",
        birth_local="2020-05-01T12:30:00",
        birth_timezone="America/Denver",
        birth_lat=39.7392,
        birth_lon=-104.9903,
        source_chart_id=source_chart_id,
    )

    assert captured["birth_data"].source_chart_id == source_chart_id
    assert result["metadata"]["source_chart_id"] == source_chart_id
    assert result["transitable_chart"]["chart_identity"]["chart_id"] == source_chart_id
    assert result["canonical_astrology_graph"]["source_chart_id"] == source_chart_id
    provenance = result["metadata"]["calculation_provenance"]
    assert provenance["source_input"]["completeness"] == "complete_live_input"
    assert provenance["source_input"]["sha256"]
    assert provenance["configuration_sha256"]
    assert provenance["calculation_profile"]["provider"]["provider"] == "fake_live"
    assert source_chart_id not in json.dumps(provenance, sort_keys=True)
