from astrology_graph_foundry.common.graph_compiler import GraphCompiler


def sample_natal():
    return {
        "person": "Example",
        "houses": {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)},
        "bodies": {
            "nSun": {"lon": 10.0, "pretty": "Aries 10", "type": "planet_or_point", "house": 1},
            "nMoon": {"lon": 70.0, "pretty": "Gemini 10", "type": "planet_or_point", "house": 3},
        },
        "lots": {"Fortune": {"lon": 130.0, "pretty": "Leo 10", "house": 5}},
        "fixed_stars": [],
        "natal_planet_aspects": [],
        "natal_planet_angle_aspects": [],
        "natal_planet_point_aspects": [],
        "declination_aspects": [],
    }


def test_graph_compiler_caches_targets_and_relationship_context():
    compiler = GraphCompiler(sample_natal())
    assert compiler.metadata()["target_count"] >= 3
    assert compiler.target_count_by_type()["planet_or_point"] == 2
    assert compiler.target_count_by_type()["lot"] == 1


def test_graph_compiler_builds_ranked_transit_candidates():
    compiler = GraphCompiler(sample_natal())
    _, ranked = compiler.transit_to_target_candidates(
        {"Mars": {"lon": 10.2}},
        include_minor=False,
        top_n=5,
    )
    assert ranked
    assert ranked[0]["relationship_type"] == "TRANSIT_ACTIVATION"
    assert ranked[0]["target_id"].startswith("natal:")
    assert "activated_target_relationships" in ranked[0]
    assert ranked[0]["rank"] == 1
