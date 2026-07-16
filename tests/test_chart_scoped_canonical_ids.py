from copy import deepcopy

from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary


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
