from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from astrology_graph_foundry.common.temporal_activation import (
    TemporalExportOptions,
    TemporalSourceContractError,
    extract_canonical_temporal_activation_graph,
)


def _candidate(date: str, orb: float, *, retrograde: bool = False) -> dict:
    return {
        "candidate_id": "tc:Mars:square:natal_Venus",
        "rank": 1,
        "transit_body": "Mars",
        "aspect": "square",
        "target": "Venus",
        "target_id": "natal:Venus",
        "target_type": "planet_or_point",
        "target_house": 8,
        "transit_house_in_target_chart": 6,
        "orb": orb,
        "distance": 90 + orb,
        "relevance_score": 0.88,
        "strength": "very tight",
        "positions": {
            "Mars": {
                "longitude": 120.0,
                "speed": -0.1 if retrograde else 0.4,
                "retrograde": retrograde,
                "sign": "Leo",
            }
        },
        "date": date,
    }


def _package() -> dict:
    observations = [
        ("2026-01-01", 1.2, False),
        ("2026-01-02", 0.4, False),
        ("2026-01-03", 0.005, False),
        ("2026-01-04", 0.5, False),
        # Deliberate gap creates a second pass.
        ("2026-01-10", 0.7, True),
        ("2026-01-11", 0.2, True),
        ("2026-01-12", 0.8, True),
    ]
    days = []
    for day, orb, retrograde in observations:
        candidate = _candidate(day, orb, retrograde=retrograde)
        candidate.pop("date", None)
        days.append(
            {
                "date": day,
                "transit_datetime": f"{day}T12:00:00-07:00",
                "positions": {
                    "Mars": {
                        "longitude": 120.0,
                        "speed": -0.1 if retrograde else 0.4,
                        "retrograde": retrograde,
                        "sign": "Leo",
                    }
                },
                "candidates": [candidate],
            }
        )
    return {
        "metadata": {
            "analysis_type": "transit_range_dataset",
            "target_label": "Kevin",
            "target_chart_id": "natal:kevin",
            "target_chart_type": "natal",
            "target_subject_scope": "individual",
            "semantic_scope": "individual_climate",
            "start_date": "2026-01-01",
            "end_date": "2026-01-12",
        },
        "target": {"metadata": {}, "chart": {}},
        "period": {
            "start_date": "2026-01-01",
            "end_date": "2026-01-12",
            "day_count": 12,
        },
        "daily_windows": days,
        "transit_arcs": [
            {
                "arc_id": "arc:tc:Mars:square:natal_Venus",
                "candidate_id": "tc:Mars:square:natal_Venus",
                "transit_body": "Mars",
                "aspect": "square",
                "target": "Venus",
                "target_id": "natal:Venus",
                "target_type": "planet_or_point",
                "target_house": 8,
                "transit_house_in_target_chart": 6,
                "start_date": "2026-01-01",
                "end_date": "2026-01-12",
                "observation_dates": [row[0] for row in observations],
                "closest_orb": 0.005,
            }
        ],
        "canonical_astrology_graph": {
            "graph_type": "canonical_astrology_graph",
            "graph_version": "1.3.0",
            "metadata": {"graph_id": "canonical:natal:kevin"},
        },
    }


def test_full_transit_export_is_arc_first_directional_and_deterministic():
    package = _package()
    original = copy.deepcopy(package)
    options = TemporalExportOptions(max_observation_gap_days=2)

    first = extract_canonical_temporal_activation_graph(package, options=options)
    second = extract_canonical_temporal_activation_graph(package, options=options)

    assert package == original
    assert first == second
    assert first["metadata"]["authoritative_unit"] == "activation_arc"
    assert first["summary"]["sequence_count"] == 1
    assert first["summary"]["activation_count"] == 2

    direct, retrograde = first["activations"]
    assert direct["sequence_id"] == retrograde["sequence_id"]
    assert direct["pass_index"] == 1
    assert retrograde["pass_index"] == 2
    assert direct["activator_ref"] == "canonical:transiting_object:mars"
    assert direct["target_ref"] == "natal:Venus"
    assert direct["relationship_type"] == "TRANSIT_ACTIVATION"
    assert direct["exactness"]["status"] == "sampled_exact"
    assert direct["exactness"]["note"].startswith("Exact time is a sampled observation")
    assert direct["motion"]["states"] == ["direct"]
    assert retrograde["motion"]["states"] == ["retrograde"]
    assert [state["phase"] for state in direct["observation_states"]] == [
        "applying_observed",
        "applying_observed",
        "sampled_exact",
        "separating_observed",
    ]
    assert all(
        state["strength_label"] == "very tight"
        for state in direct["observation_states"]
    )
    assert all("strength" not in state for state in direct["observation_states"])



def test_full_transit_daily_candidates_without_materialized_candidate_ids_join_arc_rows():
    package = _package()
    for day in package["daily_windows"]:
        day["candidates"][0].pop("candidate_id", None)

    result = extract_canonical_temporal_activation_graph(package)

    assert result["summary"]["activation_count"] == 2
    assert result["summary"]["observation_state_count"] == 7
    assert result["summary"]["warning_count"] == 0
    assert all(
        activation["provenance"]["observation_join_policy"]
        == "candidate_id_exact"
        for activation in result["activations"]
    )
    assert [
        activation["observation_count"] for activation in result["activations"]
    ] == [4, 3]

@pytest.mark.parametrize(
    "label",
    [
        "tight",
        "very tight",
        "partile / extremely tight",
        "exact / ultra-partile",
    ],
)
def test_temporal_observation_strength_labels_are_preserved_as_labels(label: str):
    package = _package()
    for day in package["daily_windows"]:
        day["candidates"][0]["strength"] = label

    result = extract_canonical_temporal_activation_graph(package)

    labels = {
        state["strength_label"]
        for activation in result["activations"]
        for state in activation["observation_states"]
    }
    assert labels == {label}


def test_analysis_view_is_rejected_as_incomplete_source_contract():
    package = {
        "view_type": "analysis",
        "metadata": {"analysis_type": "transit_range_dataset"},
        "transit_arcs": [],
    }
    with pytest.raises(TemporalSourceContractError, match="ranked subset"):
        extract_canonical_temporal_activation_graph(package)


def test_schema_validates_exported_fixture():
    root = Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "schemas"
    schema = json.loads(
        (root / "canonical_temporal_activation_graph_v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    result = extract_canonical_temporal_activation_graph(_package())
    errors = sorted(
        Draft202012Validator(schema).iter_errors(result),
        key=lambda error: list(error.path),
    )
    assert not errors, [error.message for error in errors]


def test_streaming_index_materialization_is_supported():
    full = _package()
    registry = {}
    days = []
    for day in full["daily_windows"]:
        candidate = day["candidates"][0]
        cid = candidate["candidate_id"]
        registry.setdefault(
            cid,
            {
                key: value
                for key, value in candidate.items()
                if key not in {"rank", "orb", "distance", "relevance_score", "strength"}
            },
        )
        days.append(
            {
                "date": day["date"],
                "transit_datetime": day["transit_datetime"],
                "candidate_refs": [
                    {
                        "candidate_id": cid,
                        "rank": candidate["rank"],
                        "orb": candidate["orb"],
                        "distance": candidate["distance"],
                        "relevance_score": candidate["relevance_score"],
                        "strength": candidate["strength"],
                    }
                ],
            }
        )
    streaming = {
        "view_type": "streaming_index",
        "metadata": full["metadata"],
        "period": full["period"],
        "candidate_registry": registry,
        "days": days,
        "arcs": full["transit_arcs"],
    }
    result = extract_canonical_temporal_activation_graph(streaming)
    assert result["metadata"]["source_materialization"] == "streaming_index"
    assert result["summary"]["activation_count"] == 2
