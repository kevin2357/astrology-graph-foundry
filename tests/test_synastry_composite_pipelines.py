from copy import deepcopy

from astrology_graph_foundry.common.identity import derive_relationship_source_chart_id
from astrology_graph_foundry.pipelines import composite, synastry


def natal(name, sun, moon, asc, source_chart_id=None):
    metadata = {"person": name}
    if source_chart_id:
        metadata["source_chart_id"] = source_chart_id
    return {
        "metadata": metadata,
        "person": {"person": name},
        "natal": {
            "person": name,
            "houses": {str(i): {"lon": (i - 1) * 30.0} for i in range(1, 13)},
            "bodies": {
                "nSun": {"lon": sun, "pretty": "Sun", "type": "planet_or_point", "house": 1},
                "nMoon": {"lon": moon, "pretty": "Moon", "type": "planet_or_point", "house": 3},
                "nASC": {"lon": asc, "pretty": "ASC", "type": "angle", "house": 1},
                "nDSC": {"lon": (asc + 180) % 360, "pretty": "DSC", "type": "angle", "house": 7},
                "nMC": {"lon": 90.0, "pretty": "MC", "type": "angle", "house": 10},
                "nIC": {"lon": 270.0, "pretty": "IC", "type": "angle", "house": 4},
            },
            "lots": {"Fortune": {"lon": 130.0, "pretty": "Fortune", "house": 5}},
            "fixed_stars": [],
            "natal_planet_aspects": [],
            "natal_planet_angle_aspects": [],
            "natal_planet_point_aspects": [],
            "declination_aspects": [],
        },
    }


def test_composite_pipeline_builds_midpoint_chart_and_semantic_graph():
    a = natal("A", 10.0, 70.0, 0.0)
    b = natal("B", 20.0, 80.0, 10.0)
    pkg = composite.build_from_datasets(a, b)
    assert pkg["metadata"]["analysis_type"] == "composite_dataset"
    assert pkg["transitable_chart"]["chart_identity"]["chart_type"] == "composite"
    assert pkg["composite_chart"]["bodies"]["nSun"]["lon"] == 15.0
    assert pkg["canonical_astrology_graph"]["objects"]
    assert pkg["composite_aspects"]
    assert pkg["projection_views"]["orthodox_astrology.v1"]["theme_metrics"]


def test_synastry_pipeline_uses_expanded_graph_and_embeds_composite():
    a = natal("A", 10.0, 70.0, 0.0)
    b = natal("B", 10.2, 130.0, 180.0)
    pkg = synastry.build_from_datasets(a, b)
    assert pkg["metadata"]["analysis_type"] == "synastry_relationship_dataset"
    assert pkg["metadata"]["uses_expanded_natal_semantic_graph"] is True
    assert pkg["natal_synastry"]["a_to_b_aspects"]
    assert pkg["natal_synastry"]["a_to_b_house_overlays"]
    row = pkg["natal_synastry"]["a_to_b_aspects"][0]
    assert row["relationship_type"] == "SYNASTRY_ASPECT"
    assert "theme_key" in row
    assert "operator_key" in row
    assert "source_natal_context_refs" in row
    assert pkg["theme_registry"][row["theme_key"]]
    assert pkg["operator_registry"][row["operator_key"]]
    assert pkg["natal_context_registries"]["person_a"]
    assert pkg["composite"]["metadata"]["analysis_type"] == "composite_dataset"


def test_synastry_analysis_and_streaming_views_are_compact():
    a = natal("A", 10.0, 70.0, 0.0)
    b = natal("B", 10.2, 130.0, 180.0)
    pkg = synastry.build_from_datasets(a, b)
    analysis = synastry.analysis_view(pkg)
    streaming = synastry.streaming_index(pkg)
    assert analysis["metadata"]["view_type"] == "synastry_analysis"
    assert analysis["metadata"]["view_compaction"] == "source_factual_relationship_handoff_v3"
    assert analysis["metadata"]["projection_status"] == "not_performed"
    assert analysis["canonical_source_graph"] == pkg["canonical_astrology_graph"]
    assert analysis["structural_evidence_graph"] == pkg["structural_evidence_graph"]
    assert "projected_objects" not in analysis
    assert "projection_coverage" not in analysis
    assert analysis["natal_context_hints"]["person_a"]
    assert streaming["metadata"]["view_type"] == "synastry_streaming_index"
    assert streaming["contact_registry"]
    top_ref = streaming["ranked_contacts"][0]
    assert "contact_id" in top_ref
    assert "theme_tags" not in top_ref
    assert top_ref["contact_id"] in streaming["contact_registry"]


def test_composite_identity_uses_participant_chart_ids_not_display_names():
    first_a = natal("Scout", 10.0, 70.0, 0.0, "astrowoof:dog:A")
    first_b = natal("Buddy", 20.0, 80.0, 10.0, "astrowoof:dog:B")
    renamed_a = deepcopy(first_a)
    renamed_b = deepcopy(first_b)
    renamed_a["metadata"]["person"] = "Scout Renamed"
    renamed_b["metadata"]["person"] = "Buddy Renamed"

    first = composite.build_from_datasets(first_a, first_b)
    renamed = composite.build_from_datasets(renamed_a, renamed_b)
    reversed_pair = composite.build_from_datasets(first_b, first_a)

    expected = derive_relationship_source_chart_id(
        "composite", ["astrowoof:dog:A", "astrowoof:dog:B"]
    )
    assert first["metadata"]["source_chart_id"] == expected
    assert renamed["metadata"]["source_chart_id"] == expected
    assert reversed_pair["metadata"]["source_chart_id"] == expected
    assert first["transitable_chart"]["chart_identity"]["chart_id"] == expected
    assert first["canonical_astrology_graph"]["source_chart_id"] == expected


def test_same_named_participants_remain_distinct_in_synastry_source_identity():
    a = natal("Scout", 10.0, 70.0, 0.0, "astrowoof:dog:A")
    b = natal("Scout", 10.2, 130.0, 180.0, "astrowoof:dog:B")

    package = synastry.build_from_datasets(a, b, include_composite=False)

    assert package["metadata"]["source_chart_ids"] == ["astrowoof:dog:A", "astrowoof:dog:B"]
    assert package["metadata"]["sensor_instance_id"] == "synastry:astrowoof:dog:A:astrowoof:dog:B"


def test_relationship_identity_derivation_is_technique_specific_and_order_independent():
    participants = ["astrowoof:dog:A", "astrowoof:dog:B"]
    composite_id = derive_relationship_source_chart_id("composite", participants)
    davison_id = derive_relationship_source_chart_id("davison", reversed(participants))

    assert composite_id == derive_relationship_source_chart_id("composite", reversed(participants))
    assert composite_id.startswith("composite:")
    assert davison_id.startswith("davison:")
    assert composite_id.split(":", 1)[1] != davison_id.split(":", 1)[1]
