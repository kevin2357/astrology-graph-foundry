
from __future__ import annotations

from copy import deepcopy

import pytest

from astrology_graph_foundry.pipelines import transit
from astrology_graph_foundry.temporal_projection_adapter import (
    build_temporal_projection_source_bundle,
)


def _full_package():
    return {
        "metadata": {
            "analysis_type": "transit_range_dataset",
            "target_label": "Kevin",
            "target_chart_id": "natal:kevin",
            "target_chart_type": "natal",
            "target_subject_scope": "individual",
            "semantic_scope": "individual_climate",
            "start_date": "2026-01-01",
            "end_date": "2026-01-02",
        },
        "period": {"start_date": "2026-01-01", "end_date": "2026-01-02", "day_count": 2},
        "target": {
            "chart": {
                "houses": {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)}
            }
        },
        "daily_windows": [
            {
                "date": "2026-01-01",
                "transit_datetime": "2026-01-01T12:00:00-07:00",
                "positions": {
                    "Mars": {"lon": 10.0, "speed_lon": 0.5, "retrograde": False},
                    "True Node": {"lon": 20.0, "speed_lon": -0.05, "retrograde": True},
                },
                "candidates": [
                    {
                        "transit_body": "Mars",
                        "aspect": "square",
                        "target": "Venus",
                        "target_name": "Venus",
                        "target_id": "natal:Venus",
                        "target_type": "planet_or_point",
                        "orb": 0.5,
                        "rank": 1,
                        "relevance_score": 10.0,
                    },
                    {
                        "transit_body": "Uranus",
                        "aspect": "sextile",
                        "target": "Mean Node",
                        "target_name": "Mean Node",
                        "target_id": "natal:Mean_Node",
                        "target_type": "planet_or_point",
                        "orb": 0.4,
                        "rank": 2,
                        "relevance_score": 9.0,
                    },
                ],
            },
            {
                "date": "2026-01-02",
                "transit_datetime": "2026-01-02T12:00:00-07:00",
                "positions": {
                    "Mars": {"lon": 10.5, "speed_lon": 0.5, "retrograde": False},
                    "True Node": {"lon": 19.95, "speed_lon": -0.05, "retrograde": True},
                },
                "candidates": [],
            },
        ],
        "transit_arcs": [
            {
                "arc_id": "arc:tc:Mars:square:natal_Venus",
                "candidate_id": "tc:Mars:square:natal_Venus",
                "transit_body": "Mars",
                "aspect": "square",
                "target": "Venus",
                "target_name": "Venus",
                "target_id": "natal:Venus",
                "target_type": "planet_or_point",
            },
            {
                "arc_id": "arc:tc:Uranus:sextile:natal_Mean_Node",
                "candidate_id": "tc:Uranus:sextile:natal_Mean_Node",
                "transit_body": "Uranus",
                "aspect": "sextile",
                "target": "Mean Node",
                "target_name": "Mean Node",
                "target_id": "natal:Mean_Node",
                "target_type": "planet_or_point",
            },
        ],
        "monthly_summary": [],
        "target_type_metrics": [],
        "activated_relationship_type_metrics": [],
        "activated_target_relationship_registry": {},
        "canonical_astrology_graph": {
            "graph_type": "canonical_astrology_graph",
            "source_chart_id": "natal:kevin",
            "objects": [{"id": "natal:Venus"}],
            "relationships": [],
        },
        "structural_evidence_graph": {"graph_type": "structural_evidence_graph"},
    }


def _standard_streaming():
    return transit.streaming_index(_full_package(), profile="standard")


def _target_package():
    return {
        "metadata": {"source_chart_id": "natal:kevin"},
        "canonical_astrology_graph": deepcopy(_full_package()["canonical_astrology_graph"]),
        "structural_evidence_graph": deepcopy(_full_package()["structural_evidence_graph"]),
    }


def test_game_materialization_from_standard_streaming_is_populated_and_complete():
    standard = _standard_streaming()
    game = transit.streaming_index(
        standard,
        profile="game",
        target_set="gameplay",
    )
    assert list(game["days_by_date"]) == ["2026-01-01", "2026-01-02"]
    assert game["candidate_registry"]
    assert game["days_by_date"]["2026-01-01"]["contacts"]
    assert game["days_by_date"]["2026-01-02"]["contacts"] == []
    for day in game["days_by_date"].values():
        for contact in day["contacts"]:
            assert contact["candidate_id"] in game["candidate_registry"]
    assert "Mars" in game["days_by_date"]["2026-01-01"]["daily_sky"]["positions"]


def test_gameplay_policy_excludes_mean_node_from_standard_streaming():
    game = transit.streaming_index(
        _standard_streaming(),
        profile="game",
        target_set="gameplay",
    )
    assert all("Mean_Node" not in candidate_id for candidate_id in game["candidate_registry"])


def test_temporal_bundle_uses_explicit_target_graph_for_streaming_source():
    standard = _standard_streaming()
    bundle = build_temporal_projection_source_bundle(
        standard,
        target_package=_target_package(),
        target_set="gameplay",
    )
    assert bundle["static_source_graph"]["graph_type"] == "canonical_astrology_graph"
    assert bundle["static_source_graph"]["source_chart_id"] == bundle["target_identity"]["chart_id"]
    assert bundle["metadata"]["static_source_graph_authority"] == "explicit_target_dataset"
    assert bundle["metadata"]["transit_target_set"] == "gameplay"
    assert all(
        "Mean_Node" not in activation["target_ref"]
        for activation in bundle["temporal_source_graph"]["activations"]
    )


def test_temporal_bundle_fails_when_streaming_source_has_no_target_dataset():
    with pytest.raises(ValueError, match="requires a nonempty canonical target graph"):
        build_temporal_projection_source_bundle(_standard_streaming())


def test_temporal_bundle_rejects_target_identity_mismatch():
    target = _target_package()
    target["canonical_astrology_graph"]["source_chart_id"] = "natal:ashley"
    with pytest.raises(ValueError, match="target mismatch"):
        build_temporal_projection_source_bundle(
            _standard_streaming(),
            target_package=target,
        )
