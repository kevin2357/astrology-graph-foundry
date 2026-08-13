from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Any, Literal

EVIDENCE_CONTRACT_VERSION = "agf.bounded_uncertainty_evidence.v1.0.0"
EvidenceClassification = Literal["invariant", "conditional", "variable", "unavailable", "inconclusive"]
EvidenceAvailability = Literal[
    "available",
    "disabled",
    "disabled_by_configuration",
    "missing_provider_field",
    "nonfinite_provider_value",
    "prerequisite_unavailable",
    "prerequisite_variable_or_unavailable",
    "provider_failure",
    "unsupported_profile",
    "unsupported_provider_field",
]

CANONICAL_AVAILABILITY_VALUES = frozenset(
    {
        "available",
        "disabled",
        "missing_provider_field",
        "nonfinite_provider_value",
        "prerequisite_unavailable",
        "prerequisite_variable_or_unavailable",
        "provider_failure",
        "unsupported_profile",
    }
)
COMPATIBILITY_AVAILABILITY_ALIASES = frozenset(
    {
        "disabled_by_configuration",
        "unsupported_provider_field",
    }
)
SUPPORTED_AVAILABILITY_VALUES = CANONICAL_AVAILABILITY_VALUES | COMPATIBILITY_AVAILABILITY_ALIASES


def scalar_range(
    low: float,
    high: float,
    *,
    unit: str,
    observed_low: float | None = None,
    observed_high: float | None = None,
) -> dict[str, Any]:
    """Return a deterministic closed scalar range with optional observed bounds."""

    low, high = float(low), float(high)
    if not (math.isfinite(low) and math.isfinite(high)):
        raise ValueError("scalar range bounds must be finite")
    if high < low:
        raise ValueError("scalar range high must be greater than or equal to low")
    result: dict[str, Any] = {
        "range_type": "scalar_closed",
        "unit": unit,
        "minimum": low,
        "maximum": high,
    }
    if observed_low is not None or observed_high is not None:
        if observed_low is None or observed_high is None:
            raise ValueError("observed scalar bounds must be supplied together")
        observed_low, observed_high = float(observed_low), float(observed_high)
        if not (low <= observed_low <= observed_high <= high):
            raise ValueError("observed scalar bounds must lie inside the proof range")
        result["observed"] = {"minimum": observed_low, "maximum": observed_high}
    return result


def circular_range_from_unwrapped(
    low: float,
    high: float,
    *,
    period: float = 360.0,
    unit: str = "degrees",
) -> dict[str, Any]:
    """Represent one unwrapped envelope as deterministic circular segments."""

    low, high, period = float(low), float(high), float(period)
    if not all(math.isfinite(value) for value in (low, high, period)):
        raise ValueError("circular range values must be finite")
    if period <= 0 or high < low:
        raise ValueError("circular range requires a positive period and ordered bounds")
    width = high - low
    if width >= period:
        segments = [{"minimum": 0.0, "maximum": period}]
        coverage = "full_circle"
        wraps = True
    else:
        start = low % period
        end = start + width
        if end <= period:
            segments = [{"minimum": start, "maximum": end}]
            wraps = False
        else:
            segments = [
                {"minimum": 0.0, "maximum": end - period},
                {"minimum": start, "maximum": period},
            ]
            wraps = True
        segments.sort(key=lambda row: (row["minimum"], row["maximum"]))
        coverage = "partial"
    return {
        "range_type": "circular_closed_segments",
        "unit": unit,
        "period": period,
        "coverage": coverage,
        "wraps_origin": wraps,
        "segments": segments,
        "unwrapped_envelope": {"minimum": low, "maximum": high},
    }


def categorical_possibilities(values: Iterable[Any]) -> dict[str, Any]:
    """Return stable unique categorical possibilities without sampling weights."""

    unique = {str(value) for value in values if value is not None}
    return {
        "possibility_type": "categorical_set",
        "values": sorted(unique),
        "count": len(unique),
    }


def transition_witnesses(
    values: list[Any],
    coordinates: list[float],
    *,
    coordinate_unit: str,
) -> list[dict[str, Any]]:
    """Record adjacent sampled states whose normalized categorical value changes."""

    if len(values) != len(coordinates):
        raise ValueError("transition values and coordinates must have equal length")
    witnesses = []
    for index in range(len(values) - 1):
        before, after = values[index], values[index + 1]
        if before == after:
            continue
        witnesses.append(
            {
                "before": str(before) if before is not None else None,
                "after": str(after) if after is not None else None,
                "interval": {
                    "start": float(coordinates[index]),
                    "end": float(coordinates[index + 1]),
                    "unit": coordinate_unit,
                },
            }
        )
    return witnesses


def counterexamples(
    values: list[Any],
    coordinates: list[float],
    *,
    expected: Any,
    coordinate_unit: str,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Retain compact witnesses showing why one proposed invariant was withheld."""

    if len(values) != len(coordinates):
        raise ValueError("counterexample values and coordinates must have equal length")
    rows = []
    for value, coordinate in zip(values, coordinates):
        if value == expected:
            continue
        rows.append(
            {
                "expected": str(expected) if expected is not None else None,
                "observed": str(value) if value is not None else None,
                "coordinate": float(coordinate),
                "coordinate_unit": coordinate_unit,
            }
        )
        if len(rows) >= limit:
            break
    return rows


def evidence_record(
    *,
    feature_key: str,
    classification: EvidenceClassification,
    value_kind: str,
    possibilities: Iterable[Any] = (),
    prerequisite_refs: Iterable[str] = (),
    range_evidence: Mapping[str, Any] | None = None,
    transitions: Iterable[Mapping[str, Any]] = (),
    counterexample_rows: Iterable[Mapping[str, Any]] = (),
    proof_scope: str = "complete_normalized_birth_interval",
    availability: EvidenceAvailability | None = None,
    status_reason: str | None = None,
) -> dict[str, Any]:
    """Build the common additive evidence envelope used by bounded feature rows."""

    record = {
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "feature_key": feature_key,
        "classification": classification,
        "value_kind": value_kind,
        "possibilities": categorical_possibilities(possibilities),
        "prerequisite_refs": sorted({str(value) for value in prerequisite_refs}),
        "range_evidence": dict(range_evidence) if range_evidence is not None else None,
        "transition_witnesses": [dict(row) for row in transitions],
        "counterexamples": [dict(row) for row in counterexample_rows],
        "proof_scope": proof_scope,
    }
    if availability is not None:
        if availability not in SUPPORTED_AVAILABILITY_VALUES:
            raise ValueError(f"unsupported bounded evidence availability: {availability}")
        record["availability"] = availability
    if status_reason is not None:
        record["status_reason"] = status_reason
    return record
