from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from astrology_graph_foundry.calculation_provenance import (
    BOUNDED_NORMALIZATION_POLICY_VERSION,
    build_bounded_source_input_provenance,
)
from astrology_graph_foundry.ephemeris.models import (
    BirthTimeBasis,
    BoundedBirthData,
    normalize_birth_time_basis,
)
from astrology_graph_foundry.pipelines import natal

SCHEMA_DIR = Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "schemas"
EVIDENCE_DIR = (
    Path(__file__).parents[1]
    / "docs"
    / "sprints"
    / "2026"
    / "08"
    / "20260809-bounded-birth-time-natal-sprint1"
    / "results"
)


def _bounded(**overrides) -> BoundedBirthData:
    values = {
        "name": "Scout",
        "birth_time_basis": BirthTimeBasis(
            mode="bounded",
            earliest_local="2020-05-17T08:00:00",
            latest_local="2020-05-17T14:00:00",
        ),
        "birth_timezone": "America/Denver",
        "birth_lat": 39.7392,
        "birth_lon": -104.9903,
        "birth_location_label": "Denver",
        "source_chart_id": "astrowoof:chart:scout",
    }
    values.update(overrides)
    return BoundedBirthData(**values)


def test_bounded_schema_is_separate_and_accepts_bounded_and_unknown_time():
    exact_schema = json.loads((SCHEMA_DIR / "birth_data_v1.schema.json").read_text(encoding="utf-8"))
    bounded_schema = json.loads((SCHEMA_DIR / "bounded_birth_data_v1.schema.json").read_text(encoding="utf-8"))
    exact_required = exact_schema["required"]
    assert "birth_local" in exact_required
    assert "birth_time_basis" not in exact_schema["properties"]

    validator = Draft202012Validator(bounded_schema, format_checker=FormatChecker())
    common = {
        "name": "Scout",
        "birth_timezone": "America/Denver",
        "birth_lat": 39.7392,
        "birth_lon": -104.9903,
    }
    validator.validate(
        {
            **common,
            "birth_time_basis": {
                "mode": "bounded",
                "earliest_local": "2020-05-17T08:00:00",
                "latest_local": "2020-05-17T14:00:00",
            },
        }
    )
    validator.validate({**common, "birth_time_basis": {"mode": "unknown_time", "birth_date": "2020-05-17"}})
    assert list(validator.iter_errors({**common, "birth_time_basis": {"mode": "exact"}}))


def test_bounded_normalization_and_resolved_utc_validation():
    birth = _bounded(
        birth_time_basis=BirthTimeBasis(
            mode="bounded",
            earliest_local="2020-05-17T08:00:00",
            latest_local="2020-05-17T14:00:00",
            earliest_utc="2020-05-17T14:00:00Z",
            latest_utc="2020-05-17T20:00:00+00:00",
        )
    )
    normalized = birth.resolved_birth_time_basis
    assert normalized is not None
    assert normalized.mode == "bounded"
    assert normalized.duration_hours == 6
    assert normalized.boundary_policy == "inclusive"
    assert normalized.start_utc == "2020-05-17T14:00:00+00:00"

    with pytest.raises(ValueError, match="does not match"):
        _bounded(
            birth_time_basis=BirthTimeBasis(
                mode="bounded",
                earliest_local="2020-05-17T08:00:00",
                latest_local="2020-05-17T14:00:00",
                earliest_utc="2020-05-17T15:00:00Z",
            )
        )


@pytest.mark.parametrize(
    ("birth_date", "expected_hours"),
    [("2024-03-10", 23), ("2024-11-03", 25)],
)
def test_unknown_time_uses_complete_local_calendar_day_across_dst(birth_date, expected_hours):
    normalized = normalize_birth_time_basis(
        BirthTimeBasis(mode="unknown_time", birth_date=birth_date),
        "America/New_York",
    )
    assert normalized.duration_hours == expected_hours
    assert normalized.boundary_policy == "local_date_start_inclusive_next_date_start_exclusive"


def test_cross_midnight_range_is_normalized_by_elapsed_utc_time():
    normalized = normalize_birth_time_basis(
        BirthTimeBasis(
            mode="bounded",
            earliest_local="2024-05-01T22:00:00",
            latest_local="2024-05-02T02:00:00",
        ),
        "America/Denver",
    )
    assert normalized.duration_hours == 4


@pytest.mark.parametrize(
    ("basis", "message"),
    [
        (
            BirthTimeBasis(mode="bounded", earliest_local="2024-03-10T02:30:00", latest_local="2024-03-10T04:00:00"),
            "nonexistent",
        ),
        (
            BirthTimeBasis(mode="bounded", earliest_local="2024-11-03T01:30:00", latest_local="2024-11-03T03:00:00"),
            "ambiguous",
        ),
        (
            BirthTimeBasis(mode="bounded", earliest_local="2024-05-02T02:00:00", latest_local="2024-05-01T22:00:00"),
            "positive duration",
        ),
        (
            BirthTimeBasis(mode="bounded", earliest_local="2024-05-01T22:00:00", latest_local="2024-05-01T22:00:00"),
            "use exact mode",
        ),
        (
            BirthTimeBasis(mode="bounded", earliest_local="2024-05-01T00:00:00", latest_local="2024-05-04T00:00:00"),
            "48 elapsed UTC hours",
        ),
    ],
)
def test_invalid_or_unsupported_bounds_fail_closed(basis, message):
    with pytest.raises(ValueError, match=message):
        normalize_birth_time_basis(basis, "America/New_York")


def test_exact_tagged_normalization_exists_without_changing_exact_schema():
    normalized = normalize_birth_time_basis(
        BirthTimeBasis(mode="exact", birth_local="2020-05-17T14:30:00"),
        "America/Denver",
    )
    assert normalized.mode == "exact"
    assert normalized.duration_hours == 0
    assert normalized.boundary_policy == "point"


def test_bounded_source_hash_changes_for_basis_but_excludes_description_and_identity():
    baseline = build_bounded_source_input_provenance(_bounded())
    renamed = build_bounded_source_input_provenance(
        _bounded(name="Scout II", birth_location_label="Elsewhere", source_chart_id="other:chart")
    )
    shifted = build_bounded_source_input_provenance(
        _bounded(
            birth_time_basis=BirthTimeBasis(
                mode="bounded",
                earliest_local="2020-05-17T08:01:00",
                latest_local="2020-05-17T14:00:00",
            )
        )
    )
    unknown = build_bounded_source_input_provenance(
        _bounded(birth_time_basis=BirthTimeBasis(mode="unknown_time", birth_date="2020-05-17"))
    )
    assert baseline["normalization_policy_version"] == BOUNDED_NORMALIZATION_POLICY_VERSION
    assert baseline["sha256"] == renamed["sha256"]
    assert baseline["sha256"] != shifted["sha256"]
    assert baseline["sha256"] != unknown["sha256"]


def test_retained_bounded_normalization_vectors_match_implementation():
    vectors = json.loads((EVIDENCE_DIR / "bounded-input-normalization-vectors.json").read_text(encoding="utf-8"))
    cases = {
        "bounded": _bounded(),
        "unknown_time_dst_short": _bounded(
            birth_time_basis=BirthTimeBasis(mode="unknown_time", birth_date="2024-03-10"),
            birth_timezone="America/New_York",
            birth_lat=40.7128,
            birth_lon=-74.006,
        ),
        "unknown_time_dst_long": _bounded(
            birth_time_basis=BirthTimeBasis(mode="unknown_time", birth_date="2024-11-03"),
            birth_timezone="America/New_York",
            birth_lat=40.7128,
            birth_lon=-74.006,
        ),
    }
    for name, birth in cases.items():
        provenance = build_bounded_source_input_provenance(birth)
        expected = vectors["cases"][name]
        normalized = provenance["values"]["birth_time_basis"]["normalized"]
        assert provenance["sha256"] == expected["source_input_sha256"]
        assert normalized["start_utc"] == expected["start_utc"]
        assert normalized["end_utc"] == expected["end_utc"]
        assert normalized["duration_hours"] == expected["duration_hours"]


def test_bounded_coordinates_and_exact_mode_are_rejected_by_bounded_model():
    with pytest.raises(ValueError, match="birth_lat"):
        _bounded(birth_lat=91)
    with pytest.raises(ValueError, match="birth_lon"):
        _bounded(birth_lon=181)
    with pytest.raises(ValueError, match="birth_lat"):
        _bounded(birth_lat=float("nan"))
    with pytest.raises(ValueError, match="name"):
        _bounded(name=" ")
    with pytest.raises(ValueError, match="use BirthData"):
        _bounded(birth_time_basis=BirthTimeBasis(mode="exact", birth_local="2020-05-17T12:00:00"))


def test_natal_cli_exposes_only_natal_bounded_flags():
    natal_help = subprocess.run(
        [sys.executable, "-m", "astrology_graph_foundry.cli", "natal", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    transit_help = subprocess.run(
        [sys.executable, "-m", "astrology_graph_foundry.cli", "transit", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert natal_help.returncode == 0
    assert "--birth-local-earliest" in natal_help.stdout
    assert "--birth-time-unknown" in natal_help.stdout
    assert "--birth-local-earliest" not in transit_help.stdout


def test_natal_boundary_rejects_conflicts_and_routes_bounded_calculation(monkeypatch):
    common = {
        "provider": "live",
        "name": "Scout",
        "birth_timezone": "America/Denver",
        "birth_lat": 39.7392,
        "birth_lon": -104.9903,
    }
    with pytest.raises(ValueError, match="cannot be combined"):
        natal.build(
            **common,
            birth_local="2020-05-17T12:00:00",
            birth_local_earliest="2020-05-17T08:00:00",
            birth_local_latest="2020-05-17T14:00:00",
        )
    sentinel = {"bounded": True}
    monkeypatch.setattr(natal, "build_bounded_natal_package", lambda birth, config: sentinel)
    assert natal.build(
        **common,
        birth_local_earliest="2020-05-17T08:00:00",
        birth_local_latest="2020-05-17T14:00:00",
    ) is sentinel
