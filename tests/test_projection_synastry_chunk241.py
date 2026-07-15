from __future__ import annotations

from astrology_graph_foundry.projection_adapter import (
    projection_coverage_for_rows,
    select_projection_representative_rows,
    summarize_unmapped_families,
)


def graph_fixture() -> dict:
    return {
        "objects": [
            {
                "id": "planet:Venus",
                "name": "Venus",
                "object_type": "planet_or_point",
            },
            {
                "id": "house:3",
                "name": "house 3",
                "object_type": "house_cusp",
                "facts": {"house": 3},
            },
            {
                "id": "harmonic:Venus:5",
                "name": "Venus harmonic 5",
                "object_type": "harmonic_point",
            },
        ],
        "relationships": [
            {
                "id": "overlay:expanded",
                "relationship_type": "HOUSE_OVERLAY",
                "source_id": "harmonic:Venus:5",
                "target_id": "house:3",
            },
            {
                "id": "overlay:venus",
                "relationship_type": "HOUSE_OVERLAY",
                "source_id": "planet:Venus",
                "target_id": "house:3",
            },
        ],
    }


def test_supported_overlay_is_selected_before_expanded_row():
    graph = graph_fixture()
    selected, summary = select_projection_representative_rows(
        graph,
        graph["relationships"],
        limit=1,
    )
    assert [row["id"] for row in selected] == ["overlay:venus"]
    assert summary["available_projectable_row_count"] == 1
    assert summary["selected_projectable_row_count"] == 1


def test_selection_fills_remaining_slots_without_dropping_expanded_rows():
    graph = graph_fixture()
    selected, summary = select_projection_representative_rows(
        graph,
        graph["relationships"],
        limit=2,
    )
    assert [row["id"] for row in selected] == [
        "overlay:venus",
        "overlay:expanded",
    ]
    assert summary["selected_unprojectable_row_count"] == 1


def test_coverage_and_unmapped_family_summary_are_compact():
    graph = graph_fixture()
    projected = {
        "relationships": [{
            "id": "projected:overlay:venus",
            "source_relationship_refs": [
                "canonical:relationship:overlay:venus"
            ],
        }],
        "indexes": {
            "projected_relationships_by_source_ref": {
                "canonical:relationship:overlay:venus": [
                    "projected:overlay:venus"
                ]
            }
        },
        "diagnostics": {
            "unmapped_source_refs": [
                "canonical:object:harmonic:Venus:5",
                "canonical:relationship:overlay:expanded",
            ]
        },
    }
    coverage = projection_coverage_for_rows(
        graph["relationships"],
        projected,
    )
    assert coverage == {
        "selected_row_count": 2,
        "projected_row_count": 1,
        "unprojected_row_count": 1,
    }

    summary = summarize_unmapped_families(graph, projected)
    assert summary["unmapped_source_count"] == 2
    families = {row["family"]: row["count"] for row in summary["families"]}
    assert families == {
        "object:harmonic_point": 1,
        "relationship:HOUSE_OVERLAY": 1,
    }
