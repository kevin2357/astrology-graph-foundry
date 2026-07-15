import json
from pathlib import Path

from astrology_graph_foundry.common.semantic_layers import (
    ORTHODOX_PROFILE_ID,
    finalize_package_semantic_boundary,
    structural_strength_score,
)


SCHEMA_DIR = Path(__file__).parents[1] / "src" / "astrology_graph_foundry" / "schemas"


def sample_graph():
    return {
        "summary": {"object_count": 2, "relationship_count": 1},
        "objects": [
            {
                "id": "obj:mars",
                "name": "Mars",
                "source_key": "nMars",
                "object_type": "planet_or_point",
                "facts": {"longitude": 10.0},
                "transit_target": True,
                "theme_tags": ["conflict_drive"],
                "semantic_operator_hints": [{"operator": "act"}],
            },
            {
                "id": "obj:venus_h5",
                "name": "Venus harmonic 5",
                "source_key": "nVenus_H5",
                "object_type": "harmonic_point",
                "facts": {"longitude": 82.0},
                "transit_target": True,
                "theme_tags": ["romance_affection"],
                "semantic_operator_hints": [{"operator": "value"}],
                "owner_object_ref": "obj:venus",
            },
        ],
        "relationships": [
            {
                "id": "rel:1",
                "relationship_type": "ASPECT",
                "source_id": "obj:mars",
                "target_id": "obj:venus_h5",
                "source_name": "Mars",
                "target_name": "Venus harmonic 5",
                "aspect": "square",
                "orb": 0.5,
                "theme_tags": ["romance_affection", "conflict_drive"],
                "semantic_operator_hints": [{"operator": "stress"}],
                "relevance_score": 88.0,
            }
        ],
    }


def test_boundary_materializes_canonical_and_projection_layers_without_legacy_aliases():
    package = {
        "metadata": {"analysis_type": "natal_dataset", "person": "Example"},
        "semantic_graph": sample_graph(),
        "theme_metrics": [{"theme": "romance_affection", "score": 12.0}],
        "evidence_graph": [{
            "id": "claim:1",
            "claim": "Strong romance affection signature.",
            "confidence": 0.98,
        }],
        "report_materials": {"recommended_sections": ["Romance"]},
    }

    result = finalize_package_semantic_boundary(package)

    assert "semantic_graph" not in result
    assert "theme_metrics" not in result
    assert "relationship_metrics" not in result
    assert "evidence_graph" not in result
    assert "report_materials" not in result
    assert result["metadata"]["legacy_semantic_aliases_materialized"] is False

    canonical = result["canonical_astrology_graph"]
    assert canonical["graph_type"] == "canonical_astrology_graph"
    assert canonical["projection_status"] == "pre_projection"
    assert all("theme_tags" not in row for row in canonical["objects"])
    assert all("orthodox_astrology_theme_tags" not in row for row in canonical["relationships"])
    assert canonical["objects"][1]["evidence_metadata"]["evidence_tier"] == "harmonic"
    assert canonical["objects"][1]["evidence_metadata"]["owner_object_ref"] == "obj:venus"

    orthodox = result["projection_views"][ORTHODOX_PROFILE_ID]
    assert orthodox["theme_metrics"][0]["theme"] == "romance_affection"
    claim = orthodox["claim_candidates"][0]
    assert "confidence" not in claim
    assert claim["legacy_confidence"] == 0.98
    assert claim["weighted_support_score"] == 0.98
    assert claim["claim_status"] == "orthodox_projection_candidate"


def test_structural_strength_excludes_orthodox_relevance_score():
    direct = {
        "aspect": "square",
        "orb": 0.25,
        "active_days": 9,
        "relevance_score": 99.0,
        "evidence_metadata": {"derivation_type": "direct"},
    }
    changed_relevance = {**direct, "relevance_score": 1.0}
    derived = {
        **direct,
        "evidence_metadata": {"derivation_type": "derived"},
    }

    assert structural_strength_score(direct) == structural_strength_score(changed_relevance)
    assert structural_strength_score(direct) > structural_strength_score(derived)


def test_independence_groups_collapse_derived_object_to_owner():
    package = {
        "metadata": {"analysis_type": "natal_dataset", "person": "Example"},
        "semantic_graph": sample_graph(),
    }
    result = finalize_package_semantic_boundary(package)
    canonical = result["canonical_astrology_graph"]
    harmonic = next(row for row in canonical["objects"] if row["id"] == "obj:venus_h5")
    assert harmonic["evidence_metadata"]["independence_group"].endswith(":obj:venus")


def test_synastry_package_gets_synthetic_canonical_graph():
    package = {
        "metadata": {
            "analysis_type": "synastry_relationship_dataset",
            "person_a": "A",
            "person_b": "B",
        },
        "object_registries": {
            "person_a": {
                "a:mars": {"id": "a:mars", "name": "Mars", "object_type": "planet_or_point"}
            },
            "person_b": {
                "b:venus": {"id": "b:venus", "name": "Venus", "object_type": "planet_or_point"}
            },
        },
        "natal_synastry": {
            "a_to_b_aspects": [{
                "id": "syn:1",
                "relationship_type": "SYNASTRY_ASPECT",
                "source_object_id": "a:mars",
                "target_object_id": "b:venus",
                "aspect": "square",
                "orb": 0.4,
                "theme_tags": ["romance_affection"],
                "semantic_operator_hints": [{"operator": "stress"}],
            }],
            "b_to_a_aspects": [],
            "a_to_b_house_overlays": [],
            "b_to_a_house_overlays": [],
        },
        "evidence_graph": [],
        "report_materials": {},
    }
    result = finalize_package_semantic_boundary(package)
    graph = result["canonical_astrology_graph"]
    assert len(graph["objects"]) == 2
    assert len(graph["relationships"]) == 1
    assert "theme_tags" not in graph["relationships"][0]
    assert result["semantic_boundary"]["canonical_layer"] == "canonical_astrology_graph"


def test_new_boundary_schemas_exist_and_parse():
    names = [
        "canonical_astrology_graph_v1.schema.json",
        "structural_evidence_graph_v1.schema.json",
        "orthodox_astrology_projection_view_v1.schema.json",
        "evidence_provenance_v1.schema.json",
        "semantic_boundary_bundle_v1.schema.json",
    ]
    for name in names:
        data = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        assert data["type"] == "object"

def test_relationship_inherits_derived_endpoint_tier_and_family_owner():
    package = {
        "metadata": {"analysis_type": "natal_dataset", "person": "Example"},
        "semantic_graph": sample_graph(),
    }
    result = finalize_package_semantic_boundary(package)
    rel = result["canonical_astrology_graph"]["relationships"][0]
    evidence = rel["evidence_metadata"]
    assert evidence["evidence_tier"] == "harmonic"
    assert evidence["derivation_type"] == "direct_relation_between_derived_objects"
    assert evidence["target_owner_object_ref"] == "obj:venus"
    assert evidence["evidence_family_group"].endswith(":obj:mars:obj:venus:square")


def test_record_and_family_independence_counts_are_separate():
    graph = sample_graph()
    second = dict(graph["objects"][1])
    second["id"] = "obj:venus_h7"
    second["source_key"] = "nVenus_H7"
    graph["objects"].append(second)
    graph["relationships"].append({
        **graph["relationships"][0],
        "id": "rel:2",
        "target_id": "obj:venus_h7",
    })
    graph["summary"] = {"object_count": 3, "relationship_count": 2}
    result = finalize_package_semantic_boundary({
        "metadata": {"analysis_type": "natal_dataset", "person": "Example"},
        "semantic_graph": graph,
    })
    structural = result["structural_evidence_graph"]
    assert structural["record_independence_group_count"] > structural["evidence_family_group_count"]
    rels = result["canonical_astrology_graph"]["relationships"]
    assert rels[0]["evidence_metadata"]["record_independence_group"] != rels[1]["evidence_metadata"]["record_independence_group"]
    assert rels[0]["evidence_metadata"]["evidence_family_group"] == rels[1]["evidence_metadata"]["evidence_family_group"]


def test_synastry_registry_operator_is_resolved_without_theme_leakage():
    package = {
        "metadata": {
            "analysis_type": "synastry_relationship_dataset",
            "person_a": "A",
            "person_b": "B",
        },
        "object_registries": {
            "person_a": {
                "natal:Mars": {"id": "natal:Mars", "name": "Mars", "object_type": "planet_or_point"}
            },
            "person_b": {
                "natal:Venus": {"id": "natal:Venus", "name": "Venus", "object_type": "planet_or_point"}
            },
        },
        "operator_registry": {
            "op:stress": [{"operator": "stress", "confidence": 0.9}]
        },
        "theme_registry": {
            "theme:romance": ["romance_affection"]
        },
        "natal_synastry": {
            "a_to_b_aspects": [{
                "id": "syn:1",
                "relationship_type": "SYNASTRY_ASPECT",
                "source_object_id": "natal:Mars",
                "target_object_id": "natal:Venus",
                "aspect": "square",
                "orb": 0.4,
                "theme_key": "theme:romance",
                "operator_key": "op:stress",
            }],
            "b_to_a_aspects": [],
            "a_to_b_house_overlays": [],
            "b_to_a_house_overlays": [],
        },
        "relationship_metrics": [{"theme": "romance_affection", "score": 8.0}],
        "evidence_graph": [],
        "report_materials": {},
    }
    result = finalize_package_semantic_boundary(package)
    graph = result["canonical_astrology_graph"]
    rel = graph["relationships"][0]
    assert rel["source_id"] == "synastry:person_a:natal:Mars"
    assert rel["target_id"] == "synastry:person_b:natal:Venus"
    assert rel["operator_hints"][0]["operator"] == "stress"
    assert "theme_tags" not in rel
    assert "romance_affection" not in json.dumps(graph)
    orthodox = result["projection_views"][ORTHODOX_PROFILE_ID]
    assert orthodox["metric_source_field"] == "relationship_metrics"
    assert orthodox["theme_metrics"][0]["theme"] == "romance_affection"


def test_lunar_return_range_exposes_nested_canonical_chart_registry():
    nested = sample_graph()
    package = {
        "metadata": {"analysis_type": "lunar_return_dataset", "target_chart_id": "natal:example"},
        "target": {
            "chart_identity": {
                "chart_id": "natal:example",
                "label": "Example",
            }
        },
        "returns": [{
            "return_id": "lr:1",
            "sequence": 1,
            "return_event": {"event_utc": "2026-01-01T00:00:00+00:00"},
            "return_chart": {"semantic_graph": nested},
        }],
        "report_materials": {},
    }
    result = finalize_package_semantic_boundary(package)
    registry = result["canonical_astrology_graph"]["nested_canonical_graph_registry"]
    assert list(registry) == ["lr:1"]
    nested_canonical = registry["lr:1"]
    assert nested_canonical["graph_type"] == "canonical_astrology_graph"
    assert all("theme_tags" not in row for row in nested_canonical["objects"])
    assert nested_canonical["relationships"][0]["evidence_metadata"]["evidence_tier"] == "harmonic"



def test_chunk12_sensor_ids_do_not_collide_between_people():
    def pkg(name):
        return {
            "metadata": {"analysis_type": "natal_dataset", "person": name},
            "semantic_graph": sample_graph(),
            "theme_metrics": [],
            "evidence_graph": [],
            "report_materials": {},
        }
    kevin = finalize_package_semantic_boundary(pkg("Kevin"))
    bre = finalize_package_semantic_boundary(pkg("Bre"))
    assert kevin["metadata"]["source_chart_id"] == "natal:kevin"
    assert bre["metadata"]["source_chart_id"] == "natal:bre"
    assert kevin["metadata"]["sensor_instance_id"] != bre["metadata"]["sensor_instance_id"]


def test_chunk12_timing_sensor_uses_chart_and_time_window():
    package = {
        "metadata": {"analysis_type": "transit_range_dataset", "target_chart_id": "natal:kevin"},
        "period": {"start_date": "2026-01-01", "end_date": "2027-07-01"},
        "semantic_graph": sample_graph(),
        "theme_metrics": [],
        "evidence_graph": [],
        "report_materials": {},
    }
    result = finalize_package_semantic_boundary(package)
    assert result["metadata"]["sensor_instance_id"] == "transit:natal:kevin:2026-01-01:2027-07-01"


def test_chunk12_source_chart_family_links_same_chart_across_sensors():
    natal = {
        "metadata": {"analysis_type": "natal_dataset", "person": "Kevin"},
        "semantic_graph": sample_graph(),
    }
    transit = {
        "metadata": {"analysis_type": "transit_range_dataset", "target_chart_id": "natal:kevin"},
        "period": {"start_date": "2026-01-01", "end_date": "2026-02-01"},
        "semantic_graph": sample_graph(),
    }
    a = finalize_package_semantic_boundary(natal)
    b = finalize_package_semantic_boundary(transit)
    ea = a["canonical_astrology_graph"]["objects"][0]["evidence_metadata"]
    eb = b["canonical_astrology_graph"]["objects"][0]["evidence_metadata"]
    assert ea["evidence_family_group"] != eb["evidence_family_group"]
    assert ea["source_chart_family_group"] == eb["source_chart_family_group"]


def test_chunk13_synthetic_rows_receive_source_chart_ids_and_real_family_groups():
    package = {
        "metadata": {
            "analysis_type": "annual_profections_dataset",
            "target_chart_id": "natal:kevin",
            "target_date": "2026-07-07",
        },
        "target": {
            "chart_identity": {
                "chart_id": "natal:kevin",
                "chart_type": "natal",
                "label": "Kevin",
            }
        },
        "profection": {"target_date": "2026-07-07", "house": 9},
        "report_materials": {},
    }
    result = finalize_package_semantic_boundary(package)
    rows = (
        result["canonical_astrology_graph"]["objects"]
        + result["canonical_astrology_graph"]["relationships"]
    )
    assert rows
    for row in rows:
        evidence = row["evidence_metadata"]
        assert evidence["source_chart_ids"] == ["natal:kevin"]
        assert evidence["source_chart_family_group"].startswith("natal:kevin:")
        assert "source_chart_unknown" not in evidence["source_chart_family_group"]


def test_chunk13_synastry_synthetic_rows_receive_both_source_chart_ids():
    package = {
        "metadata": {
            "analysis_type": "synastry_relationship_dataset",
            "person_a": "Kevin",
            "person_b": "Bre",
        },
        "person_a": {"metadata": {"person": "Kevin", "source_chart_id": "natal:kevin"}},
        "person_b": {"metadata": {"person": "Bre", "source_chart_id": "natal:bre"}},
        "object_registries": {
            "person_a": {
                "natal:Mars": {"id": "natal:Mars", "name": "Mars", "object_type": "planet_or_point"}
            },
            "person_b": {
                "natal:Venus": {"id": "natal:Venus", "name": "Venus", "object_type": "planet_or_point"}
            },
        },
        "natal_synastry": {
            "a_to_b_aspects": [{
                "id": "syn:1",
                "relationship_type": "SYNASTRY_ASPECT",
                "source_object_id": "natal:Mars",
                "target_object_id": "natal:Venus",
                "aspect": "square",
                "orb": 0.5,
            }],
            "b_to_a_aspects": [],
            "a_to_b_house_overlays": [],
            "b_to_a_house_overlays": [],
        },
        "relationship_metrics": [],
        "evidence_graph": [],
        "report_materials": {},
    }
    result = finalize_package_semantic_boundary(package)
    expected = ["natal:kevin", "natal:bre"]
    rows = (
        result["canonical_astrology_graph"]["objects"]
        + result["canonical_astrology_graph"]["relationships"]
    )
    assert rows
    assert all(row["evidence_metadata"]["source_chart_ids"] == expected for row in rows)
    assert all(
        row["evidence_metadata"]["source_chart_family_group"].startswith(
            "natal:kevin+natal:bre:"
        )
        for row in rows
    )


def test_chunk13_old_full_transit_analysis_type_normalizes_to_public_sensor_id():
    package = {
        "metadata": {
            "analysis_type": "transit_period_dataset",
            "target_chart_id": "natal:kevin",
            "start_date": "2026-01-01",
            "end_date": "2026-02-01",
        },
        "period": {"start_date": "2026-01-01", "end_date": "2026-02-01"},
        "semantic_graph": sample_graph(),
        "theme_metrics": [],
        "evidence_graph": [],
        "report_materials": {},
    }
    result = finalize_package_semantic_boundary(package)
    assert result["metadata"]["sensor_instance_id"] == (
        "transit:natal:kevin:2026-01-01:2026-02-01"
    )


def test_chunk14_final_materialization_is_idempotent():
    package = {
        "metadata": {"analysis_type": "natal_dataset", "person": "Example"},
        "semantic_graph": sample_graph(),
        "theme_metrics": [{"theme": "romance_affection", "score": 12.0}],
        "evidence_graph": [{"id": "claim:1", "claim": "Example", "confidence": 0.8}],
        "report_materials": {"recommended_sections": ["Example"]},
    }
    first = finalize_package_semantic_boundary(package)
    first_graph = json.dumps(first["canonical_astrology_graph"], sort_keys=True)
    second = finalize_package_semantic_boundary(first)
    assert json.dumps(second["canonical_astrology_graph"], sort_keys=True) == first_graph
    assert second["semantic_boundary"]["legacy_fields_dual_written"] is False
    assert second["semantic_boundary"]["legacy_removal_status"] == "completed_chunk1.5"
    assert "semantic_graph" not in second
    assert "theme_metrics" not in second
    assert "evidence_graph" not in second
    assert "report_materials" not in second

def test_chunk15_orthodox_row_adapter_keeps_canonical_clean():
    from astrology_graph_foundry.common.semantic_layers import orthodox_row_annotation
    row = {
        "id": "rel:1",
        "source_name": "Mars",
        "target_name": "Venus",
        "aspect": "square",
        "operator_hints": [{"operator": "stress"}],
    }
    projected = orthodox_row_annotation(row)
    assert "growth_edge" in projected["theme_tags"]
    assert projected["semantic_operator_hints"][0]["operator"] == "stress"
    assert "theme_tags" not in row


def test_chunk15_analysis_view_omits_full_projection_view():
    from astrology_graph_foundry.pipelines.natal import analysis_view
    package = finalize_package_semantic_boundary({
        "metadata": {"analysis_type": "natal_dataset", "person": "Example"},
        "person": "Example",
        "natal": {"bodies": {}, "houses": {}, "angles": {}, "lots": {}, "sect": {}},
        "semantic_graph": sample_graph(),
        "theme_metrics": [{"theme": "growth_edge", "score": 1.0}],
        "evidence_graph": [],
        "report_materials": {},
    })
    view = analysis_view(package)
    assert "projection_views" not in view
    assert "orthodox_projection_extract" in view
    assert view["top_relationships"][0]["theme_tags"]

def test_chunk15_projection_view_survives_refinalization():
    package = {
        "metadata": {"analysis_type": "natal_dataset", "person": "Example"},
        "semantic_graph": sample_graph(),
        "theme_metrics": [{"theme": "growth_edge", "score": 3.0}],
        "evidence_graph": [{"id": "claim:1", "claim": "Example", "confidence": 0.7}],
        "report_materials": {"recommended_sections": ["Example"]},
    }
    first = finalize_package_semantic_boundary(package)
    before = json.dumps(
        first["projection_views"]["orthodox_astrology.v1"],
        sort_keys=True,
    )
    second = finalize_package_semantic_boundary(first)
    after = json.dumps(
        second["projection_views"]["orthodox_astrology.v1"],
        sort_keys=True,
    )
    assert after == before
    assert second["projection_views"]["orthodox_astrology.v1"]["theme_metrics"]
