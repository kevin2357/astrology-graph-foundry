from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from astrology_graph_foundry.ephemeris import bounded_natal
from astrology_graph_foundry.ephemeris.models import BirthTimeBasis, BoundedBirthData, ProviderConfig

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "src" / "astrology_graph_foundry" / "schemas"


def _birth(name="Scout", source_chart_id="astrowoof:dog:scout"):
    return BoundedBirthData(
        name=name,
        birth_time_basis=BirthTimeBasis(mode="bounded", earliest_local="2020-05-17T08:00:00", latest_local="2020-05-17T14:00:00"),
        birth_timezone="America/Denver",
        birth_lat=39.7392,
        birth_lon=-104.9903,
        source_chart_id=source_chart_id,
    )


def _assessment():
    stable = {
        "classification": "invariant",
        "longitude_range": {"unwrapped_min": 10.0, "unwrapped_max": 10.5, "possible_sign_indexes": [0]},
        "motion": {"classification": "invariant", "possible_states": ["direct"], "speed_min": 0.9, "speed_max": 1.1},
        "sign_dignity": {"classification": "invariant", "sign": "Aries", "sect_dependent_components": "unavailable"},
        "sample_count": 361,
    }
    variable = deepcopy(stable)
    variable.update(
        {
            "classification": "variable",
            "longitude_range": {"unwrapped_min": 29.0, "unwrapped_max": 31.0, "possible_sign_indexes": [0, 1]},
            "sign_dignity": None,
        }
    )
    return {
        "proof_profile": {"version": "agf.interval_proof.v1.0.0", "minimum_step_seconds": 60},
        "interval": {"start_jd": 1.0, "end_jd": 1.25, "boundary_policy": "inclusive"},
        "evaluation_count": 361,
        "status": "complete",
        "failures": [],
        "bodies": {"Sun": stable, "Moon": variable, "Mars": deepcopy(stable)},
        "aspects": [
            {
                "a": "Sun",
                "b": "Mars",
                "classification": "invariant",
                "aspect": "trine",
                "possible_aspects": ["trine"],
                "orb_range": {"min": 0.1, "max": 0.7},
            },
            {"a": "Sun", "b": "Moon", "classification": "conditional", "aspect": None, "possible_aspects": ["square"], "orb_range": None},
        ],
    }


def _build(monkeypatch, **birth_kwargs):
    monkeypatch.setattr(bounded_natal, "evaluate_bounded_natal_interval", lambda birth, config: deepcopy(_assessment()))
    return bounded_natal.build_bounded_natal_package(_birth(**birth_kwargs), ProviderConfig(ephemeris_mode="moshier"))


def _registry():
    registry = Registry()
    for path in SCHEMA_DIR.glob("*.schema.json"):
        registry = registry.with_resource(path.name, Resource.from_contents(json.loads(path.read_text(encoding="utf-8"))))
    return registry


def test_bounded_package_is_schema_valid_and_precision_safe(monkeypatch):
    package = _build(monkeypatch)
    schema = json.loads((SCHEMA_DIR / "bounded_natal_dataset_v1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, registry=_registry()).validate(package)
    assert package["metadata"]["created_at"].endswith("+00:00")
    provenance = package["metadata"]["calculation_provenance"]
    assert "evidence_contract_version" not in provenance["source_input"]
    assert provenance["calculation_profile_version"] == "agf.bounded_natal.calculation_profile.v1.4.0"
    assert provenance["calculation_profile"]["evidence_contract_version"] == "agf.bounded_uncertainty_evidence.v1.0.0"
    assert provenance["calculation_profile"]["bounded_feature_policy"]["harmonics"]["numbers"] == [2, 3, 4, 5, 7, 9]
    graph = package["canonical_astrology_graph"]
    assert graph["graph_type"] == "bounded_canonical_astrology_graph"
    assert graph["graph_version"] == "1.2.0"
    assert {row["name"] for row in graph["objects"]} == {"Sun", "Mars"}
    assert len(graph["relationships"]) == 1
    assert all(not ({"longitude", "pretty", "sign_degree"} & row.keys()) for row in graph["objects"])
    assert all(not ({"orb", "distance", "strength"} & row.keys()) for row in graph["relationships"])
    assert package["uncertainty_assessment"]["body_evidence"]["Moon"]["classification"] == "variable"
    registry = package["uncertainty_assessment"]["evidence_registry"]
    assert all(row["uncertainty_evidence_ref"] in registry for row in graph["objects"] + graph["relationships"])


def test_reduced_capabilities_and_feature_dispositions_are_explicit(monkeypatch):
    package = _build(monkeypatch)
    assert package["capabilities"]["supports_exact_longitudes"] is False
    assert package["capabilities"]["supports_semantic_graph_activation"] is False
    dispositions = package["uncertainty_assessment"]["feature_dispositions"]
    assert dispositions["houses"] == "unavailable_birth_time_dependent"
    assert dispositions["representative_longitudes"] == "prohibited_precision_laundering"
    assert dispositions["declinations"] == "assessed_as_continuous_ranges"
    assert package["capabilities"]["supports_bounded_body_coordinate_evidence"] is True
    assert package["capabilities"]["supports_bounded_declination_evidence"] is True


def test_ids_are_deterministic_scoped_and_display_name_independent(monkeypatch):
    first = _build(monkeypatch, name="Scout")
    renamed = _build(monkeypatch, name="Scout II")
    first_ids = [row["id"] for row in first["canonical_astrology_graph"]["objects"]]
    assert first_ids == [row["id"] for row in renamed["canonical_astrology_graph"]["objects"]]
    assert all(value.startswith("astrowoof:dog:scout:") for value in first_ids)
    endpoints = set(first_ids)
    assert all(
        row["source_id"] in endpoints and row["target_id"] in endpoints for row in first["canonical_astrology_graph"]["relationships"]
    )


def test_repeated_finalization_is_idempotent(monkeypatch):
    from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary

    package = _build(monkeypatch)
    before = json.dumps(package["canonical_astrology_graph"], sort_keys=True)
    finalize_package_semantic_boundary(package)
    assert json.dumps(package["canonical_astrology_graph"], sort_keys=True) == before


def test_pre_generalized_bounded_artifact_remains_schema_valid(monkeypatch):
    package = _build(monkeypatch)
    package["canonical_astrology_graph"]["graph_version"] = "1.0.0"
    assessment = package["uncertainty_assessment"]
    assessment.pop("evidence_contract_version", None)
    for row in list(assessment["body_evidence"].values()) + list(assessment["aspect_evidence"]):
        row.pop("evidence", None)
    provenance = package["metadata"]["calculation_provenance"]
    provenance["calculation_profile_version"] = "agf.bounded_natal.calculation_profile.v1.0.0"
    provenance["calculation_profile"]["profile_version"] = "agf.bounded_natal.calculation_profile.v1.0.0"
    provenance["calculation_profile"].pop("evidence_contract_version", None)
    schema = json.loads((SCHEMA_DIR / "bounded_natal_dataset_v1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, registry=_registry()).validate(package)


def test_invariant_transforms_materialize_without_exact_longitudes_and_keep_owner_lineage(monkeypatch):
    assessment = _assessment()
    assessment["bodies"]["Sun"]["transforms"] = {
        "antiscia": {
            "classification": "invariant",
            "possible_sign_indexes": [5],
            "evidence": {"feature_key": "body:Sun:transform:antiscia"},
        },
        "contra_antiscia": {
            "classification": "variable",
            "possible_sign_indexes": [5, 6],
            "evidence": {"feature_key": "body:Sun:transform:contra_antiscia"},
        },
        "harmonics": {
            "3": {
                "classification": "invariant",
                "possible_sign_indexes": [1],
                "evidence": {"feature_key": "body:Sun:transform:harmonic:3"},
            },
            "9": {
                "classification": "variable",
                "possible_sign_indexes": list(range(12)),
                "evidence": {"feature_key": "body:Sun:transform:harmonic:9"},
            },
        },
    }
    assessment["derived_aspects"] = [
        {
            "a": "body:Sun",
            "b": "transform:Sun:harmonic:3",
            "a_name": "Sun",
            "b_name": "Sun harmonic 3",
            "classification": "invariant",
            "aspect": "square",
            "evidence": {"feature_key": "derived_aspect:body:Sun:transform:Sun:harmonic:3"},
        }
    ]
    assessment["declination_relationships"] = [
        {
            "a": "Sun",
            "b": "Mars",
            "classification": "invariant",
            "relationship": "parallel",
            "evidence": {"feature_key": "declination_relationship:Sun:Mars"},
        }
    ]
    monkeypatch.setattr(bounded_natal, "evaluate_bounded_natal_interval", lambda birth, config: deepcopy(assessment))
    package = bounded_natal.build_bounded_natal_package(_birth(), ProviderConfig(ephemeris_mode="moshier"))
    graph = package["canonical_astrology_graph"]
    derived = [row for row in graph["objects"] if row["object_type"] != "bounded_natal_body"]
    assert {row["object_type"] for row in derived} == {"bounded_antiscia_point", "bounded_harmonic_point"}
    assert all("longitude" not in row and "motion_state" not in row for row in derived)
    object_ids = {row["id"] for row in graph["objects"]}
    assert all(row["owner_object_ref"] in object_ids for row in derived)
    owner_relationships = [row for row in graph["relationships"] if row["relationship_type"].startswith("BOUNDED_HAS_")]
    assert len(owner_relationships) == 2
    assert all(row["source_id"] in object_ids and row["target_id"] in object_ids for row in owner_relationships)
    assert all(row["uncertainty_evidence_ref"] in package["uncertainty_assessment"]["evidence_registry"] for row in derived)
    invariant_relationship_types = {row["relationship_type"] for row in graph["relationships"]}
    assert "BOUNDED_INVARIANT_DERIVED_ASPECT" in invariant_relationship_types
    assert "BOUNDED_INVARIANT_DECLINATION_PARALLEL" in invariant_relationship_types
    assert all(
        "orb" not in row and "applying_delta" not in row
        for row in graph["relationships"]
        if row["relationship_type"].startswith("BOUNDED_INVARIANT_")
    )
    schema = json.loads((SCHEMA_DIR / "bounded_natal_dataset_v1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, registry=_registry()).validate(package)


def test_transform_configuration_changes_bounded_configuration_identity(monkeypatch):
    monkeypatch.setattr(bounded_natal, "evaluate_bounded_natal_interval", lambda birth, config: deepcopy(_assessment()))
    default = bounded_natal.build_bounded_natal_package(_birth(), ProviderConfig(ephemeris_mode="moshier"))
    changed = bounded_natal.build_bounded_natal_package(
        _birth(),
        ProviderConfig(ephemeris_mode="moshier", harmonic_numbers=(3, 5)),
    )
    disabled = bounded_natal.build_bounded_natal_package(
        _birth(),
        ProviderConfig(ephemeris_mode="moshier", include_antiscia=False, include_harmonics=False),
    )
    hashes = {
        row["metadata"]["calculation_provenance"]["configuration_sha256"]
        for row in (default, changed, disabled)
    }
    assert len(hashes) == 3
