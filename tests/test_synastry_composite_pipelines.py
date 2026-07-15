from astro_analysis_sdk.pipelines import composite, synastry


def natal(name, sun, moon, asc):
    return {
        "metadata": {"person": name},
        "person": {"person": name},
        "natal": {
            "person": name,
            "houses": {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)},
            "bodies": {
                "nSun": {"lon": sun, "pretty": "Sun", "type": "planet_or_point", "house": 1},
                "nMoon": {"lon": moon, "pretty": "Moon", "type": "planet_or_point", "house": 3},
                "nASC": {"lon": asc, "pretty": "ASC", "type": "angle", "house": 1},
                "nDSC": {"lon": (asc + 180) % 360, "pretty": "DSC", "type": "angle", "house": 7},
                "nMC": {"lon": 90.0, "pretty": "MC", "type": "angle", "house": 10},
                "nIC": {"lon": 270.0, "pretty": "IC", "type": "angle", "house": 4},
            },
            "lots": {"Fortune": {"lon": 130.0, "pretty": "Fortune", "house": 5}},
            "fixed_stars": [],
            "natal_planet_aspects": [],
            "natal_planet_angle_aspects": [],
            "natal_planet_point_aspects": [],
            "declination_aspects": [],
        },
    }


def test_composite_pipeline_builds_midpoint_chart_and_semantic_graph():
    a = natal("A", 10.0, 70.0, 0.0)
    b = natal("B", 20.0, 80.0, 10.0)
    pkg = composite.build_from_datasets(a, b)
    assert pkg["metadata"]["analysis_type"] == "composite_dataset"
    assert pkg["transitable_chart"]["chart_identity"]["chart_type"] == "composite"
    assert pkg["composite_chart"]["bodies"]["nSun"]["lon"] == 15.0
    assert pkg["canonical_astrology_graph"]["objects"]
    assert pkg["composite_aspects"]
    assert pkg["projection_views"]["orthodox_astrology.v1"]["theme_metrics"]


def test_synastry_pipeline_uses_expanded_graph_and_embeds_composite():
    a = natal("A", 10.0, 70.0, 0.0)
    b = natal("B", 10.2, 130.0, 180.0)
    pkg = synastry.build_from_datasets(a, b)
    assert pkg["metadata"]["analysis_type"] == "synastry_relationship_dataset"
    assert pkg["metadata"]["uses_expanded_natal_semantic_graph"] is True
    assert pkg["natal_synastry"]["a_to_b_aspects"]
    assert pkg["natal_synastry"]["a_to_b_house_overlays"]
    row = pkg["natal_synastry"]["a_to_b_aspects"][0]
    assert row["relationship_type"] == "SYNASTRY_ASPECT"
    assert "theme_key" in row
    assert "operator_key" in row
    assert "source_natal_context_refs" in row
    assert pkg["theme_registry"][row["theme_key"]]
    assert pkg["operator_registry"][row["operator_key"]]
    assert pkg["natal_context_registries"]["person_a"]
    assert pkg["composite"]["metadata"]["analysis_type"] == "composite_dataset"


def test_synastry_analysis_and_streaming_views_are_compact():
    a = natal("A", 10.0, 70.0, 0.0)
    b = natal("B", 10.2, 130.0, 180.0)
    pkg = synastry.build_from_datasets(a, b)
    analysis = synastry.analysis_view(pkg)
    streaming = synastry.streaming_index(pkg)
    assert analysis["metadata"]["view_type"] == "synastry_analysis"
    assert analysis["natal_context_hints"]["person_a"]
    assert streaming["metadata"]["view_type"] == "synastry_streaming_index"
    assert streaming["contact_registry"]
    top_ref = streaming["ranked_contacts"][0]
    assert "contact_id" in top_ref
    assert "theme_tags" not in top_ref
    assert top_ref["contact_id"] in streaming["contact_registry"]
