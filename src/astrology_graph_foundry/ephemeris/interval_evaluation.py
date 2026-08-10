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
        segment_padding = []
        for index in range(len(times) - 1):
            duration = times[index + 1] - times[index]
            observed_speed = max(abs(speeds[index]), abs(speeds[index + 1]))
            segment_padding.append(observed_speed * duration * profile.speed_envelope_factor)
        low = min(path[index] - (segment_padding[index - 1] if index else segment_padding[0]) for index in range(len(path)))
        high = max(path[index] + (segment_padding[index - 1] if index else segment_padding[0]) for index in range(len(path)))
        signs = _signs_for_range(low, high, profile.longitude_tolerance_degrees)
        speed_padding = max(
            (abs(speeds[index + 1] - speeds[index]) * profile.speed_envelope_factor for index in range(len(speeds) - 1)),
            default=0.0,
        )
        speed_low, speed_high = min(speeds) - speed_padding, max(speeds) + speed_padding
        motions = _motion_states(speed_low, speed_high, profile.speed_zero_tolerance_degrees_per_day)
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
            aspects.append(
                {
                    "a": first,
                    "b": second,
                    "classification": classification,
                    "aspect": aspect_name,
                    "possible_aspects": sorted(value for value in distinct if value is not None),
                    "orb_range": {"min": orb_low, "max": orb_high} if orb_values else None,
                }
            )
    return {
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
        "proof_profile": asdict(profile),
        "status": "inconclusive",
        "failures": [{"reason": reason}],
        "bodies": {name: {"classification": "inconclusive", "reason": reason} for name in body_ids},
        "aspects": [],
    }
