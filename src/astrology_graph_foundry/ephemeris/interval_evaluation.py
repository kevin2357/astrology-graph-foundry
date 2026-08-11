from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from typing import Any, Literal

from astrology_graph_foundry.common.aspects import orb_allowed
from astrology_graph_foundry.common.constants import (
    ASPECTS,
    MAJOR_ASPECTS,
    SIGN_RULERS_MODERN,
    SIGN_RULERS_TRADITIONAL,
)
from astrology_graph_foundry.ephemeris.uncertainty_evidence import (
    EVIDENCE_CONTRACT_VERSION,
    EvidenceClassification,
    circular_range_from_unwrapped,
    counterexamples,
    evidence_record,
    scalar_range,
    transition_witnesses,
)

Classification = Literal["invariant", "conditional", "variable", "inconclusive"]
PositionEvaluator = Callable[[float], Mapping[str, Mapping[str, float | bool | None]]]
SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
EXALTATIONS = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mercury": "Virgo",
    "Venus": "Pisces",
    "Mars": "Capricorn",
    "Jupiter": "Cancer",
    "Saturn": "Libra",
}


@dataclass(frozen=True)
class IntervalProofProfile:
    version: str = "agf.interval_proof.v1.0.0"
    initial_step_seconds: float = 3600.0
    minimum_step_seconds: float = 60.0
    longitude_tolerance_degrees: float = 1e-7
    speed_zero_tolerance_degrees_per_day: float = 1e-7
    speed_envelope_factor: float = 1.25
    maximum_evaluations: int = 5000


def _unwrap(value: float, reference: float) -> float:
    return reference + ((value - reference + 180.0) % 360.0 - 180.0)


def _signs_for_range(low: float, high: float, tolerance: float) -> list[int]:
    first = math.floor((low + tolerance) / 30.0)
    last = math.floor((high - tolerance) / 30.0)
    return sorted({index % 12 for index in range(first, last + 1)})


def _motion_states(low: float, high: float, tolerance: float) -> list[str]:
    states = []
    if high > tolerance:
        states.append("direct")
    if low < -tolerance:
        states.append("retrograde")
    if low <= tolerance and high >= -tolerance:
        states.append("stationary")
    return states


def _sample_motion_state(speed: float, tolerance: float) -> str:
    if speed > tolerance:
        return "direct"
    if speed < -tolerance:
        return "retrograde"
    return "stationary"


def _scalar_envelope(
    values: list[float],
    speeds: list[float],
    times: list[float],
    factor: float,
) -> tuple[float, float]:
    padding = [
        max(abs(speeds[index]), abs(speeds[index + 1]))
        * (times[index + 1] - times[index])
        * factor
        for index in range(len(times) - 1)
    ]
    return (
        min(values[index] - (padding[index - 1] if index else padding[0]) for index in range(len(values))),
        max(values[index] + (padding[index - 1] if index else padding[0]) for index in range(len(values))),
    )


def _coordinate_evidence(
    *,
    name: str,
    samples: Mapping[float, Mapping[str, Mapping[str, float | bool | None]]],
    times: list[float],
    value_key: str,
    speed_key: str,
    value_kind: str,
    unit: str,
    factor: float,
    circular: bool = False,
) -> dict[str, Any]:
    values: list[float] = []
    speeds: list[float] = []
    for time in times:
        row = samples[time].get(name) or {}
        value, speed = row.get(value_key), row.get(speed_key)
        if value is None or speed is None:
            availability = str(
                row.get(f"{value_key}_availability")
                or row.get(f"{speed_key}_availability")
                or "missing_provider_field"
            )
            return evidence_record(
                feature_key=f"body:{name}:{value_key}",
                classification="inconclusive",
                value_kind=value_kind,
                prerequisite_refs=[f"provider_position:{name}"],
                availability=availability,
                status_reason=str(
                    row.get(f"{value_key}_status_reason")
                    or row.get(f"{speed_key}_status_reason")
                    or f"provider did not return {value_key} and {speed_key} at every evaluation"
                ),
            )
        value, speed = float(value), float(speed)
        if not math.isfinite(value) or not math.isfinite(speed):
            return evidence_record(
                feature_key=f"body:{name}:{value_key}",
                classification="inconclusive",
                value_kind=value_kind,
                prerequisite_refs=[f"provider_position:{name}"],
                availability="nonfinite_provider_value",
                status_reason=f"provider returned non-finite {value_key} or {speed_key}",
            )
        values.append(value % 360.0 if circular else value)
        speeds.append(speed)
    proof_values = [values[0]]
    if circular:
        for value in values[1:]:
            proof_values.append(_unwrap(value, proof_values[-1]))
    else:
        proof_values = values
    low, high = _scalar_envelope(proof_values, speeds, times, factor)
    range_evidence = (
        circular_range_from_unwrapped(low, high, unit=unit)
        if circular
        else scalar_range(low, high, unit=unit, observed_low=min(values), observed_high=max(values))
    )
    return evidence_record(
        feature_key=f"body:{name}:{value_key}",
        classification="invariant" if high == low else "variable",
        value_kind=value_kind,
        prerequisite_refs=[f"provider_position:{name}", f"provider_speed:{name}:{speed_key}"],
        range_evidence=range_evidence,
        availability="available",
    )


def _speed_evidence(
    *,
    name: str,
    samples: Mapping[float, Mapping[str, Mapping[str, float | bool | None]]],
    times: list[float],
    speed_key: str,
    value_kind: str,
    factor: float,
) -> dict[str, Any]:
    speeds = []
    for time in times:
        row = samples[time].get(name) or {}
        speed = row.get(speed_key)
        if speed is None:
            availability = str(row.get(f"{speed_key}_availability") or "missing_provider_field")
            return evidence_record(
                feature_key=f"body:{name}:{speed_key}",
                classification="inconclusive",
                value_kind=value_kind,
                prerequisite_refs=[f"provider_speed:{name}:{speed_key}"],
                availability=availability,
                status_reason=str(
                    row.get(f"{speed_key}_status_reason")
                    or f"provider did not return {speed_key} at every evaluation"
                ),
            )
        speed = float(speed)
        if not math.isfinite(speed):
            return evidence_record(
                feature_key=f"body:{name}:{speed_key}",
                classification="inconclusive",
                value_kind=value_kind,
                prerequisite_refs=[f"provider_speed:{name}:{speed_key}"],
                availability="nonfinite_provider_value",
                status_reason=f"provider returned non-finite {speed_key}",
            )
        speeds.append(speed)
    padding = max(
        (abs(speeds[index + 1] - speeds[index]) * factor for index in range(len(speeds) - 1)),
        default=0.0,
    )
    low, high = min(speeds) - padding, max(speeds) + padding
    return evidence_record(
        feature_key=f"body:{name}:{speed_key}",
        classification="invariant" if high == low else "variable",
        value_kind=value_kind,
        prerequisite_refs=[f"provider_speed:{name}:{speed_key}"],
        range_evidence=scalar_range(
            low,
            high,
            unit="degrees_per_day",
            observed_low=min(speeds),
            observed_high=max(speeds),
        ),
        availability="available",
    )
def _distance(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _aspect_at(a: str, lon_a: float, b: str, lon_b: float, include_minor: bool) -> str | None:
    distance = _distance(lon_a, lon_b)
    candidates = []
    for name, angle in ASPECTS.items():
        if not include_minor and name not in MAJOR_ASPECTS:
            continue
        orb = abs(distance - angle)
        if orb <= orb_allowed(a, b, name):
            candidates.append((orb, name))
    return min(candidates)[1] if candidates else None


def evaluate_interval(
    start_jd: float,
    end_jd: float,
    body_ids: Mapping[str, int],
    evaluator: PositionEvaluator,
    *,
    include_minor: bool = True,
    profile: IntervalProofProfile | None = None,
) -> dict[str, Any]:
    """Conservatively classify body and aspect facts over a Julian-day interval.

    The evaluator is provider-independent. Each returned body must expose ``lon`` and
    ``speed_lon``. Sampling alone is never called proof: every segment is enlarged by
    a speed-based envelope, and missing/non-finite data or exhausted budgets fail
    closed as inconclusive.
    """
    profile = profile or IntervalProofProfile()
    if not end_jd > start_jd:
        raise ValueError("interval end_jd must be greater than start_jd")
    # v1 refines the entire initial grid to the minimum step. This is deliberately
    # more conservative than feature-triggered refinement and gives every segment
    # the same documented upper bound; later profiles may prune quiet segments.
    step_days = profile.minimum_step_seconds / 86400.0
    count = max(1, math.ceil((end_jd - start_jd) / step_days))
    times = [start_jd + (end_jd - start_jd) * index / count for index in range(count + 1)]
    if len(times) > profile.maximum_evaluations:
        return _inconclusive_result(body_ids, profile, "initial evaluation budget exceeded")
    try:
        samples = {time: evaluator(time) for time in times}
    except Exception as exc:  # noqa: BLE001 - provider failures are evidence, not crashes
        return _inconclusive_result(body_ids, profile, f"provider failure: {exc}")

    failures = []
    bodies: dict[str, Any] = {}
    unwrapped: dict[str, list[float]] = {}
    for name in body_ids:
        values = []
        speeds = []
        valid = True
        for time in times:
            row = samples[time].get(name)
            if row is None or row.get("lon") is None or row.get("speed_lon") is None:
                valid = False
                break
            lon, speed = float(row["lon"]), float(row["speed_lon"])
            if not math.isfinite(lon) or not math.isfinite(speed):
                valid = False
                break
            values.append(lon % 360.0)
            speeds.append(speed)
        if not valid:
            failures.append({"body": name, "reason": "missing_or_nonfinite_position"})
            bodies[name] = {"classification": "inconclusive", "reason": "provider data incomplete"}
            continue
        path = [values[0]]
        for value in values[1:]:
            path.append(_unwrap(value, path[-1]))
        unwrapped[name] = path
        low, high = _scalar_envelope(path, speeds, times, profile.speed_envelope_factor)
        signs = _signs_for_range(low, high, profile.longitude_tolerance_degrees)
        speed_padding = max(
            (abs(speeds[index + 1] - speeds[index]) * profile.speed_envelope_factor for index in range(len(speeds) - 1)),
            default=0.0,
        )
        speed_low, speed_high = min(speeds) - speed_padding, max(speeds) + speed_padding
        motions = _motion_states(speed_low, speed_high, profile.speed_zero_tolerance_degrees_per_day)
        sign_values = [SIGNS[int(value // 30) % 12] for value in values]
        motion_values = [_sample_motion_state(value, profile.speed_zero_tolerance_degrees_per_day) for value in speeds]
        sign_classification: EvidenceClassification = "invariant" if len(signs) == 1 else "variable"
        motion_classification: EvidenceClassification = "invariant" if len(motions) == 1 else "variable"
        sign_dignity = None
        if len(signs) == 1:
            sign = SIGNS[signs[0]]
            opposite = SIGNS[(signs[0] + 6) % 12]
            sign_dignity = {
                "classification": "invariant",
                "sign": sign,
                "domicile_traditional": SIGN_RULERS_TRADITIONAL.get(sign) == name,
                "domicile_modern": SIGN_RULERS_MODERN.get(sign) == name,
                "exaltation": EXALTATIONS.get(name) == sign,
                "detriment_traditional": SIGN_RULERS_TRADITIONAL.get(opposite) == name,
                "fall": EXALTATIONS.get(name) == opposite,
                "sect_dependent_components": "unavailable",
            }
        dignity_components = []
        if sign_dignity is not None:
            dignity_components = [
                f"{key}={str(sign_dignity[key]).lower()}"
                for key in ("domicile_traditional", "domicile_modern", "exaltation", "detriment_traditional", "fall")
            ]
        bodies[name] = {
            "classification": "invariant" if len(signs) == 1 and len(motions) == 1 else "variable",
            "longitude_range": {"unwrapped_min": low, "unwrapped_max": high, "possible_sign_indexes": signs},
            "motion": {
                "classification": "invariant" if len(motions) == 1 else "variable",
                "possible_states": motions,
                "speed_min": speed_low,
                "speed_max": speed_high,
            },
            "sign_dignity": sign_dignity,
            "sample_count": len(times),
            "evidence": {
                "longitude": evidence_record(
                    feature_key=f"body:{name}:longitude",
                    classification=(
                        "invariant"
                        if high - low <= profile.longitude_tolerance_degrees
                        else "variable"
                    ),
                    value_kind="ecliptic_longitude_range",
                    prerequisite_refs=[f"provider_position:{name}"],
                    range_evidence=circular_range_from_unwrapped(low, high),
                ),
                "sign": evidence_record(
                    feature_key=f"body:{name}:sign",
                    classification=sign_classification,
                    value_kind="zodiac_sign",
                    possibilities=(SIGNS[index] for index in signs),
                    prerequisite_refs=[f"body:{name}:longitude"],
                    transitions=transition_witnesses(sign_values, times, coordinate_unit="jd_ut"),
                    counterexample_rows=(
                        counterexamples(
                            sign_values,
                            times,
                            expected=sign_values[0],
                            coordinate_unit="jd_ut",
                        )
                        if sign_values
                        else []
                    ),
                ),
                "motion": evidence_record(
                    feature_key=f"body:{name}:motion",
                    classification=motion_classification,
                    value_kind="longitudinal_motion_state",
                    possibilities=motions,
                    prerequisite_refs=[f"provider_speed:{name}"],
                    range_evidence=scalar_range(speed_low, speed_high, unit="degrees_per_day"),
                    transitions=transition_witnesses(motion_values, times, coordinate_unit="jd_ut"),
                    counterexample_rows=(
                        counterexamples(
                            motion_values,
                            times,
                            expected=motion_values[0],
                            coordinate_unit="jd_ut",
                        )
                        if motion_values
                        else []
                    ),
                ),
                "longitude_speed": _speed_evidence(
                    name=name,
                    samples=samples,
                    times=times,
                    speed_key="speed_lon",
                    value_kind="ecliptic_longitude_speed_range",
                    factor=profile.speed_envelope_factor,
                ),
                "latitude": _coordinate_evidence(
                    name=name,
                    samples=samples,
                    times=times,
                    value_key="lat",
                    speed_key="speed_lat",
                    value_kind="ecliptic_latitude_range",
                    unit="degrees",
                    factor=profile.speed_envelope_factor,
                ),
                "latitude_speed": _speed_evidence(
                    name=name,
                    samples=samples,
                    times=times,
                    speed_key="speed_lat",
                    value_kind="ecliptic_latitude_speed_range",
                    factor=profile.speed_envelope_factor,
                ),
                "right_ascension": _coordinate_evidence(
                    name=name,
                    samples=samples,
                    times=times,
                    value_key="right_ascension",
                    speed_key="right_ascension_speed",
                    value_kind="equatorial_right_ascension_range",
                    unit="degrees",
                    factor=profile.speed_envelope_factor,
                    circular=True,
                ),
                "right_ascension_speed": _speed_evidence(
                    name=name,
                    samples=samples,
                    times=times,
                    speed_key="right_ascension_speed",
                    value_kind="equatorial_right_ascension_speed_range",
                    factor=profile.speed_envelope_factor,
                ),
                "declination": _coordinate_evidence(
                    name=name,
                    samples=samples,
                    times=times,
                    value_key="declination",
                    speed_key="declination_speed",
                    value_kind="equatorial_declination_range",
                    unit="degrees",
                    factor=profile.speed_envelope_factor,
                ),
                "declination_speed": _speed_evidence(
                    name=name,
                    samples=samples,
                    times=times,
                    speed_key="declination_speed",
                    value_kind="equatorial_declination_speed_range",
                    factor=profile.speed_envelope_factor,
                ),
                "dignity": evidence_record(
                    feature_key=f"body:{name}:sign_dignity",
                    classification="invariant" if sign_dignity is not None else "variable",
                    value_kind="non_sect_sign_dignity_components",
                    possibilities=dignity_components,
                    prerequisite_refs=[f"body:{name}:sign"],
                    availability="available",
                    status_reason=(None if sign_dignity is not None else "zodiac sign varies across interval"),
                ),
            },
        }

    aspects = []
    names = list(body_ids)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            if first not in unwrapped or second not in unwrapped:
                aspects.append({"a": first, "b": second, "classification": "inconclusive"})
                continue
            observed = [_aspect_at(first, unwrapped[first][i], second, unwrapped[second][i], include_minor) for i in range(len(times))]
            distinct = set(observed)
            classification: Classification = "invariant" if len(distinct) == 1 and None not in distinct else "conditional"
            if len(distinct) > 1 and None not in distinct:
                classification = "variable"
            aspect_name = next(iter(distinct)) if len(distinct) == 1 else None
            orb_values = []
            if aspect_name:
                exact = ASPECTS[aspect_name]
                orb_values = [abs(_distance(unwrapped[first][i], unwrapped[second][i]) - exact) for i in range(len(times))]
                relative_padding = 0.0
                for sample_index in range(len(times) - 1):
                    first_speed = abs(float(samples[times[sample_index]][first]["speed_lon"]))
                    second_speed = abs(float(samples[times[sample_index]][second]["speed_lon"]))
                    relative_padding = max(
                        relative_padding,
                        (first_speed + second_speed) * (times[sample_index + 1] - times[sample_index]) * profile.speed_envelope_factor,
                    )
                orb_low = max(0.0, min(orb_values) - relative_padding)
                orb_high = max(orb_values) + relative_padding
                if orb_high > orb_allowed(first, second, aspect_name):
                    classification = "conditional"
            row = {
                    "a": first,
                    "b": second,
                    "classification": classification,
                    "aspect": aspect_name,
                    "possible_aspects": sorted(value for value in distinct if value is not None),
                    "orb_range": {"min": orb_low, "max": orb_high} if orb_values else None,
                }
            row["evidence"] = evidence_record(
                feature_key=f"aspect:{first}:{second}",
                classification=classification,
                value_kind="aspect_type",
                possibilities=(value for value in distinct if value is not None),
                prerequisite_refs=[f"body:{first}:longitude", f"body:{second}:longitude"],
                range_evidence=(
                    scalar_range(orb_low, orb_high, unit="degrees") if orb_values else None
                ),
                transitions=transition_witnesses(observed, times, coordinate_unit="jd_ut"),
                counterexample_rows=(
                    counterexamples(
                        observed,
                        times,
                        expected=observed[0],
                        coordinate_unit="jd_ut",
                    )
                    if observed
                    else []
                ),
            )
            aspects.append(row)
    return {
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "proof_profile": asdict(profile),
        "interval": {"start_jd": start_jd, "end_jd": end_jd, "boundary_policy": "inclusive"},
        "evaluation_count": len(times),
        "status": "inconclusive" if failures else "complete",
        "failures": failures,
        "bodies": bodies,
        "aspects": aspects,
    }


def _inconclusive_result(body_ids: Mapping[str, int], profile: IntervalProofProfile, reason: str) -> dict[str, Any]:
    return {
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "proof_profile": asdict(profile),
        "status": "inconclusive",
        "failures": [{"reason": reason}],
        "bodies": {name: {"classification": "inconclusive", "reason": reason} for name in body_ids},
        "aspects": [],
    }
