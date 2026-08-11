from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from astrology_graph_foundry.calculation_provenance import (
    build_bounded_calculation_provenance,
)
from astrology_graph_foundry.common.identity import source_chart_id_from_natal_package
from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary
from astrology_graph_foundry.ephemeris.live_natal import evaluate_bounded_natal_interval
from astrology_graph_foundry.ephemeris.models import BoundedBirthData, ProviderConfig

BOUNDED_NATAL_SCHEMA_VERSION = "1.0.0"
BOUNDED_GRAPH_VERSION = "1.7.0"


def _body_id(name: str) -> str:
    # Use the Foundry-local natal namespace so the shared finalizer performs the
    # same source_chart_id scoping and reference migration as exact Natal graphs.
    return f"natal:bounded:{name.replace(' ', '_')}"


def _relationship_id(first: str, second: str, aspect: str) -> str:
    return f"bounded_aspect:{first.replace(' ', '_')}:{aspect}:{second.replace(' ', '_')}"


def _transform_id(name: str, kind: str, qualifier: str | None = None) -> str:
    suffix = f":{qualifier}" if qualifier is not None else ""
    return f"natal:bounded:{name.replace(' ', '_')}:{kind}{suffix}"


def _transform_evidence_ref(name: str, kind: str, qualifier: str | None = None) -> str:
    suffix = f":{qualifier}" if qualifier is not None else ""
    return f"uncertainty:transforms:{name}:{kind}{suffix}"


def _coordinate_node_id(key: str) -> str:
    parts = key.split(":")
    if parts[0] == "body" and len(parts) == 2:
        return _body_id(parts[1])
    if parts[0] == "transform" and len(parts) >= 3:
        qualifier = parts[3] if len(parts) == 4 else None
        return _transform_id(parts[1], parts[2], qualifier)
    if parts[0] == "calculated_point" and len(parts) == 2:
        return _calculated_point_id(parts[1])
    raise ValueError(f"unsupported bounded coordinate node key: {key}")


def _angle_id(name: str) -> str:
    return f"natal:bounded:angle:{name}"


def _calculated_point_id(name: str) -> str:
    return f"natal:bounded:calculated_point:{name}"


def _cusp_id(number: int) -> str:
    return f"natal:bounded:house_cusp:{number}"


def _invariant_house(assessment: dict[str, Any], key: str) -> tuple[int, str] | None:
    evidence = ((assessment.get("terrestrial_frame") or {}).get("house_memberships") or {}).get(key) or {}
    values = (evidence.get("possibilities") or {}).get("values") or []
    if evidence.get("classification") != "invariant" or len(values) != 1:
        return None
    return int(values[0]), f"uncertainty:terrestrial_frame:house_membership:{key}"


def build_bounded_natal_package(
    birth: BoundedBirthData,
    config: ProviderConfig | None = None,
) -> dict[str, Any]:
    config = config or ProviderConfig()
    assessment = evaluate_bounded_natal_interval(birth, config)
    provisional = {"metadata": {"analysis_type": "bounded_natal_dataset"}, "natal": {}, "person": {}}
    source_chart_id = birth.source_chart_id or source_chart_id_from_natal_package(provisional, fallback_name=birth.name)

    objects = []
    for name, evidence in sorted(assessment["bodies"].items()):
        sign_range = evidence.get("longitude_range") or {}
        signs = sign_range.get("possible_sign_indexes") or []
        motion = evidence.get("motion") or {}
        invariant_house = _invariant_house(assessment, f"body:{name}")
        invariant_sign = len(signs) == 1
        invariant_motion = motion.get("classification") == "invariant" and len(motion.get("possible_states") or []) == 1
        if not ((invariant_sign and invariant_motion) or invariant_house is not None):
            continue
        dignity = evidence.get("sign_dignity")
        object_row = {
                "id": _body_id(name),
                "name": name,
                "source_key": f"n{name}",
                "object_type": "bounded_natal_body",
                **({"sign_index": signs[0]} if invariant_sign else {}),
                **({"motion_state": motion["possible_states"][0]} if invariant_motion else {}),
                **({"sign_dignity": dignity} if dignity is not None else {}),
                "uncertainty_evidence_ref": f"uncertainty:bodies:{name}",
                "transit_target": False,
                "source_operator_hints": ["bounded_categorical_placement"],
            }
        if invariant_house is not None:
            object_row["house_number"], object_row["house_uncertainty_evidence_ref"] = invariant_house
        triplicity = (assessment.get("sect_triplicity") or {}).get(name) or {}
        triplicity_values = (triplicity.get("possibilities") or {}).get("values") or []
        if triplicity.get("classification") == "invariant" and len(triplicity_values) == 1:
            object_row["triplicity_ruler"] = triplicity_values[0]
            object_row["triplicity_uncertainty_evidence_ref"] = f"uncertainty:sect_triplicity:{name}"
        objects.append(object_row)
    object_names = {row["name"] for row in objects}
    relationships = []
    for row in assessment["aspects"]:
        if row.get("classification") != "invariant" or not row.get("aspect"):
            continue
        if row["a"] not in object_names or row["b"] not in object_names:
            continue
        relationships.append(
            {
                "id": _relationship_id(row["a"], row["b"], row["aspect"]),
                "relationship_type": "BOUNDED_INVARIANT_ASPECT",
                "source_id": _body_id(row["a"]),
                "target_id": _body_id(row["b"]),
                "source_name": row["a"],
                "target_name": row["b"],
                "aspect": row["aspect"],
                "uncertainty_evidence_ref": f"uncertainty:aspects:{row['a']}:{row['b']}",
                "source_operator_hints": ["bounded_invariant_aspect"],
            }
        )

    for name in sorted(object_names):
        body_evidence = assessment["bodies"][name]
        transforms = body_evidence.get("transforms") or {}
        transform_rows = [
            ("antiscia", "bounded_antiscia_point", "BOUNDED_HAS_ANTISCIA_POINT", transforms.get("antiscia"), None),
            (
                "contra_antiscia",
                "bounded_contra_antiscia_point",
                "BOUNDED_HAS_CONTRA_ANTISCIA_POINT",
                transforms.get("contra_antiscia"),
                None,
            ),
        ]
        transform_rows.extend(
            ("harmonic", "bounded_harmonic_point", "BOUNDED_HAS_HARMONIC_POINT", row, number)
            for number, row in sorted((transforms.get("harmonics") or {}).items(), key=lambda item: int(item[0]))
        )
        for kind, object_type, relationship_type, transform, qualifier in transform_rows:
            signs = (transform or {}).get("possible_sign_indexes") or []
            membership_key = f"transform:{name}:{kind}{f':{qualifier}' if qualifier is not None else ''}"
            house = _invariant_house(assessment, membership_key)
            invariant_sign = (transform or {}).get("classification") == "invariant" and len(signs) == 1
            if not invariant_sign and house is None:
                continue
            transform_id = _transform_id(name, kind, qualifier)
            evidence_ref = _transform_evidence_ref(name, kind, qualifier)
            display_kind = f"harmonic {qualifier}" if qualifier is not None else kind.replace("_", " ")
            objects.append(
                {
                    "id": transform_id,
                    "name": f"{name} {display_kind}",
                    "source_key": f"n{name}:{kind}{f':{qualifier}' if qualifier is not None else ''}",
                    "object_type": object_type,
                    **({"sign_index": signs[0]} if invariant_sign else {}),
                    "owner_object_ref": _body_id(name),
                    "transform_kind": kind,
                    **({"harmonic_number": int(qualifier)} if qualifier is not None else {}),
                    "uncertainty_evidence_ref": evidence_ref,
                    "transit_target": False,
                    "source_operator_hints": ["bounded_coordinate_transform"],
                    **(
                        {
                            "house_number": house[0],
                            "house_uncertainty_evidence_ref": house[1],
                        }
                        if house
                        else {}
                    ),
                }
            )
            relationships.append(
                {
                    "id": f"bounded_transform_owner:{_body_id(name)}:{transform_id}",
                    "relationship_type": relationship_type,
                    "source_id": _body_id(name),
                    "target_id": transform_id,
                    "source_name": name,
                    "target_name": f"{name} {display_kind}",
                    "uncertainty_evidence_ref": evidence_ref,
                    "source_operator_hints": ["bounded_coordinate_transform_lineage"],
                }
            )

    frame = assessment.get("terrestrial_frame") or {}
    sect = frame.get("sect") or {}
    sect_values = (sect.get("possibilities") or {}).get("values") or []
    if sect.get("classification") == "invariant" and len(sect_values) == 1:
        objects.append({
            "id": "natal:bounded:sect",
            "name": f"{sect_values[0].title()} sect",
            "source_key": "sect",
            "object_type": "bounded_sect_state",
            "sect": sect_values[0],
            "uncertainty_evidence_ref": "uncertainty:terrestrial_frame:sect",
            "source_operator_hints": ["bounded_invariant_sect"],
        })
    for house_number, semantics in sorted((frame.get("cusp_semantics") or {}).items(), key=lambda item: int(item[0])):
        sign = semantics.get("sign") or {}
        sign_values = (sign.get("possibilities") or {}).get("values") or []
        if sign.get("classification") != "invariant" or len(sign_values) != 1:
            continue
        objects.append({
            "id": _cusp_id(int(house_number)),
            "name": f"House {house_number} cusp",
            "source_key": f"house:{house_number}",
            "object_type": "bounded_house_cusp",
            "house_number": int(house_number),
            "sign_index": ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces").index(sign_values[0]),
            "traditional_ruler": ((semantics["traditional_ruler"].get("possibilities") or {}).get("values") or [None])[0],
            "modern_ruler": ((semantics["modern_ruler"].get("possibilities") or {}).get("values") or [None])[0],
            "uncertainty_evidence_ref": f"uncertainty:terrestrial_frame:cusp_semantics:{house_number}:sign",
            "source_operator_hints": ["bounded_invariant_house_cusp"],
        })
    for angle_name in ("ASC", "DSC", "MC", "IC", "Vertex"):
        evidence = (frame.get("coordinates") or {}).get(f"angle:{angle_name}") or {}
        signs = (evidence.get("possibilities") or {}).get("values") or []
        if evidence.get("classification") != "invariant" or len(signs) != 1:
            continue
        angle_object = {
            "id": _angle_id(angle_name),
            "name": angle_name,
            "source_key": f"angle:{angle_name}",
            "object_type": "bounded_angle",
            "sign_index": int(signs[0]),
            "uncertainty_evidence_ref": f"uncertainty:terrestrial_frame:angle:{angle_name}",
            "source_operator_hints": ["bounded_invariant_angle_sign"],
        }
        invariant_house = _invariant_house(assessment, f"angle:{angle_name}")
        if invariant_house is not None:
            angle_object["house_number"], angle_object["house_uncertainty_evidence_ref"] = invariant_house
        objects.append(angle_object)
    for point_name, evidence in sorted((frame.get("calculated_points") or {}).items()):
        signs = evidence.get("possible_sign_indexes") or []
        invariant_sign = evidence.get("classification") == "invariant" and len(signs) == 1
        invariant_house = _invariant_house(assessment, f"calculated_point:{point_name}")
        if not invariant_sign and invariant_house is None:
            continue
        point_object = {
            "id": _calculated_point_id(point_name),
            "name": point_name,
            "source_key": f"calculated_point:{point_name}",
            "object_type": "bounded_calculated_point",
            **({"sign_index": signs[0]} if invariant_sign else {}),
            "possible_formula_ids": evidence.get("possible_formula_ids") or [],
            "uncertainty_evidence_ref": f"uncertainty:terrestrial_frame:calculated_point:{point_name}",
            "source_operator_hints": ["bounded_branched_calculated_point"],
        }
        if invariant_house is not None:
            point_object["house_number"], point_object["house_uncertainty_evidence_ref"] = invariant_house
        objects.append(point_object)

    canonical_object_ids = {row["id"] for row in objects}
    for row in frame.get("angle_relationships") or []:
        if row.get("classification") != "invariant" or not row.get("aspect"):
            continue
        source_id = _coordinate_node_id(row["a"])
        target_id = _angle_id(row["b"].split(":", 1)[1])
        if source_id not in canonical_object_ids or target_id not in canonical_object_ids:
            continue
        evidence_ref = f"uncertainty:terrestrial_frame:angle_relationship:{row['a']}:{row['b']}"
        relationships.append({
            "id": f"bounded_angle_aspect:{source_id}:{row['aspect']}:{target_id}",
            "relationship_type": "BOUNDED_INVARIANT_ANGLE_ASPECT",
            "source_id": source_id,
            "target_id": target_id,
            "source_name": row["a_name"],
            "target_name": row["b_name"],
            "aspect": row["aspect"],
            "uncertainty_evidence_ref": evidence_ref,
            "source_operator_hints": ["bounded_invariant_angle_aspect"],
        })
    for row in frame.get("calculated_point_relationships") or []:
        if row.get("classification") != "invariant" or not row.get("aspect"):
            continue
        source_id = _coordinate_node_id(row["a"])
        target_id = _coordinate_node_id(row["b"])
        if source_id not in canonical_object_ids or target_id not in canonical_object_ids:
            continue
        evidence_ref = f"uncertainty:terrestrial_frame:calculated_point_relationship:{row['a']}:{row['b']}"
        relationships.append({
            "id": f"bounded_calculated_point_aspect:{source_id}:{row['aspect']}:{target_id}",
            "relationship_type": "BOUNDED_INVARIANT_CALCULATED_POINT_ASPECT",
            "source_id": source_id,
            "target_id": target_id,
            "source_name": row["a_name"],
            "target_name": row["b_name"],
            "aspect": row["aspect"],
            "uncertainty_evidence_ref": evidence_ref,
            "source_operator_hints": ["bounded_invariant_calculated_point_aspect"],
        })
    for row in assessment.get("derived_aspects") or []:
        if row.get("classification") != "invariant" or not row.get("aspect"):
            continue
        source_id, target_id = _coordinate_node_id(row["a"]), _coordinate_node_id(row["b"])
        if source_id not in canonical_object_ids or target_id not in canonical_object_ids:
            continue
        evidence_ref = f"uncertainty:derived_aspects:{row['a']}:{row['b']}"
        relationships.append(
            {
                "id": f"bounded_derived_aspect:{source_id}:{row['aspect']}:{target_id}",
                "relationship_type": "BOUNDED_INVARIANT_DERIVED_ASPECT",
                "source_id": source_id,
                "target_id": target_id,
                "source_name": row["a_name"],
                "target_name": row["b_name"],
                "aspect": row["aspect"],
                "uncertainty_evidence_ref": evidence_ref,
                "source_operator_hints": ["bounded_invariant_derived_aspect"],
            }
        )
    for row in assessment.get("declination_relationships") or []:
        if row.get("classification") != "invariant" or not row.get("relationship"):
            continue
        source_id, target_id = _body_id(row["a"]), _body_id(row["b"])
        if source_id not in canonical_object_ids or target_id not in canonical_object_ids:
            continue
        evidence_ref = f"uncertainty:declination_relationships:{row['a']}:{row['b']}:{row['relationship']}"
        relationships.append(
            {
                "id": f"bounded_declination:{source_id}:{row['relationship']}:{target_id}",
                "relationship_type": (
                    "BOUNDED_INVARIANT_DECLINATION_PARALLEL"
                    if row["relationship"] == "parallel"
                    else "BOUNDED_INVARIANT_DECLINATION_CONTRAPARALLEL"
                ),
                "source_id": source_id,
                "target_id": target_id,
                "source_name": row["a"],
                "target_name": row["b"],
                "uncertainty_evidence_ref": evidence_ref,
                "source_operator_hints": ["bounded_invariant_declination_relationship"],
            }
        )

    feature_dispositions = {
        "houses": "assessed_as_terrestrial_frame_ranges",
        "house_placements": "assessed_with_invariant_house_promotion",
        "angles": "assessed_as_terrestrial_frame_ranges",
        "cusp_signs_and_rulers": "assessed_with_invariant_prerequisite_promotion",
        "angle_relationships": "assessed_with_invariant_relationship_promotion",
        "sect": "assessed_with_invariant_prerequisite_promotion",
        "lots": "assessed_as_branched_calculated_point_ranges",
        "optional_external_features": "explicitly_unavailable_without_qualified_data_profile",
        "body_latitudes": "assessed_as_continuous_ranges",
        "right_ascensions": "assessed_as_continuous_circular_ranges",
        "declinations": "assessed_as_continuous_ranges",
        "declination_aspects": "assessed_with_invariant_relationship_promotion",
        "antiscia": "assessed_with_invariant_sign_promotion",
        "harmonics": "assessed_with_invariant_sign_promotion",
        "fixed_stars": "deferred_interval_semantics",
        "aspect_strength": "deferred_interval_semantics",
        "aspect_application": "deferred_interval_semantics",
        "representative_longitudes": "prohibited_precision_laundering",
    }
    evidence_registry = {
        **{f"uncertainty:bodies:{name}": evidence for name, evidence in sorted(assessment["bodies"].items())},
        **{f"uncertainty:aspects:{row['a']}:{row['b']}": row for row in assessment["aspects"]},
        **{
            _transform_evidence_ref(name, kind): transform["evidence"]
            for name, body in sorted(assessment["bodies"].items())
            for kind, transform in (
                ("antiscia", (body.get("transforms") or {}).get("antiscia")),
                ("contra_antiscia", (body.get("transforms") or {}).get("contra_antiscia")),
            )
            if transform is not None
        },
        **(
            {"uncertainty:terrestrial_frame:sect": (assessment.get("terrestrial_frame") or {})["sect"]}
            if (assessment.get("terrestrial_frame") or {}).get("sect") is not None
            else {}
        ),
        **{
            f"uncertainty:sect_triplicity:{name}": evidence
            for name, evidence in sorted((assessment.get("sect_triplicity") or {}).items())
        },
        **{
            f"uncertainty:terrestrial_frame:cusp_semantics:{house}:{kind}": evidence
            for house, semantics in sorted((assessment.get("terrestrial_frame") or {}).get("cusp_semantics", {}).items())
            for kind, evidence in sorted(semantics.items())
        },
        **{
            f"uncertainty:terrestrial_frame:angle_relationship:{row['a']}:{row['b']}": row["evidence"]
            for row in (assessment.get("terrestrial_frame") or {}).get("angle_relationships", [])
        },
        **{
            f"uncertainty:terrestrial_frame:{key}": value
            for key, value in sorted((assessment.get("terrestrial_frame") or {}).get("coordinates", {}).items())
        },
        **{
            f"uncertainty:terrestrial_frame:calculated_point:{name}": value
            for name, value in sorted((assessment.get("terrestrial_frame") or {}).get("calculated_points", {}).items())
        },
        **{
            f"uncertainty:terrestrial_frame:calculated_point_relationship:{row['a']}:{row['b']}": row
            for row in (assessment.get("terrestrial_frame") or {}).get("calculated_point_relationships", [])
        },
        **{
            f"uncertainty:optional_external_feature:{name}": value
            for name, value in sorted((assessment.get("optional_external_features") or {}).items())
        },
        **{
            f"uncertainty:terrestrial_frame:house_membership:{key}": value
            for key, value in sorted((assessment.get("terrestrial_frame") or {}).get("house_memberships", {}).items())
        },
        **{
            f"uncertainty:derived_aspects:{row['a']}:{row['b']}": row["evidence"]
            for row in assessment.get("derived_aspects") or []
        },
        **{
            f"uncertainty:declination_relationships:{row['a']}:{row['b']}:{row['relationship']}": row["evidence"]
            for row in assessment.get("declination_relationships") or []
        },
        **{
            _transform_evidence_ref(name, "harmonic", number): transform["evidence"]
            for name, body in sorted(assessment["bodies"].items())
            for number, transform in sorted(
                (((body.get("transforms") or {}).get("harmonics") or {}).items()),
                key=lambda item: int(item[0]),
            )
        },
    }
    graph = {
        "graph_type": "bounded_canonical_astrology_graph",
        "graph_version": BOUNDED_GRAPH_VERSION,
        "graph_layer": "canonical_source_graph",
        "source_sensor_id": source_chart_id,
        "projection_status": "pre_projection",
        "identity_policy": {"object_id_scope": "source_chart_id", "source_chart_id": source_chart_id},
        "objects": objects,
        "relationships": relationships,
        "summary": {"object_count": len(objects), "relationship_count": len(relationships)},
        "capabilities": {
            "supports_bounded_categorical_placements": True,
            "supports_bounded_invariant_aspects": True,
            "supports_bounded_body_coordinate_evidence": True,
            "supports_bounded_declination_evidence": True,
            "supports_bounded_coordinate_transforms": True,
            "supports_bounded_derived_aspects": True,
            "supports_bounded_declination_relationships": True,
            "supports_bounded_terrestrial_frame_evidence": True,
            "supports_bounded_invariant_house_membership": True,
            "supports_bounded_invariant_cusp_semantics": True,
            "supports_bounded_invariant_angle_aspects": True,
            "supports_bounded_invariant_sect": True,
            "supports_bounded_invariant_triplicity": True,
            "supports_bounded_branched_calculated_points": True,
            "supports_exact_longitudes": False,
            "supports_longitude_aspects": False,
            "supports_house_transits": False,
            "supports_angle_transits": False,
            "supports_semantic_graph_activation": False,
            "supports_returns": False,
            "supports_annual_profections": False,
        },
    }
    package = {
        "metadata": {
            "schema_version": BOUNDED_NATAL_SCHEMA_VERSION,
            "analysis_type": "bounded_natal_dataset",
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "person": birth.name,
            "source_chart_id": source_chart_id,
            "provider": "live_swiss_ephemeris",
            "calculation_provenance": build_bounded_calculation_provenance(
                birth_data=birth,
                config=config,
                interval_assessment=assessment,
            ),
        },
        "person": {
            "person": birth.name,
            "source_chart_id": source_chart_id,
            "birth_timezone": birth.birth_timezone,
            "birth_lat": birth.birth_lat,
            "birth_lon": birth.birth_lon,
            "birth_location_label": birth.birth_location_label,
        },
        "birth_time_basis": birth.resolved_birth_time_basis.as_dict(),
        "bounded_natal": {
            "source_chart_id": source_chart_id,
            "bodies": {name: evidence for name, evidence in sorted(assessment["bodies"].items())},
            "aspects": assessment["aspects"],
            "derived_aspects": assessment.get("derived_aspects") or [],
            "derived_aspect_invariant_absence_count": assessment.get("derived_aspect_invariant_absence_count", 0),
            "declination_relationships": assessment.get("declination_relationships") or [],
            "terrestrial_frame": assessment.get("terrestrial_frame"),
            "calculated_points": (assessment.get("terrestrial_frame") or {}).get("calculated_points") or {},
            "optional_external_features": assessment.get("optional_external_features") or {},
        },
        "uncertainty_assessment": {
            **(
                {"evidence_contract_version": assessment["evidence_contract_version"]}
                if assessment.get("evidence_contract_version")
                else {}
            ),
            "status": assessment["status"],
            "proof_profile": assessment["proof_profile"],
            "interval": assessment["interval"],
            "evaluation_count": assessment["evaluation_count"],
            "failures": assessment["failures"],
            "body_evidence": assessment["bodies"],
            "aspect_evidence": assessment["aspects"],
            "derived_aspect_evidence": assessment.get("derived_aspects") or [],
            "declination_relationship_evidence": assessment.get("declination_relationships") or [],
            "terrestrial_frame_evidence": assessment.get("terrestrial_frame"),
            "optional_external_feature_evidence": assessment.get("optional_external_features") or {},
            "evidence_registry": evidence_registry,
            "feature_dispositions": feature_dispositions,
        },
        "capabilities": graph["capabilities"],
        "canonical_astrology_graph": graph,
    }
    finalized = finalize_package_semantic_boundary(package)
    finalized["metadata"]["canonical_graph_contract"] = "bounded_canonical_astrology_graph.v1"
    finalized["semantic_boundary"]["canonical_graph_contract"] = "bounded_canonical_astrology_graph.v1"
    finalized["semantic_boundary"]["bounded_birth_time"] = True
    return finalized
