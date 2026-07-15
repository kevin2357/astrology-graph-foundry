from types import SimpleNamespace
from astro_analysis_sdk.pipelines import transit_period


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
        "natal_planet_aspects": [
            {"body1": "nSun", "body2": "nMoon", "aspect": "sextile", "orb": 0.2},
        ],
        "natal_planet_angle_aspects": [],
        "natal_planet_point_aspects": [],
        "declination_aspects": [],
    }


class FakeProvider:
    def __init__(self):
        self._natal = sample_natal()

    def target_metadata(self):
        return {"person": "Example", "target_label": "Example", "chart_type": "natal", "subject_scope": "individual", "semantic_scope": "individual_climate", "provider": "fake"}

    def target_chart(self):
        return self._natal

    def iter_days(self):
        for date in ["2026-01-01", "2026-01-02"]:
            yield SimpleNamespace(
                date_local=date,
                local_datetime=f"{date}T12:00:00",
                positions={"Mars": {"lon": 10.1}, "Venus": {"lon": 70.0}},
                reverse_read_candidates=[],
                transit_to_transit_aspects=[],
            )


def test_streaming_index_uses_candidate_registry_for_daily_rows():
    package = transit_period.build_from_provider(FakeProvider(), "2026-01-01", "2026-01-02", top_n_per_day=5)
    streaming = transit_period.streaming_index(package)
    assert streaming["candidate_registry"]
    day = streaming["days"][0]
    assert day["candidate_refs"]
    row = day["candidate_refs"][0]
    assert "candidate_id" in row
    assert "orb" in row
    assert "theme_tags" not in row
    assert row["candidate_id"] in streaming["candidate_registry"]
    registry_row = streaming["candidate_registry"][row["candidate_id"]]
    assert "theme_tags" in registry_row
    assert "semantic_operator_hints" in registry_row
