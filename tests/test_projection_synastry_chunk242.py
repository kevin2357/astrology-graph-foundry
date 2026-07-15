from __future__ import annotations

from astrology_graph_foundry.projection_adapter import (
    canonical_subset_for_relationship_ids,
    select_projection_representative_rows,
    summarize_unmapped_families,
)


def graph_fixture() -> dict:
    return {
        "objects": [
            {
                "id": "synastry:person_a:natal:Venus",
                "name": "Venus",
                "object_type": "planet_or_point",
            },
            {
                "id": "synastry:person_b:house:3",
                "name": "person_b house 3",
                "object_type": "house_cusp",
                "facts": {"house": 3},
            },
            {
                "id": "synastry:person_a:harmonic:Venus:5",
                "name": "Venus harmonic 5",
                "object_type": "harmonic_point",
            },
        ],
        "relationships": [
            {
                "id": "overlay:venus",
                "relationship_type": "HOUSE_OVERLAY",
                "source_id": "synastry:person_a:natal:Venus",
                "target_id": "synastry:person_b:house:3",
            },
            {
                "id": "overlay:expanded",
                "relationship_type": "HOUSE_OVERLAY",
                "source_id": "synastry:person_a:harmonic:Venus:5",
                "target_id": "synastry:person_b:house:3",
            },
        ],
    }


def compact_rows() -> list[dict]:
    # Deliberately use compact/raw endpoint IDs that differ from canonical IDs.
    return [
        {
            "id": "overlay:expanded",
            "source_object_id": "harmonic:Venus:5",
            "target_object_id": "house:3",
        },
        {
            "id": "overlay:venus",
            "source_object_id": "natal:Venus",
            "target_object_id": "house:3",
        },
    ]


def test_selection_resolves_projectability_by_shared_relationship_id():
    selected, summary = select_projection_representative_rows(
        graph_fixture(),
        compact_rows(),
        limit=1,
    )
    assert [row["id"] for row in selected] == ["overlay:venus"]
    assert summary["available_projectable_row_count"] == 1
    assert summary["selected_projectable_row_count"] == 1
    assert summary["unresolved_canonical_relationship_id_count"] == 0


def test_canonical_subset_uses_canonical_endpoint_namespace():
    subset = canonical_subset_for_relationship_ids(
        graph_fixture(),
        ["overlay:expanded"],
    )
    assert [row["id"] for row in subset["relationships"]] == [
        "overlay:expanded"
    ]
    assert {row["id"] for row in subset["objects"]} == {
        "synastry:person_a:harmonic:Venus:5",
        "synastry:person_b:house:3",
    }


def test_unmapped_summary_reports_real_object_family_not_unknown():
    subset = canonical_subset_for_relationship_ids(
        graph_fixture(),
        ["overlay:expanded"],
    )
    projected = {
        "diagnostics": {
            "unmapped_source_refs": [
                "canonical:object:synastry:person_a:harmonic:Venus:5",
                "canonical:relationship:overlay:expanded",
            ]
        }
    }
    summary = summarize_unmapped_families(subset, projected)
    families = {row["family"]: row["count"] for row in summary["families"]}
    assert families == {
        "object:harmonic_point": 1,
        "relationship:HOUSE_OVERLAY": 1,
    }
