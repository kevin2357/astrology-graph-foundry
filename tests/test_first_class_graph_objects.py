from astro_analysis_sdk.common.chart_graph import (
    REL_HAS_DIGNITY,
    REL_HAS_HARMONIC_POINT,
    REL_TRANSIT_ACTIVATION,
    build_chart_graph,
)


def test_promotes_nested_body_facts_to_graph_objects():
    natal = {
        "bodies": {
            "nSun": {
                "lon": 10,
                "pretty": "Aries 10",
                "type": "planet_or_point",
                "house": 1,
                "dignity": {"sign": "Aries"},
                "harmonics": {"2": {"lon": 20, "pretty": "Aries 20"}},
                "antiscia": {"antiscia_lon": 170, "contra_antiscia_lon": 190},
            },
            "nMoon": {"lon": 70, "pretty": "Gemini 10", "type": "planet_or_point", "house": 3},
        },
        "lots": {"Fortune": {"lon": 25, "pretty": "Aries 25", "house": 1}},
        "declination_aspects": [],
        "natal_planet_aspects": [],
        "natal_planet_angle_aspects": [],
        "natal_planet_point_aspects": [],
        "sect": {"is_day_chart": True},
    }
    graph = build_chart_graph(natal)
    object_types = {obj["object_type"] for obj in graph["objects"]}
    rel_types = {rel["relationship_type"] for rel in graph["relationships"]}
    assert "dignity_state" in object_types
    assert "harmonic_point" in object_types
    assert "antiscia_point" in object_types
    assert "lot" in object_types
    assert REL_HAS_DIGNITY in rel_types
    assert REL_HAS_HARMONIC_POINT in rel_types
    assert REL_TRANSIT_ACTIVATION in graph["relationship_type_ontology"]
