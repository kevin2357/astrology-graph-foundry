import gzip
import json
from pathlib import Path

from astrology_graph_foundry.common.io import read_json, write_json
from astrology_graph_foundry.pipelines import transit_period
from types import SimpleNamespace


def sample_natal():
    return {
        "person": "Example",
        "houses": {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)},
        "bodies": {
            "nSun": {"lon": 10.0, "pretty": "Aries 10", "type": "planet_or_point", "house": 1},
            "nMoon": {"lon": 70.0, "pretty": "Gemini 10", "type": "planet_or_point", "house": 3},
        },
        "lots": {},
        "fixed_stars": [],
        "natal_planet_aspects": [{"body1": "nSun", "body2": "nMoon", "aspect": "sextile", "orb": 0.2}],
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
                date_local=date, local_datetime=f"{date}T12:00:00",
                positions={
                    "Mars": {"lon": 10.1, "retrograde": False, "speed_lon": 0.7},
                    "Venus": {"lon": 70.0, "retrograde": False, "speed_lon": 1.1},
                },
                reverse_read_candidates=[], transit_to_transit_aspects=[],
            )


def _package():
    return transit_period.build_from_provider(FakeProvider(), "2026-01-01", "2026-01-02", top_n_per_day=5)


def test_standard_profile_preserves_legacy_shape():
    view = transit_period.streaming_index(_package(), profile="standard")
    assert view["streaming_profile"] == "standard"
    assert isinstance(view["days"], list)
    assert "candidate_registry" in view
    assert "activated_target_relationship_registry" in view


def test_compact_profile_uses_date_index_and_reduced_registry():
    view = transit_period.streaming_index(_package(), profile="compact")
    assert view["streaming_profile"] == "compact"
    assert set(view["days_by_date"]) == {"2026-01-01", "2026-01-02"}
    assert view["candidate_registry"]
    assert "target_pretty" not in next(iter(view["candidate_registry"].values()))


def test_game_profile_filters_targets_and_includes_daily_sky():
    view = transit_period.streaming_index(_package(), profile="game")
    assert view["streaming_profile"] == "game"
    assert view["target_set"] == "gameplay"
    day = view["days_by_date"]["2026-01-01"]
    assert day["daily_sky"]["positions"]["Mars"]["sign"] == "Aries"
    assert day["daily_sky"]["positions"]["Mars"]["house"] == 1
    assert day["contacts"]
    assert {row["transit_body"] for row in view["candidate_registry"].values()} <= {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "True Node"}
    names = {row["target_name"] for row in view["candidate_registry"].values()}
    assert names <= {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "True Node", "ASC", "DSC", "MC", "IC"}


def test_gzip_json_roundtrip_is_deterministic(tmp_path: Path):
    view = transit_period.streaming_index(_package(), profile="game")
    one = tmp_path / "one.json.gz"
    two = tmp_path / "two.json.gz"
    write_json(one, view)
    write_json(two, view)
    assert read_json(one) == view
    assert one.read_bytes() == two.read_bytes()
    with gzip.open(one, "rt", encoding="utf-8") as handle:
        assert json.load(handle)["streaming_profile"] == "game"
