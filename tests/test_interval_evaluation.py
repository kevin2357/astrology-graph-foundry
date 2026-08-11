from __future__ import annotations

import math

from astrology_graph_foundry.ephemeris.interval_evaluation import IntervalProofProfile, evaluate_interval

PROFILE = IntervalProofProfile(minimum_step_seconds=60, maximum_evaluations=3000)


def _linear(**bodies):
    def evaluate(jd):
        return {name: {"lon": (start + speed * jd) % 360, "speed_lon": speed} for name, (start, speed) in bodies.items()}

    return evaluate


def _rich_linear(**bodies):
    def evaluate(jd):
        return {
            name: {
                "lon": (start + speed * jd) % 360,
                "speed_lon": speed,
                "lat": latitude + latitude_speed * jd,
                "speed_lat": latitude_speed,
                "right_ascension": (right_ascension + right_ascension_speed * jd) % 360,
                "right_ascension_speed": right_ascension_speed,
                "declination": declination + declination_speed * jd,
                "declination_speed": declination_speed,
            }
            for name, (
                start,
                speed,
                latitude,
                latitude_speed,
                right_ascension,
                right_ascension_speed,
                declination,
                declination_speed,
            ) in bodies.items()
        }

    return evaluate


def test_stable_and_variable_moon_signs():
    stable = evaluate_interval(0, 0.25, {"Moon": 1}, _linear(Moon=(5, 13)), profile=PROFILE)
    variable = evaluate_interval(0, 0.25, {"Moon": 1}, _linear(Moon=(29, 13)), profile=PROFILE)
    assert stable["bodies"]["Moon"]["classification"] == "invariant"
    assert stable["bodies"]["Moon"]["sign_dignity"]["sign"] == "Aries"
    assert stable["bodies"]["Moon"]["sign_dignity"]["sect_dependent_components"] == "unavailable"
    assert variable["bodies"]["Moon"]["classification"] == "variable"
    assert variable["bodies"]["Moon"]["sign_dignity"] is None
    assert variable["bodies"]["Moon"]["longitude_range"]["possible_sign_indexes"] == [0, 1]


def test_circular_wraparound_is_not_a_false_zodiac_ingress():
    result = evaluate_interval(0, 0.2, {"Sun": 0}, _linear(Sun=(359.9, 2)), profile=PROFILE)
    evidence = result["bodies"]["Sun"]["longitude_range"]
    assert evidence["unwrapped_min"] > 358
    assert evidence["unwrapped_max"] > 359
    generalized = result["bodies"]["Sun"]["evidence"]["longitude"]
    assert generalized["range_evidence"]["wraps_origin"] is True
    assert len(generalized["range_evidence"]["segments"]) == 2


def test_station_window_is_variable_motion():
    def station(jd):
        speed = jd - 0.5
        return {"Mercury": {"lon": 10 + (jd - 0.5) ** 2 / 2, "speed_lon": speed}}

    result = evaluate_interval(0, 1, {"Mercury": 2}, station, profile=PROFILE)
    assert result["bodies"]["Mercury"]["motion"]["classification"] == "variable"
    assert set(result["bodies"]["Mercury"]["motion"]["possible_states"]) == {"direct", "retrograde", "stationary"}


def test_aspect_entry_exit_and_invariant_orb_range():
    invariant = evaluate_interval(0, 0.1, {"Sun": 0, "Moon": 1}, _linear(Sun=(0, 1), Moon=(120, 1)), profile=PROFILE)
    row = invariant["aspects"][0]
    assert row["classification"] == "invariant"
    assert row["aspect"] == "trine"
    assert row["orb_range"]["min"] == 0

    crossing = evaluate_interval(0, 1, {"Sun": 0, "Moon": 1}, _linear(Sun=(0, 0), Moon=(112, 16)), profile=PROFILE)
    assert crossing["aspects"][0]["classification"] == "conditional"


def test_dense_refinement_detects_multiple_crossing_threat():
    def oscillating(jd):
        phase = 2 * math.pi * jd * 48
        return {"Moon": {"lon": 29.5 + math.sin(phase), "speed_lon": 2 * math.pi * 48 * math.cos(phase)}}

    result = evaluate_interval(0, 1 / 24, {"Moon": 1}, oscillating, profile=PROFILE)
    assert result["bodies"]["Moon"]["classification"] == "variable"
    assert result["evaluation_count"] == 61


def test_provider_failure_and_budget_exhaustion_fail_closed():
    def failure(_jd):
        raise RuntimeError("synthetic failure")

    failed = evaluate_interval(0, 0.01, {"Sun": 0}, failure, profile=PROFILE)
    assert failed["status"] == "inconclusive"
    assert "provider failure" in failed["failures"][0]["reason"]

    tiny_budget = IntervalProofProfile(minimum_step_seconds=1, maximum_evaluations=2)
    exhausted = evaluate_interval(0, 1, {"Sun": 0}, _linear(Sun=(0, 1)), profile=tiny_budget)
    assert exhausted["status"] == "inconclusive"


def test_repeat_determinism():
    args = (0, 0.25, {"Sun": 0, "Moon": 1}, _linear(Sun=(1, 1), Moon=(121, 13)))
    assert evaluate_interval(*args, profile=PROFILE) == evaluate_interval(*args, profile=PROFILE)


def test_generalized_evidence_records_prerequisites_transitions_and_counterexamples():
    result = evaluate_interval(0, 0.25, {"Moon": 1}, _linear(Moon=(29, 13)), profile=PROFILE)
    assert result["evidence_contract_version"] == "agf.bounded_uncertainty_evidence.v1.0.0"
    sign = result["bodies"]["Moon"]["evidence"]["sign"]
    assert sign["classification"] == "variable"
    assert sign["possibilities"]["values"] == ["Aries", "Taurus"]
    assert sign["prerequisite_refs"] == ["body:Moon:longitude"]
    assert sign["transition_witnesses"]
    assert sign["counterexamples"]


def test_aspect_generalized_evidence_preserves_endpoint_prerequisites():
    result = evaluate_interval(0, 0.1, {"Sun": 0, "Moon": 1}, _linear(Sun=(0, 1), Moon=(120, 1)), profile=PROFILE)
    row = result["aspects"][0]["evidence"]
    assert row["classification"] == "invariant"
    assert row["possibilities"]["values"] == ["trine"]
    assert row["prerequisite_refs"] == ["body:Moon:longitude", "body:Sun:longitude"]
    assert row["range_evidence"]["range_type"] == "scalar_closed"


def test_rich_coordinate_ranges_match_exhaustive_sample_oracle_and_preserve_dignity_truths():
    evaluator = _rich_linear(Mars=(10, 1, -2, 0.2, 359.9, 2, -20, 0.5))
    result = evaluate_interval(0, 0.1, {"Mars": 4}, evaluator, profile=PROFILE)
    evidence = result["bodies"]["Mars"]["evidence"]
    assert evidence["latitude"]["availability"] == "available"
    assert evidence["latitude"]["range_evidence"]["observed"] == {"minimum": -2.0, "maximum": -1.98}
    assert evidence["declination"]["range_evidence"]["observed"] == {"minimum": -20.0, "maximum": -19.95}
    assert evidence["right_ascension"]["range_evidence"]["wraps_origin"] is True
    assert evidence["dignity"]["possibilities"]["values"] == [
        "detriment_traditional=false",
        "domicile_modern=true",
        "domicile_traditional=true",
        "exaltation=false",
        "fall=false",
    ]


def test_missing_and_nonfinite_optional_provider_fields_are_feature_local():
    missing = evaluate_interval(0, 0.1, {"Sun": 0}, _linear(Sun=(10, 1)), profile=PROFILE)
    assert missing["status"] == "complete"
    assert missing["bodies"]["Sun"]["evidence"]["declination"]["classification"] == "inconclusive"
    assert missing["bodies"]["Sun"]["evidence"]["declination"]["availability"] == "missing_provider_field"

    def nonfinite(jd):
        row = _rich_linear(Sun=(10, 1, 0, 0, 10, 1, 0, 0))(jd)
        row["Sun"]["declination"] = math.nan
        return row

    result = evaluate_interval(0, 0.1, {"Sun": 0}, nonfinite, profile=PROFILE)
    assert result["bodies"]["Sun"]["evidence"]["declination"]["availability"] == "nonfinite_provider_value"


def test_feature_local_provider_failure_is_not_mislabeled_as_missing_data():
    def failed_equatorial(jd):
        row = _linear(Sun=(10, 1))(jd)
        row["Sun"].update(
            {
                "declination_availability": "provider_failure",
                "declination_status_reason": "synthetic equatorial failure",
                "declination_speed_availability": "provider_failure",
                "declination_speed_status_reason": "synthetic equatorial failure",
            }
        )
        return row

    result = evaluate_interval(0, 0.1, {"Sun": 0}, failed_equatorial, profile=PROFILE)
    evidence = result["bodies"]["Sun"]["evidence"]["declination"]
    assert evidence["availability"] == "provider_failure"
    assert evidence["status_reason"] == "synthetic equatorial failure"


def test_antiscia_and_contra_antiscia_transform_ranges_preserve_wrap_and_lineage():
    result = evaluate_interval(0, 0.1, {"Sun": 0}, _linear(Sun=(359.9, 1)), profile=PROFILE)
    transforms = result["bodies"]["Sun"]["transforms"]
    antiscia = transforms["antiscia"]["evidence"]
    contra = transforms["contra_antiscia"]["evidence"]
    assert antiscia["prerequisite_refs"] == ["body:Sun:longitude"]
    assert contra["prerequisite_refs"] == ["body:Sun:longitude"]
    assert antiscia["range_evidence"]["range_type"] == "circular_closed_segments"
    assert contra["range_evidence"]["range_type"] == "circular_closed_segments"


def test_harmonic_multiplication_handles_origin_wrap_and_full_circle_coverage():
    wrapped = evaluate_interval(
        0,
        0.1,
        {"Sun": 0},
        _linear(Sun=(119.9, 1)),
        harmonic_numbers=(3,),
        profile=PROFILE,
    )["bodies"]["Sun"]["transforms"]["harmonics"]["3"]
    assert wrapped["evidence"]["range_evidence"]["wraps_origin"] is True

    full = evaluate_interval(
        0,
        1,
        {"Moon": 1},
        _linear(Moon=(0, 50)),
        harmonic_numbers=(9,),
        profile=PROFILE,
    )["bodies"]["Moon"]["transforms"]["harmonics"]["9"]
    assert full["classification"] == "variable"
    assert full["evidence"]["range_evidence"]["coverage"] == "full_circle"
    assert full["possible_sign_indexes"] == list(range(12))


def test_disabled_transforms_are_absent_instead_of_mislabeled_variable():
    result = evaluate_interval(
        0,
        0.1,
        {"Sun": 0},
        _linear(Sun=(11, 1)),
        include_antiscia=False,
        include_harmonics=False,
        profile=PROFILE,
    )
    assert result["bodies"]["Sun"]["transforms"] == {}


def test_transform_sign_sets_agree_with_exhaustive_minute_oracle_away_from_boundaries():
    start, end = 0.0, 0.1
    result = evaluate_interval(
        start,
        end,
        {"Sun": 0},
        _linear(Sun=(11, 1)),
        harmonic_numbers=(2, 3, 5),
        profile=PROFILE,
    )
    transforms = result["bodies"]["Sun"]["transforms"]
    count = math.ceil((end - start) / (PROFILE.minimum_step_seconds / 86400.0))
    source_values = [11 + (end - start) * index / count for index in range(count + 1)]
    cases = {
        "antiscia": ((180 - value) % 360 for value in source_values),
        "contra_antiscia": ((180 + value) % 360 for value in source_values),
        "harmonic:2": ((2 * value) % 360 for value in source_values),
        "harmonic:3": ((3 * value) % 360 for value in source_values),
        "harmonic:5": ((5 * value) % 360 for value in source_values),
    }
    for key, values in cases.items():
        row = transforms[key] if not key.startswith("harmonic:") else transforms["harmonics"][key.split(":")[1]]
        oracle = sorted({int(value // 30) % 12 for value in values})
        assert row["possible_sign_indexes"] == oracle
