from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from jsonschema import Draft202012Validator

from astrology_graph_foundry.calculation_provenance import (
    CALCULATION_PROFILE_VERSION,
    CALCULATION_PROVENANCE_CONTRACT_VERSION,
    NORMALIZATION_POLICY_VERSION,
    build_calculation_provenance,
    normalize_source_input,
    sha256_json,
)
from astrology_graph_foundry.ephemeris.models import BirthData, ProviderConfig
from astrology_graph_foundry.ephemeris.providers import LiveSwissEphemerisProvider

SCHEMA_DIR = Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "schemas"
EVIDENCE_DIR = (
    Path(__file__).parents[1]
    / "docs"
    / "sprints"
    / "2026"
    / "08"
    / "20260805-release-engineering-sprint2"
    / "results"
)


def _birth(**overrides) -> BirthData:
    values = {
        "name": "Scout",
        "birth_local": "2020-05-17T14:30:00",
        "birth_timezone": "America/Denver",
        "birth_lat": 39.7392,
        "birth_lon": -104.9903,
        "birth_location_label": "Denver",
        "source_chart_id": "astrowoof:chart:scout",
    }
    values.update(overrides)
    return BirthData(**values)


def _runtime(**overrides):
    values = {
        "mode": "live_calculation",
        "provider": "swiss_ephemeris",
        "distribution": "pyswisseph",
        "distribution_version": "2.10.3.2",
        "library_version": "2.10.03",
        "calculation_flags": {
            "ecliptic_positions": ["FLG_SWIEPH", "FLG_SPEED"],
            "equatorial_declinations": ["FLG_SWIEPH", "FLG_SPEED", "FLG_EQUATORIAL"],
        },
        "ephemeris_data": {"status": "test_fixture", "inventory_sha256": "a" * 64},
    }
    values.update(overrides)
    return values


def _provenance(birth: BirthData | None = None, config: ProviderConfig | None = None, runtime=None):
    birth = birth or _birth()
    return build_calculation_provenance(
        birth_data=birth,
        natal_chart={},
        config=config or ProviderConfig(),
        provider_runtime=runtime or _runtime(),
    )


def test_normalized_input_excludes_descriptive_and_identity_fields():
    baseline, status = normalize_source_input(_birth(), {})
    renamed, renamed_status = normalize_source_input(
        _birth(name="Scout II", birth_location_label="Elsewhere", source_chart_id="other:chart"),
        {},
    )
    assert status == renamed_status == "complete_live_input"
    assert baseline == renamed
    assert sha256_json(baseline) == sha256_json(renamed)


def test_normalized_input_hash_changes_for_geometry():
    baseline = _provenance()["source_input"]["sha256"]
    assert _provenance(_birth(birth_local="2020-05-17T14:31:00"))["source_input"]["sha256"] != baseline
    assert _provenance(_birth(birth_lat=39.7393))["source_input"]["sha256"] != baseline
    assert _provenance(_birth(birth_lon=-104.9904))["source_input"]["sha256"] != baseline


def test_configuration_hash_changes_for_material_choices():
    baseline = _provenance()["configuration_sha256"]
    assert _provenance(config=ProviderConfig(house_system="W"))["configuration_sha256"] != baseline
    assert _provenance(config=ProviderConfig(include_minor=False))["configuration_sha256"] != baseline
    assert _provenance(runtime=_runtime(distribution_version="2.10.3.3"))["configuration_sha256"] != baseline


def test_provenance_versions_output_boundary_and_golden_hashes():
    provenance = _provenance()
    assert provenance["contract_version"] == CALCULATION_PROVENANCE_CONTRACT_VERSION
    assert provenance["calculation_basis_status"] == "complete_live_profile"
    assert provenance["calculation_profile_version"] == CALCULATION_PROFILE_VERSION
    assert provenance["normalization_policy_version"] == NORMALIZATION_POLICY_VERSION
    assert provenance["output_artifact_hash"]["owner"] == "orchestration"
    assert provenance["output_artifact_hash"]["status"] == "not_emitted_by_agf"
    assert provenance["source_input"]["sha256"] == "81fb2c383274d18c48d057009362312274cdb0a72c200425aebbe7e4f07aa0db"
    assert provenance["configuration_sha256"] == "eb9cb67167df00b529b88b1b678b2ec7708171b98573efa2605ffdfe06a8afad"


def test_cached_source_recovery_and_unavailable_source_are_explicit():
    recovered, status = normalize_source_input(
        None,
        {
            "birth_local": "2020-05-17T14:30:00",
            "birth_timezone": "America/Denver",
            "birth_lat": 39.7392,
            "birth_lon": -104.9903,
        },
    )
    assert recovered is not None
    assert status == "recovered_from_cached_chart"
    missing, status = normalize_source_input(None, {"birth_local": "2020-05-17T14:30:00"})
    assert missing is None
    assert status == "legacy_source_unavailable"
    cached = build_calculation_provenance(
        birth_data=None,
        natal_chart={
            "birth_local": "2020-05-17T14:30:00",
            "birth_timezone": "America/Denver",
            "birth_lat": 39.7392,
            "birth_lon": -104.9903,
        },
        config=ProviderConfig(),
        provider_runtime={"mode": "cached_replay", "provider": "cached_jsonl"},
    )
    assert cached["calculation_basis_status"] == "cached_replay_profile_not_original_calculation"


def test_provenance_matches_packaged_schema():
    schema = json.loads((SCHEMA_DIR / "calculation_provenance_v1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(_provenance())


def test_live_runtime_provenance_records_library_and_data_but_not_machine_path(monkeypatch, tmp_path):
    provider = LiveSwissEphemerisProvider.__new__(LiveSwissEphemerisProvider)
    provider.swe = SimpleNamespace(version="2.10.03")
    provider.config = ProviderConfig(ephe_path=str(tmp_path))
    (tmp_path / "sepl_18.se1").write_bytes(b"qualified ephemeris data")
    monkeypatch.setattr(
        "astrology_graph_foundry.ephemeris.providers.metadata.version",
        lambda name: "2.10.3.2" if name == "pyswisseph" else None,
    )
    runtime = provider.calculation_runtime_provenance()
    assert runtime["distribution_version"] == "2.10.3.2"
    assert runtime["library_version"] == "2.10.03"
    assert runtime["ephemeris_data"]["status"] == "inventoried"
    assert runtime["ephemeris_data"]["resource_count"] == 1
    assert runtime["ephemeris_data"]["resources"][0]["name"] == "sepl_18.se1"
    assert "ephe_path" not in json.dumps(runtime)
    assert str(tmp_path) not in json.dumps(runtime)


def test_retained_golden_vectors_and_examples_match_implementation():
    vectors = json.loads((EVIDENCE_DIR / "calculation-provenance-vectors.json").read_text(encoding="utf-8"))
    examples = json.loads((EVIDENCE_DIR / "calculation-provenance-examples.json").read_text(encoding="utf-8"))
    cases = {
        "display-and-identity-only": _provenance(
            _birth(name="Scout II", birth_location_label="Elsewhere", source_chart_id="other:chart")
        ),
        "birth-minute": _provenance(_birth(birth_local="2020-05-17T14:31:00")),
        "latitude": _provenance(_birth(birth_lat=39.7393)),
        "whole-sign-houses": _provenance(config=ProviderConfig(house_system="W")),
        "major-aspects-only": _provenance(config=ProviderConfig(include_minor=False)),
        "provider-version": _provenance(runtime=_runtime(distribution_version="2.10.3.3")),
    }
    baseline = _provenance()
    assert vectors["baseline"]["source_input_sha256"] == baseline["source_input"]["sha256"]
    assert vectors["baseline"]["configuration_sha256"] == baseline["configuration_sha256"]
    for vector in vectors["mutations"]:
        actual = cases[vector["name"]]
        assert vector["source_input_sha256"] == actual["source_input"]["sha256"]
        assert vector["configuration_sha256"] == actual["configuration_sha256"]
    schema = json.loads((SCHEMA_DIR / "calculation_provenance_v1.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    validator.validate(examples["live"])
    validator.validate(examples["cached_legacy"])
