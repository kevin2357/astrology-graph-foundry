from __future__ import annotations

import json
from copy import deepcopy

from astro_analysis_sdk.projection_adapter import (
    project_synastry_package,
    projected_analysis_rows,
)


def package_fixture() -> dict:
    graph = {
        "graph_type": "canonical_astrology_graph",
        "graph_version": "1.3.0",
        "objects": [
            {
                "id": "synastry:person_a:natal:Venus",
                "name": "Venus",
                "object_type": "planet_or_point",
                "subject_owner": "person_a",
                "structural_strength_score": 0.9,
            },
            {
                "id": "synastry:person_b:natal:Mercury",
                "name": "Mercury",
                "object_type": "planet_or_point",
                "subject_owner": "person_b",
                "structural_strength_score": 0.85,
            },
            {
                "id": "synastry:person_b:house:3",
                "name": "person_b house 3",
                "object_type": "house_cusp",
                "subject_owner": "person_b",
                "facts": {"house": 3},
                "structural_strength_score": 0.7,
            },
        ],
        "relationships": [
            {
                "id": "syn:venus:trine:mercury",
                "relationship_type": "SYNASTRY_ASPECT",
                "direction": "a_to_b",
                "source_person": "Kevin",
                "target_person": "Bre",
                "source_id": "synastry:person_a:natal:Venus",
                "target_id": "synastry:person_b:natal:Mercury",
                "aspect": "trine",
                "orb": 0.4,
                "theme_key": "communication|ease_support|home_family",
                "operator_key": "connect|interpret",
                "structural_strength_score": 0.88,
            },
            {
                "id": "overlay:venus:house3",
                "relationship_type": "HOUSE_OVERLAY",
                "direction": "a_to_b",
                "source_person": "Kevin",
                "target_person": "Bre",
                "source_id": "synastry:person_a:natal:Venus",
                "target_id": "synastry:person_b:house:3",
                "target_house": 3,
                "theme_key": "communication|values_resources",
                "operator_key": "connect",
                "structural_strength_score": 0.76,
            },
        ],
        "summary": {"object_count": 3, "relationship_count": 2},
    }
    return {
        "metadata": {
            "analysis_type": "synastry_relationship_dataset",
            "source_chart_id": "natal:kevin",
            "source_chart_ids": ["natal:kevin", "natal:bre"],
            "sensor_instance_id": "synastry:natal:kevin:natal:bre",
        },
        "semantic_boundary": {},
        "canonical_astrology_graph": graph,
        "structural_evidence_graph": {"graph_version": "1.3.0"},
        "theme_registry": {
            "communication|ease_support|home_family": [
                "communication", "ease_support", "home_family"
            ],
            "communication|values_resources": [
                "communication", "values_resources"
            ],
        },
        "operator_registry": {
            "connect|interpret": [
                {"operator": "connect"},
                {"operator": "interpret"},
            ],
            "connect": [{"operator": "connect"}],
        },
        "object_registries": {},
        "natal_context_registries": {},
        "projection_views": {"orthodox_astrology.v1": {"theme_metrics": []}},
    }


def by_source_id(result: dict) -> dict[str, dict]:
    prefix = "canonical:relationship:"
    projected = {
        row["id"]: row for row in result["relationships"]
    }
    return {
        ref[len(prefix):]: projected[ids[0]]
        for ref, ids in result["indexes"][
            "projected_relationships_by_source_ref"
        ].items()
        if ref.startswith(prefix)
    }


def test_registry_aware_synastry_resolves_complete_theme_set():
    result = project_synastry_package(package_fixture())
    row = by_source_id(result)["syn:venus:trine:mercury"]
    assert {
        "communication", "ease_support", "home_family"
    } <= set(row["theme_tags"])
    registry_evidence = [
        value for value in row["attributes"]["theme_evidence"]
        if value["origin"] == "source_registry"
    ]
    assert {value["theme"] for value in registry_evidence} == {
        "communication", "ease_support", "home_family"
    }
    assert all(
        value["source_ref"]
        == "theme_registry:communication|ease_support|home_family"
        for value in registry_evidence
    )


def test_professional_context_changes_vocabulary_and_is_auditable():
    general = project_synastry_package(package_fixture(), professional=False)
    professional = project_synastry_package(package_fixture(), professional=True)
    general_row = by_source_id(general)["syn:venus:trine:mercury"]
    professional_row = by_source_id(professional)["syn:venus:trine:mercury"]
    assert "home_family" in general_row["theme_tags"]
    assert "team_foundation" in professional_row["theme_tags"]
    assert "romance_affection" in general_row["theme_tags"]
    assert "professional_rapport" in professional_row["theme_tags"]
    assert general_row["relationship_type"] == "supports_and_facilitates"
    assert professional_row["relationship_type"] == (
        "professional_supports_and_facilitates"
    )
    assert professional_row["attributes"]["context_mode"] == "professional"
    transformed = [
        value for value in professional_row["attributes"]["theme_evidence"]
        if value.get("context_transform")
    ]
    assert transformed


def test_house_overlay_preserves_direction_and_target_house():
    result = project_synastry_package(package_fixture())
    row = by_source_id(result)["overlay:venus:house3"]
    assert row["relationship_type"] == "activates_relationship_domain"
    assert row["attributes"]["direction"] == "a_to_b"
    assert row["attributes"]["source_person"] == "Kevin"
    assert row["attributes"]["target_person"] == "Bre"
    assert row["attributes"]["target_house"] == 3
    assert "communication" in row["theme_tags"]


def test_projected_analysis_rows_uses_batch_projection_result():
    package = package_fixture()
    source_rows = deepcopy(package["canonical_astrology_graph"]["relationships"])
    projected = project_synastry_package(package)
    rows = projected_analysis_rows(source_rows, projected)
    contact = rows[0]
    assert contact["projected_relationship_id"]
    assert {
        "communication", "ease_support", "home_family"
    } <= set(contact["theme_tags"])
    assert contact["projection_theme_evidence"]
    assert "theme_tags" not in source_rows[0]


def test_projection_is_deterministic_and_source_immutable():
    package = package_fixture()
    before = json.dumps(package["canonical_astrology_graph"], sort_keys=True)
    first = project_synastry_package(package)
    second = project_synastry_package(package)
    assert first == second
    assert json.dumps(package["canonical_astrology_graph"], sort_keys=True) == before
