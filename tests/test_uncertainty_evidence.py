from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from astrology_graph_foundry.ephemeris.uncertainty_evidence import (
    EVIDENCE_CONTRACT_VERSION,
    categorical_possibilities,
    circular_range_from_unwrapped,
    counterexamples,
    evidence_record,
    scalar_range,
    transition_witnesses,
)

SCHEMA = Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "schemas" / "bounded_uncertainty_evidence_v1.schema.json"
VECTORS = (
    Path(__file__).parents[1]
    / "docs"
    / "sprints"
    / "2026"
    / "08"
    / "20260811-coordinate-derived-bounded-natal-sprint1"
    / "results"
    / "uncertainty-evidence-vectors.json"
)


def test_scalar_range_requires_ordered_finite_bounds_and_contains_observations():
    result = scalar_range(-2, 5, unit="degrees", observed_low=-1, observed_high=4)
    assert result["observed"] == {"minimum": -1.0, "maximum": 4.0}
    with pytest.raises(ValueError, match="finite"):
        scalar_range(float("nan"), 1, unit="degrees")
    with pytest.raises(ValueError, match="inside"):
        scalar_range(0, 1, unit="degrees", observed_low=-1, observed_high=1)


def test_circular_ranges_preserve_wrap_disjoint_segments_and_full_circle():
    wrapped = circular_range_from_unwrapped(359, 361)
    assert wrapped["wraps_origin"] is True
    assert wrapped["segments"] == [
        {"minimum": 0.0, "maximum": 1.0},
        {"minimum": 359.0, "maximum": 360.0},
    ]
    quiet = circular_range_from_unwrapped(10, 12)
    assert quiet["segments"] == [{"minimum": 10.0, "maximum": 12.0}]
    full = circular_range_from_unwrapped(10, 370)
    assert full["coverage"] == "full_circle"


def test_possibilities_transitions_and_counterexamples_are_deterministic():
    assert categorical_possibilities(["Pisces", "Aries", "Pisces"])["values"] == ["Aries", "Pisces"]
    values = ["Pisces", "Pisces", "Aries", "Aries"]
    coordinates = [1.0, 2.0, 3.0, 4.0]
    assert transition_witnesses(values, coordinates, coordinate_unit="jd_ut") == [
        {"before": "Pisces", "after": "Aries", "interval": {"start": 2.0, "end": 3.0, "unit": "jd_ut"}}
    ]
    rows = counterexamples(values, coordinates, expected="Pisces", coordinate_unit="jd_ut")
    assert [row["coordinate"] for row in rows] == [3.0, 4.0]


def test_common_evidence_record_is_schema_valid_and_sorts_prerequisites():
    row = evidence_record(
        feature_key="body:Moon:sign",
        classification="variable",
        value_kind="zodiac_sign",
        possibilities=["Pisces", "Aries"],
        prerequisite_refs=["position:Moon", "provider:swisseph", "position:Moon"],
        range_evidence=circular_range_from_unwrapped(359, 361),
        transitions=[{"before": "Pisces", "after": "Aries"}],
        counterexample_rows=[{"expected": "Pisces", "observed": "Aries"}],
    )
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(row)
    assert row["evidence_contract_version"] == EVIDENCE_CONTRACT_VERSION
    assert row["prerequisite_refs"] == ["position:Moon", "provider:swisseph"]


def test_released_availability_schema_gap_is_reproduced_for_reconciliation():
    """Characterize the 0.8.0 producer/schema mismatch before changing policy."""

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    declared = {
        "available",
        "disabled_by_configuration",
        "unsupported_provider_field",
        "missing_provider_field",
        "nonfinite_provider_value",
        "provider_failure",
    }
    additional_producer_values = {
        "disabled",
        "unsupported_profile",
        "prerequisite_unavailable",
        "prerequisite_variable_or_unavailable",
    }

    def record(availability):
        return evidence_record(
            feature_key="audit:availability",
            classification="unavailable",
            value_kind="audit_value",
            availability=availability,
        )

    assert all(not list(validator.iter_errors(record(value))) for value in declared)
    assert all(list(validator.iter_errors(record(value))) for value in additional_producer_values)


def test_retained_uncertainty_vectors_match_implemented_range_contract():
    cases = {row["name"]: row for row in json.loads(VECTORS.read_text(encoding="utf-8"))["cases"]}
    wrapped = circular_range_from_unwrapped(359, 361)
    assert wrapped["segments"] == cases["circular_origin_wrap"]["segments"]
    assert wrapped["wraps_origin"] == cases["circular_origin_wrap"]["wraps_origin"]
    quiet = circular_range_from_unwrapped(10, 12)
    assert quiet["segments"] == cases["circular_quiet_segment"]["segments"]
    assert circular_range_from_unwrapped(10, 370)["coverage"] == cases["circular_full_coverage"]["coverage"]
