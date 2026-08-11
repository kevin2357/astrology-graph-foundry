from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from astrology_graph_foundry.common.aspects import find_aspect, relevance_score
from astrology_graph_foundry.common.chart_graph import build_chart_graph, normalize_relationship_types
from astrology_graph_foundry.common.geometry import house_for_lon
from astrology_graph_foundry.common.graph_compiler import GraphCompiler, TransitTarget
from astrology_graph_foundry.common.semantic_layers import (
    finalize_package_semantic_boundary,
    finalize_view_semantic_boundary,
    orthodox_claims_from_package,
    orthodox_metrics_from_package,
    orthodox_report_materials_from_package,
    orthodox_row_annotation,
)
from astrology_graph_foundry.common.themes import operator_hints, theme_tags
from astrology_graph_foundry.pipelines.composite import build_from_datasets as build_composite_from_datasets
from astrology_graph_foundry.pipelines.composite import resolve_pair_inputs

SCHEMA_VERSION = "1.2.0"
PIPELINE_VERSION = "synastry_pipeline_v1.1.0"
logger = logging.getLogger(__name__)


def _person_name(dataset: dict[str, Any], fallback: str) -> str:
    return (
        dataset.get("metadata", {}).get("person")
        or dataset.get("person", {}).get("person")
        or dataset.get("person", fallback)
        or fallback
    )


def _natal(dataset: dict[str, Any]) -> dict[str, Any]:
    natal = dataset.get("natal", dataset)
    graph = dataset.get("canonical_astrology_graph") or natal.get("semantic_graph")
    if graph is None:
        graph = build_chart_graph(natal)
    natal["semantic_graph"] = normalize_relationship_types(graph)
    return natal


def _compiler(dataset: dict[str, Any], *, relationship_limit: int = 8) -> GraphCompiler:
    return GraphCompiler(_natal(dataset), relationship_limit=relationship_limit)


def _cusps(natal: dict[str, Any]) -> list[float]:
    houses = natal.get("houses") or {}
    return [float(houses[str(i)]["lon"]) for i in range(1, 13) if str(i) in houses]


def _safe(value: Any) -> str:
    return str(value or "unknown").replace(" ", "_").replace(":", "_")


def _operator_key(hints: list[dict[str, Any]]) -> str:
    if not hints:
        return "op:none"
    parts = []
    for hint in hints:
        parts.append(f"{hint.get('operator')}:{round(float(hint.get('confidence') or 0), 3)}")
    return "op:" + "|".join(parts)


def _theme_key(tags: list[str]) -> str:
    return "theme:" + "|".join(sorted(str(t) for t in tags)) if tags else "theme:none"


def _synastry_id(direction: str, src: TransitTarget, tgt: TransitTarget, aspect: dict[str, Any]) -> str:
    return f"syn:{direction}:{_safe(src.id)}:{str(aspect.get('aspect')).replace(' ', '_')}:{_safe(tgt.id)}"


def _overlay_id(direction: str, src: TransitTarget, house: int) -> str:
    return f"ov:{direction}:{_safe(src.id)}:h{house}"


def _object_registry(compiler: GraphCompiler) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for obj in compiler.graph.get("objects", []) or []:
        oid = obj.get("id")
        if not oid:
            continue
        # Keep registry compact but report-useful. The full natal graph can be
        # regenerated from the natal package; synastry consumers mainly need
        # labels, positions, classes, and houses for aspect interpretation.
        entry = {
            k: obj.get(k)
            for k in (
                "id",
                "object_type",
                "name",
                "source_key",
                "longitude",
                "sign",
                "house",
                "pretty",
                "modality",
                "element",
                "ruler",
                "dignity_state",
                "sect_status",
                "formula",
            )
            if k in obj and obj.get(k) is not None
        }
        owner_id = (obj.get("facts") or {}).get("owner_id") or obj.get("owner_object_ref")
        if owner_id is not None:
            entry["owner_object_ref"] = str(owner_id)
        # Source-operator hints are pre-projection semantics and are compact
        # enough to preserve once per registry object.
        if obj.get("semantic_operator_hints"):
            entry["semantic_operator_hints"] = list(obj.get("semantic_operator_hints") or [])
        registry[str(oid)] = entry
    return dict(sorted(registry.items()))


def _natal_context_registry(compiler: GraphCompiler) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for target in compiler.targets:
        for rel in target.activated_relationships:
            rel_id = rel.get("relationship_id")
            if rel_id:
                registry[str(rel_id)] = dict(rel)
    return dict(sorted(registry.items()))


def _target_context_refs(target: TransitTarget) -> list[str]:
    return [str(rel["relationship_id"]) for rel in target.activated_relationships if rel.get("relationship_id")]


def _operator_registry_from_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    registry: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = row.get("operator_key")
        if key and key not in registry:
            registry[str(key)] = list(row.get("semantic_operator_hints", []) or [])
    return dict(sorted(registry.items()))


def _theme_registry_from_rows(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    registry: dict[str, list[str]] = {}
    for row in rows:
        key = row.get("theme_key")
        if key and key not in registry:
            registry[str(key)] = list(row.get("theme_tags", []) or [])
    return dict(sorted(registry.items()))


def _aspect_matrix(
    source_name: str,
    source_compiler: GraphCompiler,
    target_name: str,
    target_compiler: GraphCompiler,
    *,
    direction: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total_pairs = len(source_compiler.targets) * len(target_compiler.targets)
    logger.info(
        "Synastry aspect scan %s: source_targets=%d target_targets=%d pair_checks=%d",
        direction,
        len(source_compiler.targets),
        len(target_compiler.targets),
        total_pairs,
    )
    checked = 0
    for src in source_compiler.targets:
        for tgt in target_compiler.targets:
            checked += 1
            aspect = find_aspect(src.name, src.longitude, tgt.name, tgt.longitude, include_minor=True)
            if not aspect:
                continue
            weight = relevance_score(src.name, tgt.source_key or tgt.name, aspect)
            tags = theme_tags(src.name, tgt.name, tgt.house, tgt.object_type, aspect=aspect.get("aspect"))
            ops = operator_hints(src.name, tgt.name, tgt.object_type, aspect=aspect.get("aspect"))
            rows.append({
                "id": _synastry_id(direction, src, tgt, aspect),
                "relationship_type": "SYNASTRY_ASPECT",
                "direction": direction,
                "source_person": source_name,
                "target_person": target_name,
                "source_object_id": src.id,
                "source_object_type": src.object_type,
                "source_object_name": src.name,
                "target_object_id": tgt.id,
                "target_object_type": tgt.object_type,
                "target_object_name": tgt.name,
                "aspect": aspect["aspect"],
                "orb": aspect["orb"],
                "distance": aspect["distance"],
                "exact_angle": aspect["exact_angle"],
                "major": aspect["major"],
                "strength": aspect["strength"],
                "weight": weight,
                "theme_key": _theme_key(tags),
                "operator_key": _operator_key(ops),
                "theme_tags": tags,
                "semantic_operator_hints": ops,
                "source_natal_context_refs": _target_context_refs(src),
                "target_natal_context_refs": _target_context_refs(tgt),
            })
    rows.sort(key=lambda r: (-float(r.get("weight") or 0), float(r.get("orb") or 99)))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    logger.info("Synastry aspect scan complete %s: checked=%d matches=%d", direction, checked, len(rows))
    return rows


def _house_overlays(
    source_name: str,
    source_compiler: GraphCompiler,
    target_name: str,
    target_natal: dict[str, Any],
    *,
    direction: str,
) -> list[dict[str, Any]]:
    cusps = _cusps(target_natal)
    rows: list[dict[str, Any]] = []
    if len(cusps) != 12:
        logger.warning("Skipping house overlays %s: target house cusp count=%d", direction, len(cusps))
        return rows
    for src in source_compiler.targets:
        house = house_for_lon(src.longitude, cusps)
        tags = theme_tags(src.name, str(house), src.object_type)
        ops = operator_hints(src.name)
        rows.append({
            "id": _overlay_id(direction, src, house),
            "relationship_type": "HOUSE_OVERLAY",
            "direction": direction,
            "source_person": source_name,
            "target_person": target_name,
            "source_object_id": src.id,
            "source_object_type": src.object_type,
            "source_object_name": src.name,
            "target_house": house,
            "theme_key": _theme_key(tags),
            "operator_key": _operator_key(ops),
            "theme_tags": tags,
            "semantic_operator_hints": ops,
            "source_natal_context_refs": _target_context_refs(src),
        })
    logger.info("House overlays complete %s: overlays=%d", direction, len(rows))
    return rows


def _registry_compact_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out.pop("theme_tags", None)
    out.pop("semantic_operator_hints", None)
    # Backward compatibility cleanup if older rows are ever passed through.
    out.pop("source_natal_relationship_context", None)
    out.pop("target_natal_relationship_context", None)
    return out


def _synastry_registry_entry(row: dict[str, Any]) -> dict[str, Any]:
    # Streaming/game view intentionally keeps only static lookup fields. Rich
    # prose/context belongs in analysis/full outputs, not game indexes.
    return {
        "id": row.get("id"),
        "relationship_type": row.get("relationship_type"),
        "direction": row.get("direction"),
        "source_object_id": row.get("source_object_id"),
        "source_object_type": row.get("source_object_type"),
        "target_object_id": row.get("target_object_id"),
        "target_object_type": row.get("target_object_type"),
        "aspect": row.get("aspect"),
        "exact_angle": row.get("exact_angle"),
        "major": row.get("major"),
        "theme_key": row.get("theme_key"),
        "operator_key": row.get("operator_key"),
    }


def _overlay_registry_entry(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "relationship_type": row.get("relationship_type"),
        "direction": row.get("direction"),
        "source_object_id": row.get("source_object_id"),
        "source_object_type": row.get("source_object_type"),
        "target_house": row.get("target_house"),
        "theme_key": row.get("theme_key"),
        "operator_key": row.get("operator_key"),
    }


def _synastry_registry(package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reg: dict[str, dict[str, Any]] = {}
    ns = package.get("natal_synastry", {})
    for key in ("a_to_b_aspects", "b_to_a_aspects"):
        for row in ns.get(key, []) or []:
            reg[str(row["id"])] = _synastry_registry_entry(row)
    return dict(sorted(reg.items()))


def _overlay_registry(package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    reg: dict[str, dict[str, Any]] = {}
    ns = package.get("natal_synastry", {})
    for key in ("a_to_b_house_overlays", "b_to_a_house_overlays"):
        for row in ns.get(key, []) or []:
            reg[str(row["id"])] = _overlay_registry_entry(row)
    return dict(sorted(reg.items()))


def _contact_activation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "contact_id": row.get("id"),
        "rank": row.get("rank"),
        "orb": row.get("orb"),
        "distance": row.get("distance"),
        "strength": row.get("strength"),
        "weight": row.get("weight"),
    }


def _overlay_activation(row: dict[str, Any]) -> dict[str, Any]:
    return {"overlay_id": row.get("id"), "rank": row.get("rank"), "target_house": row.get("target_house")}


def _relationship_metrics(*collections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scores: dict[str, float] = defaultdict(float)
    evidence: dict[str, list[str]] = defaultdict(list)
    # Damp expanded-object volume so thousands of harmonic/antiscia contacts do
    # not swamp core relationship signatures simply by count.
    object_type_weight = {
        "planet_or_point": 1.0,
        "angle": 1.0,
        "calculated_point": 0.85,
        "lot": 0.75,
        "dignity_state": 0.45,
        "antiscia_point": 0.5,
        "contra_antiscia_point": 0.5,
        "harmonic_point": 0.35,
        "declination_position": 0.45,
        "sect_state": 0.35,
    }
    for rows in collections:
        for row in rows:
            source_type = row.get("source_object_type") or row.get("source_type")
            target_type = row.get("target_object_type") or row.get("target_type")
            damp = min(object_type_weight.get(str(source_type), 0.65), object_type_weight.get(str(target_type), 0.65))
            base = float(row.get("weight") or 3.0) * damp
            for tag in row.get("theme_tags", []) or []:
                scores[tag] += base
                evidence[tag].append(row.get("id"))
    return [
        {"theme": theme, "score": round(score, 3), "evidence_refs": evidence[theme][:20]}
        for theme, score in sorted(scores.items(), key=lambda kv: -kv[1])
    ]


def _evidence_graph(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"synastry_claim_{i:04d}",
            "theme": metric["theme"],
            "claim": f"The synastry has a strong {metric['theme'].replace('_', ' ')} signature.",
            "confidence": min(0.98, 0.45 + float(metric["score"]) / 250),
            "supporting_relationship_refs": metric.get("evidence_refs", [])[:12],
        }
        for i, metric in enumerate(metrics[:25], 1)
    ]


def _natal_context_hints(package: dict[str, Any], *, per_person_limit: int = 40) -> dict[str, list[dict[str, Any]]]:
    hints: dict[str, list[dict[str, Any]]] = {"person_a": [], "person_b": []}
    for person_key in ("person_a", "person_b"):
        object_registry = package.get("object_registries", {}).get(person_key, {})
        context_registry = package.get("natal_context_registries", {}).get(person_key, {})
        # Prioritize relationship summaries attached to objects that appear in top contacts.
        seen: set[str] = set()
        for section in ("a_to_b_aspects", "b_to_a_aspects", "a_to_b_house_overlays", "b_to_a_house_overlays"):
            for row in package.get("natal_synastry", {}).get(section, [])[:80]:
                refs = []
                if person_key == "person_a":
                    refs.extend(row.get("source_natal_context_refs", []) if section.startswith("a_to_b") else row.get("target_natal_context_refs", []))
                else:
                    refs.extend(row.get("target_natal_context_refs", []) if section.startswith("a_to_b") else row.get("source_natal_context_refs", []))
                for ref in refs:
                    if ref in seen or ref not in context_registry:
                        continue
                    seen.add(ref)
                    hints[person_key].append(orthodox_row_annotation(context_registry[ref]))
                    if len(hints[person_key]) >= per_person_limit:
                        break
                if len(hints[person_key]) >= per_person_limit:
                    break
            if len(hints[person_key]) >= per_person_limit:
                break
        # Add minimal object hints so report consumers can discuss natal context
        # without loading the full natal dataset.
        for obj in list(object_registry.values())[:20]:
            if len(hints[person_key]) >= per_person_limit:
                break
            hints[person_key].append({"object_id": obj.get("id"), "object_name": obj.get("name"), "object_type": obj.get("object_type"), "house": obj.get("house"), "pretty": obj.get("pretty")})
    return hints


def _top_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return [
        _registry_compact_row(orthodox_row_annotation(row))
        for row in rows[:limit]
    ]


def analysis_view(package: dict[str, Any], *, top_aspect_limit: int = 80, top_overlay_limit: int = 60) -> dict[str, Any]:
    """Build a compact source-factual Synastry handoff without projection."""
    ns = package.get("natal_synastry", {})
    all_aspect_rows = (
        (ns.get("a_to_b_aspects", []) or [])
        + (ns.get("b_to_a_aspects", []) or [])
    )
    all_overlay_rows = (
        (ns.get("a_to_b_house_overlays", []) or [])
        + (ns.get("b_to_a_house_overlays", []) or [])
    )
    aspect_rows = [_registry_compact_row(row) for row in all_aspect_rows[:top_aspect_limit]]
    overlay_rows = [_registry_compact_row(row) for row in all_overlay_rows[:top_overlay_limit]]
    view = {
        "metadata": {
            **package["metadata"],
            "view_type": "synastry_analysis",
            "view_compaction": "source_factual_relationship_handoff_v3",
            "projection_status": "not_performed",
            "projection_owner": "semantic_projection_core_or_orchestration",
        },
        "person_a": package.get("person_a"),
        "person_b": package.get("person_b"),
        "object_registries": package.get("object_registries", {}),
        "theme_registry": dict(package.get("theme_registry") or {}),
        "operator_registry": dict(package.get("operator_registry") or {}),
        "natal_context_hints": _natal_context_hints(package),
        "top_synastry_aspects": aspect_rows,
        "top_house_overlays": overlay_rows,
        "source_selection": {
            "top_synastry_aspects": {"available": len(all_aspect_rows), "selected": len(aspect_rows)},
            "top_house_overlays": {"available": len(all_overlay_rows), "selected": len(overlay_rows)},
        },
        "canonical_source_graph": package.get("canonical_astrology_graph") or {},
        "structural_evidence_graph": package.get("structural_evidence_graph") or {},
        "composite_summary": _compact_composite_summary(package.get("composite")),
    }
    return finalize_view_semantic_boundary(view, package)


def streaming_index(package: dict[str, Any]) -> dict[str, Any]:
    ns = package.get("natal_synastry", {})
    contacts = _synastry_registry(package)
    overlays = _overlay_registry(package)
    logger.info("Creating synastry streaming index: contacts=%d overlays=%d", len(contacts), len(overlays))
    view = {
        "metadata": {**package["metadata"], "view_type": "synastry_streaming_index", "view_compaction": "minimal_game_contact_registry_v2"},
        "person_a": package.get("person_a"),
        "person_b": package.get("person_b"),
        "object_registry_summary": {
            person: {oid: {k: obj.get(k) for k in ("id", "object_type", "name", "longitude", "house") if obj.get(k) is not None} for oid, obj in registry.items()}
            for person, registry in package.get("object_registries", {}).items()
        },
        "contact_registry": contacts,
        "overlay_registry": overlays,
        "theme_registry": _theme_registry_from_rows(sum((ns.get(k, []) for k in ns), [])),
        "operator_registry": _operator_registry_from_rows(sum((ns.get(k, []) for k in ns), [])),
        "natal_context_registry_available_in_full_or_analysis": True,
        "indexes": {
            "by_direction": _index_by(package, "direction"),
            "by_aspect": _index_by(package, "aspect"),
            "by_source_object": _index_by(package, "source_object_id"),
            "by_target_object": _index_by(package, "target_object_id"),
            "by_theme": _index_by_theme(package),
            "by_house": _index_by_house(package),
        },
        "ranked_contacts": [_contact_activation(row) for row in (ns.get("a_to_b_aspects", []) + ns.get("b_to_a_aspects", []))],
        "house_overlay_refs": [_overlay_activation(row) for row in (ns.get("a_to_b_house_overlays", []) + ns.get("b_to_a_house_overlays", []))],
        "orthodox_relationship_metric_summary": orthodox_metrics_from_package(package)[:40],
    }
    return finalize_view_semantic_boundary(view, package)


def _iter_contact_rows(package: dict[str, Any]) -> list[dict[str, Any]]:
    ns = package.get("natal_synastry", {})
    return (ns.get("a_to_b_aspects", []) or []) + (ns.get("b_to_a_aspects", []) or [])


def _iter_overlay_rows(package: dict[str, Any]) -> list[dict[str, Any]]:
    ns = package.get("natal_synastry", {})
    return (ns.get("a_to_b_house_overlays", []) or []) + (ns.get("b_to_a_house_overlays", []) or [])


def _index_by(package: dict[str, Any], field: str) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for row in _iter_contact_rows(package):
        value = row.get(field)
        if value is not None:
            index[str(value)].append(row["id"])
    return dict(sorted(index.items()))


def _index_by_theme(package: dict[str, Any]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for row in _iter_contact_rows(package) + _iter_overlay_rows(package):
        for tag in row.get("theme_tags", []) or []:
            index[str(tag)].append(row["id"])
    return dict(sorted(index.items()))


def _index_by_house(package: dict[str, Any]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for row in _iter_overlay_rows(package):
        index[str(row.get("target_house"))].append(row["id"])
    for row in _iter_contact_rows(package):
        # Aspect rows do not always have an explicit house field after
        # compaction; consumers can resolve object houses through registry.
        pass
    return dict(sorted(index.items()))


def _compact_composite_summary(composite: dict[str, Any] | None) -> dict[str, Any] | None:
    if not composite:
        return None
    report_materials = orthodox_report_materials_from_package(composite)
    return {
        "metadata": composite.get("metadata", {}),
        "balance_metrics": composite.get("balance_metrics", {}),
        "orthodox_theme_metrics": orthodox_metrics_from_package(composite)[:20],
        "top_composite_aspects": report_materials.get("top_composite_aspects", [])[:20],
        "top_claim_candidates": orthodox_claims_from_package(composite)[:12],
    }


def _compact_full_package(package: dict[str, Any]) -> dict[str, Any]:
    # Keep full research matrices, but move repeated semantic material into registries.
    out = dict(package)
    out["natal_synastry"] = {
        key: [_registry_compact_row(row) for row in rows]
        for key, rows in package.get("natal_synastry", {}).items()
    }
    rows = []
    for values in package.get("natal_synastry", {}).values():
        rows.extend(values)
    out["theme_registry"] = _theme_registry_from_rows(rows)
    out["operator_registry"] = _operator_registry_from_rows(rows)
    return out


def build_from_datasets(person_a_dataset: dict[str, Any], person_b_dataset: dict[str, Any], *, include_composite: bool = True) -> dict[str, Any]:
    name_a = _person_name(person_a_dataset, "Person A")
    name_b = _person_name(person_b_dataset, "Person B")
    logger.info("Building synastry dataset for %s + %s", name_a, name_b)
    natal_a = _natal(person_a_dataset)
    natal_b = _natal(person_b_dataset)
    compiler_a = _compiler(person_a_dataset)
    compiler_b = _compiler(person_b_dataset)
    logger.info(
        "Compiled synastry natal graphs: %s targets=%d objects=%d rels=%d; %s targets=%d objects=%d rels=%d",
        name_a,
        len(compiler_a.targets),
        len(compiler_a.graph.get("objects", [])),
        len(compiler_a.graph.get("relationships", [])),
        name_b,
        len(compiler_b.targets),
        len(compiler_b.graph.get("objects", [])),
        len(compiler_b.graph.get("relationships", [])),
    )
    a_to_b = _aspect_matrix(name_a, compiler_a, name_b, compiler_b, direction="a_to_b")
    b_to_a = _aspect_matrix(name_b, compiler_b, name_a, compiler_a, direction="b_to_a")
    overlays_a_to_b = _house_overlays(name_a, compiler_a, name_b, natal_b, direction="a_to_b")
    overlays_b_to_a = _house_overlays(name_b, compiler_b, name_a, natal_a, direction="b_to_a")
    metrics = _relationship_metrics(a_to_b, b_to_a, overlays_a_to_b, overlays_b_to_a)
    evidence = _evidence_graph(metrics)
    composite = build_composite_from_datasets(person_a_dataset, person_b_dataset) if include_composite else None
    package = {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "analysis_type": "synastry_relationship_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "person_a": name_a,
            "person_b": name_b,
            "uses_expanded_natal_semantic_graph": True,
            "relationship_types": ["SYNASTRY_ASPECT", "HOUSE_OVERLAY"] + (["COMPOSITE_ASPECT"] if include_composite else []),
            "compaction_model": "registries_and_refs_v1",
            "graph_compiler": {
                "person_a": compiler_a.metadata(),
                "person_b": compiler_b.metadata(),
            },
        },
        "person_a": {"metadata": person_a_dataset.get("metadata", {}), "semantic_graph_summary": natal_a.get("semantic_graph", {}).get("summary", {})},
        "person_b": {"metadata": person_b_dataset.get("metadata", {}), "semantic_graph_summary": natal_b.get("semantic_graph", {}).get("summary", {})},
        "object_registries": {
            "person_a": _object_registry(compiler_a),
            "person_b": _object_registry(compiler_b),
        },
        "natal_context_registries": {
            "person_a": _natal_context_registry(compiler_a),
            "person_b": _natal_context_registry(compiler_b),
        },
        "natal_synastry": {
            "a_to_b_aspects": a_to_b,
            "b_to_a_aspects": b_to_a,
            "a_to_b_house_overlays": overlays_a_to_b,
            "b_to_a_house_overlays": overlays_b_to_a,
        },
        "composite": composite,
        "relationship_metrics": metrics,
        "evidence_graph": evidence,
        "report_materials": {
            "recommended_sections": [
                "Executive Summary",
                "Individual Natal Context",
                "Planet/Object-to-Object Synastry",
                "House Overlay Analysis",
                "Composite Relationship Entity",
                "Relationship Themes and Evidence Graph",
                "Operating Manual / Practical Synthesis",
                "Technical Appendix",
            ],
            "top_synastry_aspects": _top_rows((a_to_b + b_to_a), 40),
            "top_house_overlays": _top_rows((overlays_a_to_b + overlays_b_to_a), 40),
            "top_relationship_metrics": metrics[:20],
            "top_evidence_claims": evidence[:12],
            "natal_context_hints": None,  # Filled below to avoid duplicate construction.
        },
    }
    package["report_materials"]["natal_context_hints"] = _natal_context_hints(package)
    compact = _compact_full_package(package)
    logger.info(
        "Synastry dataset complete: a_to_b=%d b_to_a=%d overlays=%d/%d composite=%s context_registry=%d/%d",
        len(a_to_b),
        len(b_to_a),
        len(overlays_a_to_b),
        len(overlays_b_to_a),
        bool(composite),
        len(package["natal_context_registries"]["person_a"]),
        len(package["natal_context_registries"]["person_b"]),
    )
    return finalize_package_semantic_boundary(compact)


def build(**kwargs: Any) -> dict[str, Any]:
    data_a, data_b = resolve_pair_inputs(**kwargs)
    return build_from_datasets(data_a, data_b, include_composite=kwargs.get("include_composite", True))
