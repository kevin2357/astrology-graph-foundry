import json
from pathlib import Path

from astrology_graph_foundry.pipelines import annual_profections


SCHEMA_DIR = Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "schemas"


def _target(chart_type="natal"):
    chart = {
        "person": "Example",
        "birth_local": "1990-04-12T09:30:00",
        "birth_timezone": "UTC",
        "birth_lat": 0.0,
        "birth_lon": 0.0,
        "houses": {
            str(i): {
                "lon": (i - 1) * 30.0,
                "traditional_ruler": "Mars" if i == 1 else "Venus",
            }
            for i in range(1, 13)
        },
        "bodies": {"nSun": {"lon": 22.0}, "nMoon": {"lon": 100.0}},
    }
    if chart_type == "natal":
        return {"metadata": {"analysis_type": "natal_dataset", "person": "Example"}, "natal": chart}
    if chart_type == "composite":
        return {
            "metadata": {"analysis_type": "composite_dataset", "person_a": "A", "person_b": "B"},
            "composite_chart": chart,
            "composite_reference_event": {
                "midpoint_utc": "1990-04-12T09:30:00+00:00",
                "midpoint_lat": 0.0,
                "midpoint_lon": 0.0,
                "timezone": "UTC",
            },
        }
    raise AssertionError(chart_type)


def test_relationship_entity_profection_is_explicitly_experimental():
    pkg = annual_profections.build(target_dataset=_target("composite"), target_date="2026-07-07")
    assert pkg["metadata"]["target_chart_type"] == "composite"
    assert pkg["metadata"]["experimental_relationship_entity_technique"] is True
    assert "Experimental relationship-entity profection" in pkg["profection"]["interpretation_note"]


def test_public_view_schema_files_exist_and_parse():
    names = [
        "natal_analysis_view_v1.schema.json",
        "transit_analysis_view_v1.schema.json",
        "transit_streaming_index_v1.schema.json",
        "synastry_analysis_view_v1.schema.json",
        "synastry_streaming_index_v1.schema.json",
    ]
    for name in names:
        data = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        assert data["type"] == "object"
        assert data["required"]
