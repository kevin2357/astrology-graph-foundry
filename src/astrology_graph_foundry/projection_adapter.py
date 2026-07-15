from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

from semantic_projection import (
    ProjectionContext,
    ProjectionOptions,
    ProjectionProfileRegistry,
    ProjectionRequest,
    project,
    projection_request_id,
    materialize_projected_graph,
    projection_summary_view as generic_projection_summary_view,
)
from semantic_projection.profiles import builtin_projection_registry as _external_builtin_projection_registry
from semantic_projection.profiles.orthodox_astrology.object_mappings import (
    OBJECT_MAPPINGS,
    canonical_object_name,
    house_number,
)

GENERAL_RELATIONSHIP_CONTEXT_ID = "orthodox.relationship.general.v1"


UNSUPPORTED_TEMPORAL_ACTIVATION_ANALYSIS_TYPES = frozenset({
    "transit_dataset",
    "transit_range_dataset",
    "transit_period_dataset",
})

class TemporalProjectionNotImplementedError(NotImplementedError):
    """Raised when a package requires a temporal-activation projection contract."""


def reject_unsupported_temporal_projection(source_package: dict[str, Any]) -> None:
    """Prevent static-chart projection from silently flattening timing packages.

    Transit packages contain a top-level target/radix graph plus nested temporal
    activations. Projecting only the top-level graph produces a plausible but
    misleading static result. Until ``projected_temporal_activation_graph.v1``
    is implemented, these packages must fail explicitly.
    """
    metadata = source_package.get("metadata") or {}
    analysis_type = str(metadata.get("analysis_type") or "")
    if analysis_type in UNSUPPORTED_TEMPORAL_ACTIVATION_ANALYSIS_TYPES:
        raise TemporalProjectionNotImplementedError(
            "Projection of temporal activation packages is not implemented. "
            f"analysis_type={analysis_type!r} contains nested transit/timing "
            "structures that cannot be represented faithfully by the static "
            "projected_semantic_graph.v1 contract. Use a static Natal, "
            "Synastry, Composite, Davison, or return-chart package, or wait for "
            "projected_temporal_activation_graph.v1."
        )
PROFESSIONAL_RELATIONSHIP_CONTEXT_ID = "orthodox.relationship.professional.v1"


def relationship_context(*, professional: bool = False) -> ProjectionContext:
    return ProjectionContext(
        context_id=(
            PROFESSIONAL_RELATIONSHIP_CONTEXT_ID
            if professional
            else GENERAL_RELATIONSHIP_CONTEXT_ID
        ),
        context_version="1.0.0",
        subject_scope="relationship",
        target_domain="orthodox_astrology.v1",
        application_context=(
            "professional_relationship"
            if professional
            else "relationship_interpretation"
        ),
        relationship_type="professional" if professional else "general",
        audience="adult_general",
        output_intent="structured_semantic_model",
    )


def _source_identity(package: dict[str, Any]) -> dict[str, Any]:
    metadata = package.get("metadata") or {}
    boundary = package.get("semantic_boundary") or {}
    return {
        "source_chart_id": (
            metadata.get("source_chart_id")
            or boundary.get("source_chart_id")
        ),
        "source_chart_ids": list(
            metadata.get("source_chart_ids")
            or boundary.get("source_chart_ids")
            or []
        ),
        "sensor_instance_id": (
            metadata.get("sensor_instance_id")
            or boundary.get("sensor_instance_id")
        ),
    }


def _source_registries(package: dict[str, Any]) -> dict[str, Any]:
    return {
        "theme_registry": deepcopy(package.get("theme_registry") or {}),
        "operator_registry": deepcopy(package.get("operator_registry") or {}),
        "object_registries": deepcopy(package.get("object_registries") or {}),
        "natal_context_registries": deepcopy(
            package.get("natal_context_registries") or {}
        ),
        "relationship_metrics": deepcopy(
            (
                package.get("projection_views", {})
                .get("orthodox_astrology.v1", {})
                .get("theme_metrics")
            )
            or []
        ),
    }



def _projectable_object_ids(graph: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for row in graph.get("objects") or []:
        oid = row.get("id")
        if oid is None:
            continue
        if house_number(row) is not None:
            result.add(str(oid))
            continue
        if canonical_object_name(row) in OBJECT_MAPPINGS:
            result.add(str(oid))
    return result


def _canonical_relationship_lookup(
    graph: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("id")): row
        for row in graph.get("relationships") or []
        if row.get("id") is not None
    }


def select_projection_representative_rows(
    graph: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    limit: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Select rows in source order while ensuring supported examples appear.

    Compact pipeline rows and canonical rows may use different endpoint-ID
    namespaces. Projectability is therefore resolved by shared relationship ID,
    then evaluated against the canonical relationship endpoints.
    """
    projectable_ids = _projectable_object_ids(graph)
    canonical_relationships = _canonical_relationship_lookup(graph)
    supported: list[dict[str, Any]] = []
    unsupported: list[dict[str, Any]] = []
    unresolved_relationship_id_count = 0

    for row in rows:
        canonical = canonical_relationships.get(str(row.get("id")))
        if canonical is None:
            unresolved_relationship_id_count += 1
            unsupported.append(row)
            continue

        source_id = str(
            canonical.get("source_id")
            or canonical.get("source_object_id")
            or ""
        )
        target_id = str(
            canonical.get("target_id")
            or canonical.get("target_object_id")
            or ""
        )
        bucket = (
            supported
            if source_id in projectable_ids and target_id in projectable_ids
            else unsupported
        )
        bucket.append(row)

    selected = [*supported[:limit]]
    remaining = max(0, limit - len(selected))
    if remaining:
        selected.extend(unsupported[:remaining])

    selected_projectable_count = min(len(supported), limit)
    return selected, {
        "available_row_count": len(rows),
        "available_projectable_row_count": len(supported),
        "available_unprojectable_row_count": len(unsupported),
        "unresolved_canonical_relationship_id_count": (
            unresolved_relationship_id_count
        ),
        "selected_row_count": len(selected),
        "selected_projectable_row_count": selected_projectable_count,
        "selected_unprojectable_row_count": (
            len(selected) - selected_projectable_count
        ),
    }


def projection_coverage_for_rows(
    rows: list[dict[str, Any]],
    projected_graph: dict[str, Any],
) -> dict[str, int]:
    lookup = projected_relationship_by_canonical_id(projected_graph)
    projected_count = sum(
        1 for row in rows if str(row.get("id")) in lookup
    )
    return {
        "selected_row_count": len(rows),
        "projected_row_count": projected_count,
        "unprojected_row_count": len(rows) - projected_count,
    }


def summarize_unmapped_families(
    source_graph: dict[str, Any],
    projected_graph: dict[str, Any],
    *,
    sample_limit: int = 5,
) -> dict[str, Any]:
    """Compact repeated unmapped diagnostics by source family."""
    unmapped_refs = list(
        projected_graph.get("diagnostics", {}).get("unmapped_source_refs")
        or projected_graph.get("audit", {}).get("unmapped_source_refs")
        or []
    )
    object_lookup = {
        str(row.get("id")): row for row in source_graph.get("objects") or []
    }
    relationship_lookup = {
        str(row.get("id")): row
        for row in source_graph.get("relationships") or []
    }
    groups: dict[str, dict[str, Any]] = {}

    for ref in unmapped_refs:
        text = str(ref)
        if text.startswith("canonical:object:"):
            source_id = text[len("canonical:object:"):]
            row = object_lookup.get(source_id) or {}
            family = str(row.get("object_type") or "unknown_object")
            key = f"object:{family}"
        elif text.startswith("canonical:relationship:"):
            source_id = text[len("canonical:relationship:"):]
            row = relationship_lookup.get(source_id) or {}
            family = str(row.get("relationship_type") or "unknown_relationship")
            key = f"relationship:{family}"
        else:
            source_id = text
            key = "unknown"

        group = groups.setdefault(
            key,
            {"family": key, "count": 0, "sample_source_refs": []},
        )
        group["count"] += 1
        if len(group["sample_source_refs"]) < sample_limit:
            group["sample_source_refs"].append(text)

    return {
        "unmapped_source_count": len(unmapped_refs),
        "family_count": len(groups),
        "families": sorted(
            groups.values(),
            key=lambda row: (-row["count"], row["family"]),
        ),
    }

def _canonical_subset(
    graph: dict[str, Any],
    relationship_ids: Iterable[str] | None,
) -> dict[str, Any]:
    if relationship_ids is None:
        return deepcopy(graph)

    wanted = {str(value) for value in relationship_ids}
    relationships = [
        deepcopy(row)
        for row in graph.get("relationships") or []
        if str(row.get("id")) in wanted
    ]
    endpoint_ids = {
        str(value)
        for row in relationships
        for value in (row.get("source_id"), row.get("target_id"))
        if value is not None
    }
    objects = [
        deepcopy(row)
        for row in graph.get("objects") or []
        if str(row.get("id")) in endpoint_ids
    ]
    result = {
        key: deepcopy(value)
        for key, value in graph.items()
        if key not in {"objects", "relationships", "indexes", "summary"}
    }
    result["objects"] = objects
    result["relationships"] = relationships
    result["summary"] = {
        "object_count": len(objects),
        "relationship_count": len(relationships),
        "source_subset": True,
    }
    result["indexes"] = {
        "object_by_id": {
            str(row.get("id")): index for index, row in enumerate(objects)
        },
        "relationship_by_id": {
            str(row.get("id")): index
            for index, row in enumerate(relationships)
        },
    }
    return result



def default_projection_context(
    package: dict[str, Any],
    *,
    profile_id: str = "orthodox_astrology.v1",
) -> ProjectionContext:
    """Build a conservative profile-aware context for a saved Foundry package."""
    metadata = package.get("metadata") or {}
    analysis_type = str(metadata.get("analysis_type") or "")
    is_relationship = any(
        token in analysis_type
        for token in ("synastry", "composite", "davison", "relationship")
    )

    if profile_id == "cognitive_architecture_demo.v0":
        return ProjectionContext(
            context_id="cognitive_architecture.general.v0",
            context_version="0.2.0",
            subject_scope="individual",
            target_domain="cognitive_architecture_demo.v0",
            application_context="cognitive_architecture_demo",
            relationship_type=None,
            audience="adult_general",
            output_intent="structured_semantic_model",
            constraints={
                "experimental": True,
                "clinical_use": False,
                "diagnostic_use": False,
            },
        )

    if profile_id == "woofmapped_astrology.v0":
        return ProjectionContext(
            context_id="woofmapped.doghouse.general.v0",
            context_version="0.1.0",
            subject_scope="dog",
            target_domain="woofmapped_astrology.v0",
            application_context="woofmapped_natal_projection",
            relationship_type=None,
            audience="handler_general",
            output_intent="structured_semantic_model",
            constraints={
                "playful_experimental_projection": True,
                "veterinary_advice": False,
                "behavioral_diagnosis": False,
                "house_mapping_policy": "doghouse",
            },
        )

    return ProjectionContext(
        context_id=(
            GENERAL_RELATIONSHIP_CONTEXT_ID
            if is_relationship
            else "orthodox.general.v1"
        ),
        context_version="1.0.0",
        subject_scope="relationship" if is_relationship else "individual",
        target_domain=profile_id,
        application_context=(
            "relationship_interpretation"
            if is_relationship
            else "general_interpretation"
        ),
        relationship_type="general" if is_relationship else None,
        audience="adult_general",
        output_intent="structured_semantic_model",
    )


def builtin_projection_registry() -> ProjectionProfileRegistry:
    return _external_builtin_projection_registry()



def project_dataset(
    source_package: dict[str, Any],
    *,
    profile_id: str = "orthodox_astrology.v1",
    profile_version: str = "1.0.0",
    context: ProjectionContext | dict[str, Any] | None = None,
    options: ProjectionOptions | dict[str, Any] | None = None,
    registry: ProjectionProfileRegistry | None = None,
) -> dict[str, Any]:
    """Project any saved Foundry package exposing the canonical boundary.

    This API performs no ephemeris or chart calculation. It consumes the
    package's existing canonical and structural graphs and optional registries.

    Temporal activation packages are rejected until the dedicated temporal
    projection contract is implemented; otherwise their top-level target chart
    would be mistaken for the complete timing package.
    """
    reject_unsupported_temporal_projection(source_package)
    source_graph = deepcopy(
        source_package.get("canonical_astrology_graph") or {}
    )
    if not source_graph:
        raise ValueError(
            "Source dataset does not contain canonical_astrology_graph. "
            "Use a full Foundry package rather than an analysis/streaming view."
        )

    if context is None:
        context_dict = default_projection_context(
            source_package,
            profile_id=profile_id,
        ).to_dict()
    elif isinstance(context, ProjectionContext):
        context_dict = context.to_dict()
    else:
        context_dict = deepcopy(context)

    if options is None:
        options_dict = ProjectionOptions().to_dict()
    elif isinstance(options, ProjectionOptions):
        options_dict = options.to_dict()
    else:
        options_dict = deepcopy(options)

    identity = _source_identity(source_package)
    request = ProjectionRequest(
        request_id=projection_request_id(
            profile_id=profile_id,
            profile_version=profile_version,
            source_identity=identity,
            context=context_dict,
            options=options_dict,
        ),
        profile_id=profile_id,
        profile_version=profile_version,
        source_graph=source_graph,
        structural_evidence=deepcopy(
            source_package.get("structural_evidence_graph") or {}
        ),
        source_identity=identity,
        context=context_dict,
        source_registries=_source_registries(source_package),
        options=options_dict,
    )
    result = project(
        request,
        registry=registry or builtin_projection_registry(),
    ).to_dict()
    result["metadata"]["source_dataset_analysis_type"] = (
        source_package.get("metadata", {}).get("analysis_type")
    )
    return result


def projection_summary_view(projected: dict[str, Any]) -> dict[str, Any]:
    """Compatibility wrapper over generic summary materialization."""
    return generic_projection_summary_view(projected)


def projection_materialization_view(
    projected: dict[str, Any],
    mode: str,
) -> dict[str, Any]:
    """Foundry compatibility wrapper over generic materialization policy."""
    return materialize_projected_graph(projected, mode=mode)


def enforce_unmapped_threshold(
    projected: dict[str, Any],
    threshold: float | None,
    *,
    scope: str = "canonical",
) -> None:
    """Raise when the selected unmapped fraction exceeds a threshold.

    ``eligible`` measures only rows the profile declared eligible. ``canonical``
    retains the legacy all-source denominator for forensic use.
    """
    if threshold is None:
        return
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("fail_on_unmapped_threshold must be between 0 and 1")
    if scope not in {"eligible", "canonical"}:
        raise ValueError("unmapped threshold scope must be eligible or canonical")

    if scope == "eligible":
        profile_scope = (projected.get("summary") or {}).get("profile_scope_coverage") or {}
        objects = profile_scope.get("objects") or {}
        relationships = profile_scope.get("relationships") or {}
        total = int(objects.get("eligible_count") or 0) + int(relationships.get("eligible_count") or 0)
        unmapped = int(objects.get("eligible_but_unmapped_count") or 0) + int(relationships.get("eligible_but_unmapped_count") or 0)
    else:
        coverage = projected.get("audit", {}).get("coverage") or {}
        total = int(coverage.get("source_object_count") or 0) + int(coverage.get("source_relationship_count") or 0)
        unmapped = int(coverage.get("unmapped_source_object_count") or 0) + int(coverage.get("unmapped_source_relationship_count") or 0)

    fraction = (unmapped / total) if total else 0.0
    if fraction > threshold:
        raise ValueError(
            f"Unmapped {scope} source fraction {fraction:.6f} "
            f"exceeds threshold {threshold:.6f}"
        )

def project_synastry_package(
    package: dict[str, Any],
    *,
    professional: bool = False,
    relationship_ids: Iterable[str] | None = None,
    include_audit: bool = True,
    include_diagnostics: bool = True,
) -> dict[str, Any]:
    """Project a saved Synastry package through the real orthodox profile.

    This is a Foundry adapter. The generic projection engine remains unaware of
    Synastry package layout.
    """
    graph = package.get("canonical_astrology_graph") or {}
    context = relationship_context(professional=professional).to_dict()
    options = ProjectionOptions(
        include_audit=include_audit,
        include_diagnostics=include_diagnostics,
        unmapped_policy="diagnostic",
    ).to_dict()
    identity = _source_identity(package)
    source_graph = _canonical_subset(graph, relationship_ids)
    request = ProjectionRequest(
        request_id=projection_request_id(
            profile_id="orthodox_astrology.v1",
            profile_version="1.0.0",
            source_identity=identity,
            context=context,
            options=options,
        ),
        profile_id="orthodox_astrology.v1",
        profile_version="1.0.0",
        source_graph=source_graph,
        structural_evidence=deepcopy(
            package.get("structural_evidence_graph") or {}
        ),
        source_identity=identity,
        context=context,
        source_registries=_source_registries(package),
        options=options,
    )
    return project(request, registry=builtin_projection_registry()).to_dict()


def canonical_subset_for_relationship_ids(
    graph: dict[str, Any],
    relationship_ids: Iterable[str],
) -> dict[str, Any]:
    """Return canonical relationships and their canonical endpoint objects."""
    return _canonical_subset(graph, relationship_ids)


def projected_relationship_by_canonical_id(
    projected_graph: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    by_id = {
        str(row.get("id")): row
        for row in projected_graph.get("relationships") or []
    }
    result = {}
    prefix = "canonical:relationship:"
    for source_ref, projected_ids in (
        projected_graph.get("indexes", {})
        .get("projected_relationships_by_source_ref", {})
        .items()
    ):
        if not source_ref.startswith(prefix) or not projected_ids:
            continue
        row = by_id.get(str(projected_ids[0]))
        if row is not None:
            result[source_ref[len(prefix):]] = row
    return result


def projected_analysis_rows(
    rows: list[dict[str, Any]],
    projected_graph: dict[str, Any],
) -> list[dict[str, Any]]:
    lookup = projected_relationship_by_canonical_id(projected_graph)
    result = []
    for source in rows:
        row = dict(source)
        projected = lookup.get(str(source.get("id")))
        if projected is not None:
            row["projected_relationship_id"] = projected.get("id")
            row["projected_relationship_type"] = projected.get(
                "relationship_type"
            )
            row["theme_tags"] = list(projected.get("theme_tags") or [])
            row["semantic_operator_hints"] = [
                {"operator": operator, "role": "projected_operator"}
                for operator in projected.get("operators") or []
            ]
            row["projection_relevance_score"] = projected.get(
                "projection_relevance_score"
            )
            row["projection_context_refs"] = list(
                projected.get("context_refs") or []
            )
            row["projection_mapping_rule_refs"] = list(
                projected.get("mapping_rule_refs") or []
            )
            row["projection_theme_evidence"] = deepcopy(
                projected.get("attributes", {}).get("theme_evidence") or []
            )
        result.append(row)
    return result
