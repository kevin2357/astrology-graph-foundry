from astro_analysis_sdk.common.transitable_chart import descriptor_for_package, from_package


def chart(label="Chart"):
    return {
        "person": label,
        "houses": {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)},
        "bodies": {"nSun": {"lon": 10.0, "type": "planet_or_point", "house": 1}},
        "natal_planet_aspects": [],
        "natal_planet_angle_aspects": [],
        "natal_planet_point_aspects": [],
        "declination_aspects": [],
        "lots": {},
        "fixed_stars": [],
    }


def test_natal_package_is_transitable():
    package = {"metadata": {"analysis_type": "natal_dataset", "person": "A"}, "natal": chart("A")}
    target = from_package(package)
    assert target.chart_type == "natal"
    assert target.subject_scope == "individual"
    assert descriptor_for_package(package)["chart_key"] == "natal"


def test_davison_package_is_transitable_relationship_chart():
    package = {
        "metadata": {"analysis_type": "davison_relationship_dataset", "person_a": "A", "person_b": "B"},
        "davison_event": {"method": "midpoint in time and space"},
        "davison_chart": chart("Davison: A + B"),
    }
    target = from_package(package)
    assert target.chart_type == "davison"
    assert target.subject_scope == "relationship"
    assert target.semantic_scope == "relationship_lifecycle_climate"


def test_composite_package_is_transitable_without_becoming_natal():
    package = {
        "metadata": {"analysis_type": "composite_dataset", "person_a": "A", "person_b": "B", "composite_method": "midpoint_longitude"},
        "composite_chart": chart("Composite: A + B"),
    }
    target = from_package(package)
    assert target.chart_type == "composite"
    assert target.subject_scope == "relationship"
    assert target.semantic_scope == "relationship_pattern_climate"
