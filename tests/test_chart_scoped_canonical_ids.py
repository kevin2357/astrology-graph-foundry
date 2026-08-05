from copy import deepcopy

from astrology_graph_foundry.common.semantic_layers import (
    finalize_package_semantic_boundary,
    rescope_natal_package_source_chart_id,
)


def _package(person: str):
    return {
        "metadata": {"analysis_type": "natal_dataset", "person": person},
        "semantic_graph": {
            "objects": [
                {
                    "id": "natal:Moon",
                    "name": "Moon",
                    "source_key": "nMoon",
                    "object_type": "planet_or_point",
                    "facts": {},
                    "transit_target": True,
                },
                {
                    "id": "antiscia_point:natal_Moon",
                    "name": "Moon antiscia point",
                    "source_key": "nMoon:antiscia_point",
                    "object_type": "antiscia_point",
                    "facts": {"owner_id": "natal:Moon"},
                    "transit_target": True,
                },
            ],
            "relationships": [
                {
                    "id": "rel:legacy",
                    "relationship_type": "HAS_ANTISCIA_POINT",
                    "source_id": "natal:Moon",
                    "target_id": "antiscia_point:natal_Moon",
                }
            ],
            "indexes": {
                "objects_by_id": {"natal:Moon": 0, "antiscia_point:natal_Moon": 1},
                "relationships_by_object_id": {
                    "natal:Moon": [0],
                    "antiscia_point:natal_Moon": [0],
                },
            },
        },
    }


def _explicit_package(person: str, source_chart_id: str):
    package = _package(person)
    package["metadata"]["source_chart_id"] = source_chart_id
    package["reference_registry"] = {
        "natal:Moon": {
            "object_ref": "natal:Moon",
            "derived_ref": "antiscia_point:natal_Moon",
            "relationship_ref": "rel:legacy",
        }
    }
    package["claims"] = [
        {
            "claim_id": "claim:moon",
            "evidence_refs": ["natal:Moon", "rel:legacy"],
            "operator": {"source_object_ref": "natal:Moon"},
        }
    ]
    package["projection_views"] = {
        "custom.v1": {
            "rows": [
                {
                    "relationship_type": "HAS_ANTISCIA_POINT",
                    "source_id": "natal:Moon",
                    "target_id": "antiscia_point:natal_Moon",
                }
            ]
        }
    }
    return package


def _all_strings_and_keys(value):
    found = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, list):
        for item in value:
            found.extend(_all_strings_and_keys(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            found.append(str(key))
            found.extend(_all_strings_and_keys(item))
    return found


def test_canonical_natal_ids_are_scoped_by_source_chart_and_refs_are_rewritten():
    kevin = finalize_package_semantic_boundary(_package("Kevin"))
    ashley = finalize_package_semantic_boundary(_package("Ashley"))

    kg = kevin["canonical_astrology_graph"]
    ag = ashley["canonical_astrology_graph"]
    k_ids = {obj["id"] for obj in kg["objects"]}
    a_ids = {obj["id"] for obj in ag["objects"]}

    assert "natal:kevin:Moon" in k_ids
    assert "natal:ashley:Moon" in a_ids
    assert k_ids.isdisjoint(a_ids)
    assert kg["source_chart_id"] == "natal:kevin"
    assert ag["source_chart_id"] == "natal:ashley"

    k_rel = kg["relationships"][0]
    assert k_rel["source_id"] == "natal:kevin:Moon"
    assert k_rel["target_id"].startswith("natal:kevin:")
    assert kg["indexes"]["objects_by_id"]["natal:kevin:Moon"] == 0
    derived = next(obj for obj in kg["objects"] if obj["object_type"] == "antiscia_point")
    assert derived["facts"]["owner_id"] == "natal:kevin:Moon"


def test_scoping_is_idempotent():
    package = finalize_package_semantic_boundary(_package("Kevin"))
    first = deepcopy(package["canonical_astrology_graph"])
    finalize_package_semantic_boundary(package)
    assert package["canonical_astrology_graph"] == first


def test_same_name_with_different_explicit_ids_has_disjoint_canonical_ids():
    first = finalize_package_semantic_boundary(_explicit_package("Scout", "astrowoof:dog:A"))
    second = finalize_package_semantic_boundary(_explicit_package("Scout", "astrowoof:dog:B"))

    first_ids = {obj["id"] for obj in first["canonical_astrology_graph"]["objects"]}
    second_ids = {obj["id"] for obj in second["canonical_astrology_graph"]["objects"]}

    assert first_ids.isdisjoint(second_ids)
    assert all(value.startswith("astrowoof:dog:A:") for value in first_ids)
    assert all(value.startswith("astrowoof:dog:B:") for value in second_ids)


def test_display_name_change_preserves_ids_with_explicit_identity():
    first = finalize_package_semantic_boundary(_explicit_package("Scout", "astrowoof:dog:A"))
    second = finalize_package_semantic_boundary(_explicit_package("Scout Renamed", "astrowoof:dog:A"))

    first_graph = first["canonical_astrology_graph"]
    second_graph = second["canonical_astrology_graph"]
    assert [obj["id"] for obj in first_graph["objects"]] == [obj["id"] for obj in second_graph["objects"]]
    assert [rel["id"] for rel in first_graph["relationships"]] == [rel["id"] for rel in second_graph["relationships"]]


def test_explicit_identity_rescope_rewrites_all_exact_references_without_prefix_stacking():
    package = finalize_package_semantic_boundary(_explicit_package("Scout", "astrowoof:dog:A"))
    package["person"] = {"source_chart_id": "astrowoof:dog:A"}
    package["natal"] = {"source_chart_id": "astrowoof:dog:A"}
    package["transitable_chart"] = {
        "chart_identity": {"chart_id": "astrowoof:dog:A"}
    }
    old_graph = deepcopy(package["canonical_astrology_graph"])
    old_ids = {
        *(obj["id"] for obj in old_graph["objects"]),
        *(rel["id"] for rel in old_graph["relationships"]),
        "astrowoof:dog:A",
    }

    migrated = rescope_natal_package_source_chart_id(package, "astrowoof:dog:B")
    graph = migrated["canonical_astrology_graph"]
    all_values = set(_all_strings_and_keys(migrated))

    assert graph["source_chart_id"] == "astrowoof:dog:B"
    assert graph["source_chart_ids"] == ["astrowoof:dog:B"]
    assert graph["identity_policy"]["source_chart_id"] == "astrowoof:dog:B"
    assert all(value.startswith("astrowoof:dog:B:") for value in (obj["id"] for obj in graph["objects"]))
    assert not any("astrowoof:dog:B:astrowoof:dog:A:" in value for value in all_values)
    assert old_ids.isdisjoint(all_values)
    assert not any("source_astrowoof_dog_a" in value for value in all_values)
    assert migrated["person"]["source_chart_id"] == "astrowoof:dog:B"
    assert migrated["natal"]["source_chart_id"] == "astrowoof:dog:B"
    assert migrated["transitable_chart"]["chart_identity"]["chart_id"] == "astrowoof:dog:B"
    assert set(graph["indexes"]["objects_by_id"]) == {obj["id"] for obj in graph["objects"]}
    assert graph["relationships"][0]["source_id"] in graph["indexes"]["objects_by_id"]
    assert graph["relationships"][0]["target_id"] in graph["indexes"]["objects_by_id"]
    assert all(
        row["evidence_metadata"]["source_chart_ids"] == ["astrowoof:dog:B"]
        for row in [*graph["objects"], *graph["relationships"]]
    )

    first_migration = deepcopy(migrated)
    finalize_package_semantic_boundary(migrated)
    assert migrated == first_migration


def test_conflicting_explicit_identity_carriers_fail_closed():
    package = _explicit_package("Scout", "astrowoof:dog:A")
    package["natal"] = {"source_chart_id": "astrowoof:dog:B"}

    try:
        finalize_package_semantic_boundary(package)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected conflicting source chart identities to fail")

    assert "Conflicting explicit source chart identities" in message
    assert "metadata.source_chart_id" in message
    assert "natal.source_chart_id" in message


def test_equal_explicit_identity_carriers_are_accepted():
    package = _explicit_package("Scout", "astrowoof:dog:A")
    package["natal"] = {"source_chart_id": "astrowoof:dog:A"}
    package["person"] = {"source_chart_id": "astrowoof:dog:A"}

    result = finalize_package_semantic_boundary(package)

    assert result["canonical_astrology_graph"]["source_chart_id"] == "astrowoof:dog:A"
    assert result["metadata"]["semantic_identity_version"] == "semantic_sensor_identity_v1.1.0"


def test_trailing_namespace_delimiter_is_preserved_without_double_separator():
    result = finalize_package_semantic_boundary(_explicit_package("Scout", "tenant:"))
    graph = result["canonical_astrology_graph"]

    assert graph["source_chart_id"] == "tenant:"
    assert all(obj["id"].startswith("tenant:") for obj in graph["objects"])
    assert all(not obj["id"].startswith("tenant::") for obj in graph["objects"])
