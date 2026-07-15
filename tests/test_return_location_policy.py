import pytest

from astro_analysis_sdk.common.return_location import resolve_return_location
from astro_analysis_sdk.common.transitable_chart import from_package
from astro_analysis_sdk.pipelines import annual_profections


def _natal_package():
    return {
        "metadata": {"analysis_type": "natal_dataset", "person": "Example"},
        "natal": {
            "person": "Example",
            "birth_local": "1990-04-12T09:30:00",
            "birth_timezone": "America/Denver",
            "birth_lat": 39.7392,
            "birth_lon": -104.9903,
            "birth_location_label": "Denver, Colorado",
            "houses": {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)},
            "bodies": {"nSun": {"lon": 22.0}, "nMoon": {"lon": 100.0}},
        },
    }


def test_return_location_policy_is_mandatory_for_api_callers():
    target = from_package(_natal_package())
    with pytest.raises(ValueError, match="mandatory"):
        resolve_return_location(target=target, return_location_policy="")


def test_target_reference_policy_resolves_reference_event_location():
    target = from_package(_natal_package())
    resolved = resolve_return_location(
        target=target,
        return_location_policy="target_reference",
    )
    assert resolved["policy"] == "target_reference"
    assert resolved["location_label"] == "Denver, Colorado"
    assert resolved["lat"] == pytest.approx(39.7392)


def test_explicit_policy_requires_complete_location():
    target = from_package(_natal_package())
    with pytest.raises(ValueError, match="requires all explicit location fields"):
        resolve_return_location(
            target=target,
            return_location_policy="explicit",
            location_timezone="America/Denver",
            location_lat=39.7392,
        )


def test_explicit_policy_preserves_resolved_location():
    target = from_package(_natal_package())
    resolved = resolve_return_location(
        target=target,
        return_location_policy="explicit",
        location_timezone="America/Denver",
        location_lat=39.7392,
        location_lon=-104.9903,
        location_label="Denver, Colorado",
    )
    assert resolved == {
        "policy": "explicit",
        "timezone": "America/Denver",
        "lat": 39.7392,
        "lon": -104.9903,
        "location_label": "Denver, Colorado",
        "source": "cli_or_api_explicit_location",
    }


def test_composite_profection_uses_traditional_sign_ruler_fallback():
    chart = _natal_package()["natal"]
    chart["houses"] = {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)}
    package = {
        "metadata": {
            "analysis_type": "composite_dataset",
            "person_a": "A",
            "person_b": "B",
        },
        "composite_chart": chart,
        "composite_reference_event": {
            "midpoint_utc": "1990-04-12T09:30:00+00:00",
            "midpoint_lat": 39.7392,
            "midpoint_lon": -104.9903,
            "timezone": "America/Denver",
            "location_label": "Composite reference",
        },
    }
    # 36 completed years -> house 1 -> Aries -> Mars.
    result = annual_profections.build(
        target_dataset=package,
        target_date="2026-04-12",
    )
    assert result["profection"]["activated_sign"] == "Aries"
    assert result["profection"]["time_lord"] == "Mars"
