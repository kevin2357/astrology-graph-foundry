from astro_analysis_sdk.common.chart_graph import normalize_relationship_list
from astro_analysis_sdk.common.transitable_chart import descriptor_for_package, from_package


def _chart(label="Chart"):
    return {
        "person": label,
        "birth_local": "1990-01-01T12:00:00",
        "birth_timezone": "UTC",
        "birth_lat": 0.0,
        "birth_lon": 0.0,
        "houses": {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)},
        "bodies": {"nSun": {"lon": 10.0, "type": "planet_or_point", "house": 1}, "nMoon": {"lon": 90.0, "type": "planet_or_point", "house": 4}},
        "natal_planet_aspects": [],
        "natal_planet_angle_aspects": [],
        "natal_planet_point_aspects": [],
        "declination_aspects": [],
        "lots": {},
        "fixed_stars": [],
    }


def test_transitable_chart_descriptor_exposes_return_and_lunation_capabilities():
    pkg = {"metadata": {"analysis_type": "natal_dataset", "person": "A"}, "natal": _chart("A")}
    desc = descriptor_for_package(pkg)
    assert desc["capabilities"]["supports_solar_return"] is True
    assert desc["capabilities"]["supports_lunation_activation"] is True
    assert desc["capabilities"]["supports_lunar_return"] is True
    assert desc["capabilities"]["supports_annual_profections"] is True
    assert desc["reference_event"]["event_local"] == "1990-01-01T12:00:00"


def test_composite_reference_event_is_read_by_interface():
    pkg = {
        "metadata": {"analysis_type": "composite_dataset", "person_a": "A", "person_b": "B"},
        "composite_chart": _chart("Composite: A + B"),
        "composite_reference_event": {
            "midpoint_utc": "1995-01-01T00:00:00+00:00",
            "midpoint_lat": 10.0,
            "midpoint_lon": 20.0,
            "timezone": "UTC",
        },
    }
    target = from_package(pkg)
    assert target.reference_event["event_utc"] == "1995-01-01T00:00:00+00:00"
    assert target.reference_event["method"] == "synthetic_midpoint_reference_event"


def test_relationship_ids_and_order_are_stable_across_input_order():
    rels = [
        {"relationship_type": "aspect", "source_id": "b", "target_id": "c", "aspect": "square", "orb": 2.0},
        {"relationship_type": "aspect", "source_id": "a", "target_id": "b", "aspect": "trine", "orb": 1.0},
    ]
    a = normalize_relationship_list(rels)
    b = normalize_relationship_list(list(reversed(rels)))
    assert [row["id"] for row in a] == [row["id"] for row in b]
    assert a == b
