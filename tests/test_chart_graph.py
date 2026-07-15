from astro_analysis_sdk.common.chart_graph import build_chart_graph


def test_chart_graph_includes_lots_as_transit_targets():
    natal = {
        "bodies": {"nSun": {"lon": 10, "type": "planet_or_point", "house": 1}},
        "lots": {"Fortune": {"lon": 40, "house": 2}},
        "fixed_stars": [],
    }
    graph = build_chart_graph(natal)
    types = {o["object_type"] for o in graph["objects"]}
    assert "lot" in types
    assert any(o["name"] == "Fortune" and o["transit_target"] for o in graph["objects"])
