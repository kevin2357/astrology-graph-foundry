from __future__ import annotations

from datetime import datetime
from typing import Any

from astrology_graph_foundry.calculation_provenance import (
    build_bounded_calculation_provenance,
)
from astrology_graph_foundry.common.identity import source_chart_id_from_natal_package
from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary
from astrology_graph_foundry.ephemeris.live_natal import evaluate_bounded_natal_interval
from astrology_graph_foundry.ephemeris.models import BoundedBirthData, ProviderConfig

BOUNDED_NATAL_SCHEMA_VERSION = "1.0.0"
BOUNDED_GRAPH_VERSION = "1.0.0"


def _body_id(name: str) -> str:
    # Use the Foundry-local natal namespace so the shared finalizer performs the
    # same source_chart_id scoping and reference migration as exact Natal graphs.
    return f"natal:bounded:{name.replace(' ', '_')}"


def _relationship_id(first: str, second: str, aspect: str) -> str:
    return f"bounded_aspect:{first.replace(' ', '_')}:{aspect}:{second.replace(' ', '_')}"


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
        if evidence.get("classification") != "invariant" or len(signs) != 1 or motion.get("classification") != "invariant":
            continue
        dignity = evidence.get("sign_dignity")
        objects.append(
            {
                "id": _body_id(name),
                "name": name,
                "source_key": f"n{name}",
                "object_type": "bounded_natal_body",
                "sign_index": signs[0],
                "motion_state": motion["possible_states"][0],
                "sign_dignity": dignity,
                "uncertainty_evidence_ref": f"uncertainty:bodies:{name}",
                "transit_target": False,
                "source_operator_hints": ["bounded_categorical_placement"],
            }
        )
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

    feature_dispositions = {
        "houses": "unavailable_birth_time_dependent",
        "house_placements": "unavailable_birth_time_dependent",
        "angles": "unavailable_birth_time_dependent",
        "sect": "unavailable_birth_time_dependent",
        "lots": "unavailable_angle_or_sect_dependent",
        "declinations": "deferred_interval_semantics",
        "declination_aspects": "deferred_interval_semantics",
        "antiscia": "deferred_interval_semantics",
        "harmonics": "deferred_interval_semantics",
        "fixed_stars": "deferred_interval_semantics",
        "aspect_strength": "deferred_interval_semantics",
        "aspect_application": "deferred_interval_semantics",
        "representative_longitudes": "prohibited_precision_laundering",
    }
    evidence_registry = {
        **{f"uncertainty:bodies:{name}": evidence for name, evidence in sorted(assessment["bodies"].items())},
        **{f"uncertainty:aspects:{row['a']}:{row['b']}": row for row in assessment["aspects"]},
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
            "created_at": datetime.now().isoformat(timespec="seconds"),
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
        },
        "uncertainty_assessment": {
            "status": assessment["status"],
            "proof_profile": assessment["proof_profile"],
            "interval": assessment["interval"],
            "evaluation_count": assessment["evaluation_count"],
            "failures": assessment["failures"],
            "body_evidence": assessment["bodies"],
            "aspect_evidence": assessment["aspects"],
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
