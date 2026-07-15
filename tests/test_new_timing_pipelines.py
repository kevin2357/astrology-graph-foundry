from astrology_graph_foundry.pipelines import annual_profections, progressed, solar_arc, transit


def sample_natal():
    return {
        "metadata": {"person": "Example"},
        "natal": {
            "person": "Example",
            "birth_local": "1990-04-12T09:30:00",
            "birth_timezone": "America/Denver",
            "birth_lat": 39.7392,
            "birth_lon": -104.9903,
            "houses": {str(i): {"lon": (i - 1) * 30.0, "traditional_ruler": "Mars" if i == 1 else "Venus"} for i in range(1, 13)},
            "bodies": {"nSun": {"lon": 22.0}, "nMoon": {"lon": 100.0}},
        },
    }


def test_annual_profections_builds_age_house_package():
    pkg = annual_profections.build(target_dataset=sample_natal(), target_date="2026-04-12")
    assert pkg["metadata"]["analysis_type"] == "annual_profections_dataset"
    assert pkg["profection"]["completed_years"] == 36
    assert pkg["profection"]["activated_house"] == 1


def test_transit_unified_module_exposes_views():
    assert callable(transit.build)
    assert callable(transit.analysis_view)
    assert callable(transit.streaming_index)


def test_complex_timing_scaffolds_identify_status():
    assert progressed.build()["metadata"]["implementation_status"] == "scaffold"
    assert solar_arc.build()["metadata"]["implementation_status"] == "scaffold"
