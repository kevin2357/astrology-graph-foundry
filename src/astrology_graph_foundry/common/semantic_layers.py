from __future__ import annotations

"""Semantic-boundary and materialization helpers.

Chunk 1.4 ends the temporary dual-write inspection cycle. Full packages now
serialize one canonical source graph, one structural evidence graph, explicit
projection views, and pipeline-specific calculated data.

Consumers should prefer:

    canonical_astrology_graph
    structural_evidence_graph
    projection_views["orthodox_astrology.v1"]
"""

from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha1
from typing import Any
import re

from astrology_graph_foundry.common.identity import resolve_explicit_source_chart_id
from astrology_graph_foundry.common.themes import theme_tags

CANONICAL_GRAPH_VERSION = "1.3.0"
STRUCTURAL_EVIDENCE_VERSION = "1.3.0"
ORTHODOX_PROFILE_ID = "orthodox_astrology.v1"
ORTHODOX_PROFILE_VERSION = "1.0.0"

CORE_OBJECT_TYPES = {
    "planet_or_point",
    "angle",
    "house_cusp",
}
DERIVED_OBJECT_TYPES = {
    "antiscia_point",
    "contra_antiscia_point",
    "harmonic_point",
    "declination_position",
    "dignity_state",
    "sect_state",
    "calculated_point",
    "lot",
    "fixed_star",
}

MAJOR_ASPECTS = {"conjunction", "opposition", "square", "trine", "sextile"}


def _stable_token(*parts: Any) -> str:
    payload = "|".join(str(part if part is not None else "") for part in parts)
    return sha1(payload.encode("utf-8")).hexdigest()[:16]


def _safe_scope_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_") or "chart"


def _scope_prefix(source_chart_id: str) -> str:
    return source_chart_id if source_chart_id.endswith(":") else source_chart_id + ":"


def _scoped_source_object_id(object_id: str, source_chart_id: str) -> str:
    """Return a globally chart-scoped canonical object identifier.

    Legacy canonical graphs used local IDs such as ``natal:Moon``. Those IDs
    collide when multiple charts are projected into a shared downstream graph.
    The canonical boundary now scopes every object beneath the authoritative
    source chart ID, e.g. ``natal:kevin:Moon``.
    """
    raw = str(object_id)
    scope = str(source_chart_id)
    prefix = _scope_prefix(scope)
    if raw == scope or raw.startswith(prefix):
        return raw
    if scope.startswith("natal:") and raw.startswith("natal:"):
        return f"{prefix}{raw[len('natal:'):]}"
    return f"{prefix}{raw}"


def _canonical_relationship_id(rel: dict[str, Any]) -> str:
    return "rel:{}:{}".format(
        str(rel.get("relationship_type") or "unknown").lower(),
        _stable_token(
            rel.get("relationship_type"),
            rel.get("source_id"),
            rel.get("target_id"),
            rel.get("target_longitude"),
            rel.get("aspect"),
            rel.get("harmonic"),
            rel.get("type"),
        ),
    )


def _rebuild_graph_indexes(graph: dict[str, Any]) -> None:
    objects = graph.get("objects", []) or []
    relationships = graph.get("relationships", []) or []
    by_object: dict[str, list[int]] = {str(obj.get("id")): [] for obj in objects}
    for index, rel in enumerate(relationships):
        source_id = str(rel.get("source_id") or "")
        target_id = str(rel.get("target_id") or "")
        if source_id in by_object:
            by_object[source_id].append(index)
        if target_id in by_object:
            by_object[target_id].append(index)
    graph["indexes"] = {
        "objects_by_id": {str(obj.get("id")): i for i, obj in enumerate(objects)},
        "objects_by_source_key": {
            str(obj.get("source_key")): str(obj.get("id"))
            for obj in objects
            if obj.get("source_key") is not None
        },
        "relationships_by_type": {
            rel_type: [
                i for i, rel in enumerate(relationships)
                if str(rel.get("relationship_type")) == rel_type
            ]
            for rel_type in sorted({
                str(rel.get("relationship_type"))
                for rel in relationships
                if rel.get("relationship_type") is not None
            })
        },
        "relationships_by_object_id": by_object,
    }


def _scope_graph_ids_in_place(
    graph: dict[str, Any],
    source_chart_id: str | None,
) -> dict[str, str]:
    """Scope graph object/relationship IDs and return an old→new ref map."""
    if not source_chart_id:
        return {}

    ref_map: dict[str, str] = {}
    objects = graph.get("objects", []) or []
    previous_source_chart_id = str(
        graph.get("source_chart_id")
        or (graph.get("identity_policy") or {}).get("source_chart_id")
        or ""
    )
    previous_scope_prefix = (
        _scope_prefix(previous_source_chart_id) if previous_source_chart_id else ""
    )
    # Synthetic and externally supplied graphs may already define globally
    # meaningful IDs (for example ``synastry:person_a:...`` or ``obj:mars``).
    # Apply this legacy migration only to Foundry chart graphs that still use
    # the historical local ``natal:<object>`` namespace.
    has_legacy_natal_ids = any(
        str(obj.get("id") or "").startswith("natal:") for obj in objects
    )
    has_previous_scope = bool(previous_source_chart_id) and any(
        str(obj.get("id") or "") == previous_source_chart_id
        or str(obj.get("id") or "").startswith(previous_scope_prefix)
        for obj in objects
    )
    if not (has_legacy_natal_ids or has_previous_scope):
        return {}
    for obj in objects:
        old_id = str(obj.get("id") or "")
        if not old_id:
            continue
        if has_previous_scope and old_id == previous_source_chart_id:
            new_id = str(source_chart_id)
        elif has_previous_scope and old_id.startswith(previous_scope_prefix):
            suffix = old_id[len(previous_scope_prefix):]
            new_id = f"{_scope_prefix(str(source_chart_id))}{suffix}"
        else:
            new_id = _scoped_source_object_id(old_id, source_chart_id)
        if new_id != old_id:
            ref_map[old_id] = new_id
            obj["id"] = new_id

    exact_source_chart_id = str(source_chart_id)
    if previous_source_chart_id and previous_source_chart_id != exact_source_chart_id:
        ref_map[previous_source_chart_id] = exact_source_chart_id

    def replace_local(value: Any) -> Any:
        if isinstance(value, str):
            return ref_map.get(value, value)
        if isinstance(value, list):
            return [replace_local(item) for item in value]
        if isinstance(value, dict):
            return {
                ref_map.get(str(key), str(key)): replace_local(item)
                for key, item in value.items()
            }
        return value

    for obj in objects:
        for key, value in list(obj.items()):
            if key != "id":
                obj[key] = replace_local(value)

    relationships = graph.get("relationships", []) or []
    old_relationship_ids: list[tuple[str, dict[str, Any]]] = []
    for rel in relationships:
        old_relationship_ids.append((str(rel.get("id") or ""), rel))
        for key, value in list(rel.items()):
            if key != "id":
                rel[key] = replace_local(value)
        rel["id"] = _canonical_relationship_id(rel)

    for old_id, rel in old_relationship_ids:
        new_id = str(rel.get("id") or "")
        if old_id and new_id and old_id != new_id:
            ref_map[old_id] = new_id

    _rebuild_graph_indexes(graph)
    graph.setdefault("identity_policy", {})["object_id_scope"] = "source_chart_id"
    graph["identity_policy"]["relationship_id_scope"] = "scoped_endpoints"
    graph["identity_policy"]["source_chart_id"] = exact_source_chart_id
    return ref_map


def _rewrite_exact_refs(value: Any, ref_map: dict[str, str]) -> Any:
    """Recursively rewrite exact ID values and registry keys in a package."""
    if not ref_map:
        return value
    if isinstance(value, str):
        return ref_map.get(value, value)
    if isinstance(value, list):
        return [_rewrite_exact_refs(item, ref_map) for item in value]
    if isinstance(value, dict):
        rewritten: dict[str, Any] = {}
        for key, item in value.items():
            new_key = ref_map.get(str(key), str(key))
            rewritten[new_key] = _rewrite_exact_refs(item, ref_map)
        return rewritten
    return value


def _refresh_rescoped_identity_provenance(
    value: Any,
    *,
    previous_source_chart_id: str,
    source_chart_id: str,
    previous_sensor_id: str,
    sensor_id: str,
) -> None:
    """Refresh generated identity provenance after an intentional Natal rescope."""
    if isinstance(value, list):
        for item in value:
            _refresh_rescoped_identity_provenance(
                item,
                previous_source_chart_id=previous_source_chart_id,
                source_chart_id=source_chart_id,
                previous_sensor_id=previous_sensor_id,
                sensor_id=sensor_id,
            )
        return
    if not isinstance(value, dict):
        return

    if value.get("source_chart_id") == previous_source_chart_id:
        value["source_chart_id"] = source_chart_id
    if value.get("source_chart_ids") == [previous_source_chart_id]:
        value["source_chart_ids"] = [source_chart_id]
    for field in ("source_sensor_id", "sensor_instance_id"):
        if value.get(field) == previous_sensor_id:
            value[field] = sensor_id

    old_family_prefix = f"{_source_scope_token([previous_source_chart_id])}:"
    new_family_prefix = f"{_source_scope_token([source_chart_id])}:"
    for field in ("record_independence_group", "evidence_family_group", "independence_group"):
        current = value.get(field)
        if isinstance(current, str) and current.startswith(previous_sensor_id + ":"):
            value[field] = sensor_id + current[len(previous_sensor_id):]
    current_family = value.get("source_chart_family_group")
    if isinstance(current_family, str) and current_family.startswith(old_family_prefix):
        value["source_chart_family_group"] = new_family_prefix + current_family[len(old_family_prefix):]

    for child in value.values():
        if isinstance(child, (dict, list)):
            _refresh_rescoped_identity_provenance(
                child,
                previous_source_chart_id=previous_source_chart_id,
                source_chart_id=source_chart_id,
                previous_sensor_id=previous_sensor_id,
                sensor_id=sensor_id,
            )


def _slug(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    text = "".join(ch if ch.isalnum() else "_" for ch in text)
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_") or "unknown"


def _chart_id_from_person_metadata(value: dict[str, Any] | None, fallback: str) -> str:
    value = value or {}
    transitable = value.get("transitable_chart") or {}
    chart_identity = transitable.get("chart_identity") or {}
    explicit = resolve_explicit_source_chart_id(
        (
            ("transitable_chart.chart_identity.chart_id", chart_identity.get("chart_id")),
            ("source_chart_id", value.get("source_chart_id")),
            ("target_chart_id", value.get("target_chart_id")),
            ("chart_id", value.get("chart_id")),
        )
    )
    if explicit:
        return str(explicit)
    return f"natal:{_slug(value.get('person') or fallback)}"


def _relationship_chart_id(
    chart_type: str,
    label: Any,
    person_a: Any = None,
    person_b: Any = None,
) -> str | None:
    chart_type = str(chart_type or "").lower()
    if chart_type not in {"composite", "davison"}:
        return None
    if person_a and person_b:
        return f"{chart_type}:{_slug(person_a)}:{_slug(person_b)}"
    label_text = str(label or "")
    if ":" in label_text:
        label_text = label_text.split(":", 1)[1]
    if "+" in label_text:
        left, right = label_text.split("+", 1)
        return f"{chart_type}:{_slug(left)}:{_slug(right)}"
    return None


def _return_location_token(package: dict[str, Any]) -> str:
    location = package.get("return_location") or {}
    if not location:
        return "location_unspecified"
    return (
        f"{_slug(location.get('location_label') or 'location')}:"
        f"{_slug(location.get('timezone') or 'timezone')}:"
        f"{location.get('lat')}:{location.get('lon')}"
    )


def _semantic_identity(package: dict[str, Any]) -> dict[str, Any]:
    metadata = package.get("metadata") or {}
    analysis_type = str(metadata.get("analysis_type") or "unknown_dataset")
    transitable = package.get("transitable_chart") or {}
    transitable_identity = transitable.get("chart_identity") or {}
    target = package.get("target") if isinstance(package.get("target"), dict) else {}
    target_identity = (target.get("chart_identity") or {}) if isinstance(target, dict) else {}

    natal = package.get("natal") if isinstance(package.get("natal"), dict) else {}
    person = package.get("person") if isinstance(package.get("person"), dict) else {}
    natal_source_chart_id = resolve_explicit_source_chart_id(
        (
            ("transitable_chart.chart_identity.chart_id", transitable_identity.get("chart_id")),
            ("metadata.source_chart_id", metadata.get("source_chart_id")),
            ("metadata.target_chart_id", metadata.get("target_chart_id")),
            ("metadata.chart_id", metadata.get("chart_id")),
            ("person.source_chart_id", person.get("source_chart_id")),
            ("natal.source_chart_id", natal.get("source_chart_id")),
        )
    ) if analysis_type == "natal_dataset" else None

    direct_chart_id = resolve_explicit_source_chart_id(
        (
            ("transitable_chart.chart_identity.chart_id", transitable_identity.get("chart_id")),
            ("metadata.source_chart_id", metadata.get("source_chart_id")),
            ("metadata.target_chart_id", metadata.get("target_chart_id")),
            ("target.chart_identity.chart_id", target_identity.get("chart_id")),
            ("target.chart_id", target.get("chart_id") if isinstance(target, dict) else None),
        )
    )
    chart_type_hint = (
        transitable_identity.get("chart_type")
        or metadata.get("target_chart_type")
        or target_identity.get("chart_type")
        or (target.get("chart_type") if isinstance(target, dict) else None)
    )
    label_hint = (
        transitable_identity.get("label")
        or metadata.get("target_label")
        or target_identity.get("label")
        or (target.get("label") if isinstance(target, dict) else None)
    )
    relationship_source_id = _relationship_chart_id(
        str(chart_type_hint or ""),
        label_hint,
        metadata.get("person_a"),
        metadata.get("person_b"),
    )

    if analysis_type == "synastry_relationship_dataset":
        person_a_meta = ((package.get("person_a") or {}).get("metadata") or {})
        person_b_meta = ((package.get("person_b") or {}).get("metadata") or {})
        source_chart_ids = [
            _chart_id_from_person_metadata(person_a_meta, metadata.get("person_a") or "person_a"),
            _chart_id_from_person_metadata(person_b_meta, metadata.get("person_b") or "person_b"),
        ]
    elif natal_source_chart_id:
        source_chart_ids = [natal_source_chart_id]
    elif direct_chart_id:
        source_chart_ids = [str(direct_chart_id)]
    elif relationship_source_id:
        source_chart_ids = [relationship_source_id]
    elif analysis_type == "natal_dataset":
        source_chart_ids = [f"natal:{_slug(metadata.get('person') or (package.get('natal') or {}).get('person') or 'natal_chart')}"]
    elif analysis_type == "composite_dataset":
        source_chart_ids = [f"composite:{_slug(metadata.get('person_a'))}:{_slug(metadata.get('person_b'))}"]
    elif analysis_type == "davison_relationship_dataset":
        source_chart_ids = [f"davison:{_slug(metadata.get('person_a'))}:{_slug(metadata.get('person_b'))}"]
    else:
        source_chart_ids = [f"source:{_slug(analysis_type)}:{_stable_token(metadata)}"]

    primary = source_chart_ids[0]
    if analysis_type in {"natal_dataset", "composite_dataset", "davison_relationship_dataset"}:
        sensor_instance_id = primary
    elif analysis_type == "synastry_relationship_dataset":
        sensor_instance_id = f"synastry:{source_chart_ids[0]}:{source_chart_ids[1]}"
    elif analysis_type in {"transit_range_dataset", "transit_period_dataset"}:
        period = package.get("period") or {}
        start = period.get("start") or period.get("start_date") or metadata.get("start") or metadata.get("start_date") or "start"
        end = period.get("end") or period.get("end_date") or metadata.get("end") or metadata.get("end_date") or "end"
        sensor_instance_id = f"transit:{primary}:{start}:{end}"
    elif analysis_type == "solar_return_dataset":
        year = metadata.get("return_year") or (package.get("return_event") or {}).get("event_utc", "")[:4] or "year"
        sensor_instance_id = f"solar_return:{primary}:{year}:{_return_location_token(package)}"
    elif analysis_type == "lunar_return_dataset":
        period = package.get("period") or {}
        start = period.get("start") or period.get("start_date") or metadata.get("start") or metadata.get("start_date") or "start"
        end = period.get("end") or period.get("end_date") or metadata.get("end") or metadata.get("end_date") or "end"
        sensor_instance_id = f"lunar_return:{primary}:{start}:{end}:{_return_location_token(package)}"
    elif analysis_type == "eclipse_lunation_dataset":
        period = package.get("period") or {}
        start = period.get("start") or period.get("start_date") or metadata.get("start") or metadata.get("start_date") or "start"
        end = period.get("end") or period.get("end_date") or metadata.get("end") or metadata.get("end_date") or "end"
        sensor_instance_id = f"eclipse_lunation:{primary}:{start}:{end}"
    elif analysis_type == "annual_profections_dataset":
        target_date = metadata.get("target_date") or (package.get("profection") or {}).get("target_date") or "date"
        sensor_instance_id = f"annual_profection:{primary}:{target_date}"
    else:
        sensor_instance_id = f"{_slug(analysis_type)}:{primary}:{_stable_token(metadata)}"

    return {
        "source_chart_id": primary,
        "source_chart_ids": source_chart_ids,
        "sensor_instance_id": sensor_instance_id,
        "identity_version": "semantic_sensor_identity_v1.1.0",
    }


def _object_owner_ref(obj: dict[str, Any]) -> str | None:
    facts = obj.get("facts") or {}
    owner = (
        obj.get("owner_object_ref")
        or obj.get("owner_object_id")
        or facts.get("owner_object_ref")
        or facts.get("owner_id")
        or obj.get("source_object_ref")
    )
    # ``owner`` is intentionally excluded: Synastry uses it for person A/B,
    # not for derived-object lineage.
    return str(owner) if owner is not None else None


def _source_scope_token(source_chart_ids: list[str] | tuple[str, ...] | None) -> str:
    values = [str(value) for value in (source_chart_ids or []) if value]
    return "+".join(values) if values else "source_chart_unknown"


def _object_evidence_metadata(obj: dict[str, Any], sensor_id: str, source_chart_ids: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    object_type = str(obj.get("object_type") or obj.get("type") or "unknown")
    source_key = str(obj.get("source_key") or obj.get("id") or obj.get("name") or "unknown")
    owner = _object_owner_ref(obj)

    if object_type == "angle":
        tier = "angle"
        family = "direct_angle"
        derivation = "direct"
    elif object_type in CORE_OBJECT_TYPES:
        tier = "core"
        family = "direct_chart_object"
        derivation = "direct"
    elif object_type in {"lot", "calculated_point"}:
        tier = "calculated_point"
        family = "calculated_point_derivation"
        derivation = "derived"
    elif object_type in {"antiscia_point", "contra_antiscia_point"}:
        tier = "antiscia"
        family = "antiscia_derivation"
        derivation = "derived"
    elif object_type == "harmonic_point":
        tier = "harmonic"
        family = "harmonic_derivation"
        derivation = "derived"
    else:
        tier = "derived" if object_type in DERIVED_OBJECT_TYPES else "supplemental"
        family = f"{object_type}_derivation"
        derivation = "derived" if tier in {"derived", "antiscia", "harmonic", "calculated_point"} else "supplemental"

    independence_root = owner or source_key
    return {
        "evidence_tier": tier,
        "derivation_type": derivation,
        "derivation_family": family,
        "owner_object_ref": owner,
        "root_owner_object_ref": independence_root,
        "source_sensor_id": sensor_id,
        "sensor_instance_id": sensor_id,
        "source_chart_ids": list(source_chart_ids or []),
        "record_independence_group": f"{sensor_id}:object-record:{obj.get('id') or source_key}",
        "evidence_family_group": f"{sensor_id}:object-family:{independence_root}",
        "source_chart_family_group": f"{_source_scope_token(source_chart_ids)}:object-family:{independence_root}",
        # Kept as the compatibility alias used by Chunk 1.
        "independence_group": f"{sensor_id}:object-family:{independence_root}",
    }


_TIER_PRIORITY = {
    "core": 0,
    "angle": 0,
    "supplemental": 1,
    "calculated_point": 2,
    "derived": 3,
    "antiscia": 4,
    "harmonic": 5,
}


def _root_owner_id(object_id: str, object_lookup: dict[str, dict[str, Any]]) -> str:
    current = str(object_id)
    seen: set[str] = set()
    while current in object_lookup and current not in seen:
        seen.add(current)
        obj = object_lookup[current]
        evidence = obj.get("evidence_metadata") or {}
        owner = evidence.get("owner_object_ref") or _object_owner_ref(obj)
        if not owner or str(owner) == current:
            break
        current = str(owner)
    return current


def _endpoint_lineage(
    object_id: str,
    object_lookup: dict[str, dict[str, Any]] | None,
) -> tuple[str, str, str]:
    if not object_lookup or object_id not in object_lookup:
        return object_id, "core", "direct"
    obj = object_lookup[object_id]
    evidence = obj.get("evidence_metadata") or {}
    root = _root_owner_id(object_id, object_lookup)
    return (
        root,
        str(evidence.get("evidence_tier") or "core"),
        str(evidence.get("derivation_type") or "direct"),
    )


def _relationship_evidence_metadata(
    rel: dict[str, Any],
    sensor_id: str,
    object_lookup: dict[str, dict[str, Any]] | None = None,
    source_chart_ids: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    rel_type = str(rel.get("relationship_type") or rel.get("type") or "UNKNOWN")
    source_id = str(rel.get("source_id") or rel.get("source_object_id") or rel.get("source") or "unknown")
    target_id = str(rel.get("target_id") or rel.get("target_object_id") or rel.get("target") or "unknown")
    rel_upper = rel_type.upper()

    source_root, source_tier, source_derivation = _endpoint_lineage(source_id, object_lookup)
    target_root, target_tier, target_derivation = _endpoint_lineage(target_id, object_lookup)
    endpoint_tiers = [source_tier, target_tier]
    endpoint_derived = any(value == "derived" for value in (source_derivation, target_derivation))

    if "ANTISC" in rel_upper:
        base_tier = "antiscia"
        family = "antiscia_relationship"
        relation_derivation = "derived"
    elif "HARMONIC" in rel_upper:
        base_tier = "harmonic"
        family = "harmonic_relationship"
        relation_derivation = "derived"
    elif "DECLINATION" in rel_upper:
        base_tier = "supplemental"
        family = "declination_relationship"
        relation_derivation = "direct"
    elif "HOUSE" in rel_upper or "OVERLAY" in rel_upper:
        base_tier = "core"
        family = "house_relationship"
        relation_derivation = "direct"
    elif "ASPECT" in rel_upper or rel.get("aspect"):
        base_tier = "core"
        family = "direct_aspect"
        relation_derivation = "direct"
    else:
        base_tier = "supplemental"
        family = rel_type.lower()
        relation_derivation = "derived" if rel.get("derived") else "direct"

    all_tiers = [base_tier, *endpoint_tiers]
    tier = max(all_tiers, key=lambda value: _TIER_PRIORITY.get(value, 1))

    if relation_derivation == "direct" and endpoint_derived:
        derivation = "direct_relation_between_derived_objects"
        family = f"{family}_between_derived_objects"
    elif relation_derivation == "derived":
        derivation = "derived"
    else:
        derivation = "direct"

    aspect_or_type = str(rel.get("aspect") or rel_type)
    record_id = str(rel.get("id") or rel.get("relationship_id") or _stable_token(source_id, target_id, aspect_or_type))
    family_key = f"{source_root}:{target_root}:{aspect_or_type}"

    return {
        "evidence_tier": tier,
        "derivation_type": derivation,
        "derivation_family": family,
        "owner_object_refs": [source_root, target_root],
        "source_owner_object_ref": source_root,
        "target_owner_object_ref": target_root,
        "endpoint_evidence_tiers": endpoint_tiers,
        "source_sensor_id": sensor_id,
        "sensor_instance_id": sensor_id,
        "source_chart_ids": list(source_chart_ids or []),
        "record_independence_group": f"{sensor_id}:relationship-record:{record_id}",
        "evidence_family_group": f"{sensor_id}:relationship-family:{family_key}",
        "source_chart_family_group": f"{_source_scope_token(source_chart_ids)}:relationship-family:{family_key}",
        # Compatibility alias now intentionally points at the collapsed family.
        "independence_group": f"{sensor_id}:relationship-family:{family_key}",
    }

def structural_strength_score(row: dict[str, Any]) -> float:
    """Projection-neutral geometric/directness score in the range 0..1.

    This deliberately excludes orthodox salience rules such as luminary,
    angle, personal-planet, or outer-planet importance.
    """
    orb = row.get("orb")
    if orb is None:
        exactness = 0.5
    else:
        exactness = max(0.0, 1.0 - min(float(orb), 12.0) / 12.0)

    aspect = str(row.get("aspect") or "").lower()
    aspect_weight = 1.0 if aspect in MAJOR_ASPECTS else (0.78 if aspect else 0.7)
    duration = float(row.get("active_days") or 1.0)
    duration_factor = min(1.0, 0.45 + (duration ** 0.5) / 10.0)

    evidence = row.get("evidence_metadata") or {}
    derivation_factor = {
        "direct": 1.0,
        "direct_relation_between_derived_objects": 0.78,
        "supplemental": 0.88,
        "derived": 0.72,
    }.get(str(evidence.get("derivation_type")), 0.82)

    return round(max(0.0, min(1.0, exactness * aspect_weight * duration_factor * derivation_factor)), 6)


def _annotate_row_legacy_and_boundary(
    row: dict[str, Any],
    sensor_id: str,
    kind: str,
    object_lookup: dict[str, dict[str, Any]] | None = None,
    source_chart_ids: list[str] | tuple[str, ...] | None = None,
    *,
    refresh_evidence: bool = False,
) -> None:
    if kind == "object":
        evidence = _object_evidence_metadata(row, sensor_id, source_chart_ids)
    else:
        evidence = _relationship_evidence_metadata(row, sensor_id, object_lookup, source_chart_ids)

    if refresh_evidence or "evidence_metadata" not in row:
        row["evidence_metadata"] = evidence

    # Dual-write: current theme tags are explicitly the orthodox projection.
    if "theme_tags" in row:
        row.setdefault("orthodox_astrology_theme_tags", deepcopy(row.get("theme_tags") or []))

    # Operator primitives remain source-domain material.
    if "semantic_operator_hints" in row:
        row.setdefault("source_operator_hints", deepcopy(row.get("semantic_operator_hints") or []))

    if "relevance_score" in row:
        row.setdefault("orthodox_astrology_relevance_score", row.get("relevance_score"))

    if refresh_evidence:
        row["structural_strength_score"] = structural_strength_score(row)
    else:
        row.setdefault("structural_strength_score", structural_strength_score(row))


def canonicalize_graph(graph: dict[str, Any], *, sensor_id: str, source_chart_ids: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    canonical = deepcopy(graph)
    canonical.pop("projection_profile", None)
    canonical.pop("dual_write_status", None)
    canonical["graph_layer"] = "canonical_source_graph"
    canonical["graph_type"] = "canonical_astrology_graph"
    canonical["graph_version"] = CANONICAL_GRAPH_VERSION
    canonical["source_sensor_id"] = sensor_id
    canonical["sensor_instance_id"] = sensor_id
    canonical["source_chart_ids"] = list(source_chart_ids or [])
    canonical["source_chart_id"] = str((source_chart_ids or [None])[0]) if source_chart_ids else None
    canonical["projection_status"] = "pre_projection"
    _scope_graph_ids_in_place(canonical, canonical.get("source_chart_id"))

    objects = canonical.get("objects", []) or []
    for obj in objects:
        _annotate_row_legacy_and_boundary(obj, sensor_id, "object", source_chart_ids=source_chart_ids, refresh_evidence=True)
        obj.pop("theme_tags", None)
        obj.pop("orthodox_astrology_theme_tags", None)
        obj.pop("relevance_score", None)
        obj.pop("orthodox_astrology_relevance_score", None)
        if "source_operator_hints" in obj:
            obj["operator_hints"] = deepcopy(obj["source_operator_hints"])

    object_lookup = {str(obj.get("id")): obj for obj in objects if obj.get("id") is not None}

    for rel in canonical.get("relationships", []) or []:
        _annotate_row_legacy_and_boundary(
            rel, sensor_id, "relationship", object_lookup, source_chart_ids, refresh_evidence=True
        )
        rel.pop("theme_tags", None)
        rel.pop("orthodox_astrology_theme_tags", None)
        rel.pop("relevance_score", None)
        rel.pop("orthodox_astrology_relevance_score", None)
        if "source_operator_hints" in rel:
            rel["operator_hints"] = deepcopy(rel["source_operator_hints"])

    canonical["boundary_notes"] = {
        "allowed_before_projection": [
            "calculated facts",
            "source astrology objects",
            "source operator primitives",
            "graph topology",
            "provenance",
            "evidence tier and derivation lineage",
            "projection-neutral structural strength",
        ],
        "excluded_from_canonical_graph": [
            "orthodox theme tags",
            "orthodox report claims",
            "consumer report structure",
            "projection-specific salience",
        ],
        "lineage_policy": (
            "Relationship evidence tier and family grouping inherit the root-owner "
            "lineage of source and target objects."
        ),
    }
    return canonical

def structural_evidence_from_graph(
    canonical_graph: dict[str, Any],
    *,
    sensor_id: str,
    source_chart_ids: list[str] | tuple[str, ...] | None = None,
    package: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tier_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    operator_counts: Counter[str] = Counter()
    independence_groups: set[str] = set()
    record_groups: set[str] = set()
    family_groups: set[str] = set()
    source_chart_family_groups: set[str] = set()

    for row in list(canonical_graph.get("objects", []) or []) + list(canonical_graph.get("relationships", []) or []):
        evidence = row.get("evidence_metadata") or {}
        tier_counts[str(evidence.get("evidence_tier") or "unknown")] += 1
        family_counts[str(evidence.get("derivation_family") or "unknown")] += 1
        if evidence.get("independence_group"):
            independence_groups.add(str(evidence["independence_group"]))
        if evidence.get("record_independence_group"):
            record_groups.add(str(evidence["record_independence_group"]))
        if evidence.get("evidence_family_group"):
            family_groups.add(str(evidence["evidence_family_group"]))
        if evidence.get("source_chart_family_group"):
            source_chart_family_groups.add(str(evidence["source_chart_family_group"]))
        for hint in row.get("operator_hints") or row.get("source_operator_hints") or []:
            if isinstance(hint, dict) and hint.get("operator"):
                operator_counts[str(hint["operator"])] += 1
            elif isinstance(hint, str):
                operator_counts[hint] += 1

    activation_groups: list[dict[str, Any]] = []
    if package:
        canonical_object_lookup = {
            str(obj.get("id")): obj
            for obj in canonical_graph.get("objects", []) or []
            if obj.get("id") is not None
        }
        arcs = package.get("transit_arcs") or []
        for arc in arcs:
            evidence = _relationship_evidence_metadata(
                arc, sensor_id, canonical_object_lookup, source_chart_ids
            )
            row = {
                "activation_id": arc.get("arc_id") or f"activation:{_stable_token(sensor_id, arc.get('transit_body'), arc.get('aspect'), arc.get('target_id'))}",
                "source_sensor_id": sensor_id,
                "transit_body": arc.get("transit_body"),
                "aspect": arc.get("aspect"),
                "target_id": arc.get("target_id"),
                "target_type": arc.get("target_type"),
                "start_date": arc.get("start_date"),
                "end_date": arc.get("end_date"),
                "active_days": arc.get("active_days"),
                "evidence_metadata": evidence,
            }
            row["structural_strength_score"] = structural_strength_score({**arc, "evidence_metadata": evidence})
            activation_groups.append(row)

    activation_groups.sort(key=lambda row: (
        -float(row.get("structural_strength_score") or 0),
        str(row.get("activation_id")),
    ))

    return {
        "graph_type": "structural_evidence_graph",
        "graph_version": STRUCTURAL_EVIDENCE_VERSION,
        "source_graph_type": "canonical_astrology_graph",
        "source_sensor_id": sensor_id,
        "sensor_instance_id": sensor_id,
        "source_chart_ids": list(source_chart_ids or []),
        "source_chart_id": str((source_chart_ids or [None])[0]) if source_chart_ids else None,
        "projection_status": "pre_projection",
        "evidence_tier_counts": dict(sorted(tier_counts.items())),
        "derivation_family_counts": dict(sorted(family_counts.items())),
        "independence_group_count": len(independence_groups),
        "record_independence_group_count": len(record_groups),
        "evidence_family_group_count": len(family_groups),
        "source_chart_family_group_count": len(source_chart_family_groups),
        "independence_policy": {
            "record_independence_group": "unique serialized observation or relationship record",
            "evidence_family_group": "collapsed root-owner/source family for anti-double-counting",
            "independence_group": "compatibility alias for evidence_family_group",
        },
        "repeated_operator_families": [
            {"operator": operator, "occurrence_count": count}
            for operator, count in sorted(operator_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "activation_groups": activation_groups,
        "permitted_inferences": [
            "repeated source-operator activation",
            "temporal overlap",
            "sensor/source diversity",
            "evidence tier balance",
            "direct-versus-derived evidence ratios",
        ],
        "deferred_until_projection": [
            "destination-domain meaning",
            "orthodox relationship or personality themes",
            "claim generation",
            "narrative synthesis",
            "consumer-facing confidence",
        ],
    }


def _convert_claim_candidate(claim: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(claim)
    out["claim_status"] = "orthodox_projection_candidate"
    out["projection_profile"] = ORTHODOX_PROFILE_ID
    if "confidence" in out:
        legacy = out.pop("confidence")
        out["legacy_confidence"] = legacy
        out["weighted_support_score"] = legacy
        out["confidence_note"] = (
            "Legacy score represented theme density/relevance, not calibrated "
            "epistemic claim confidence."
        )
    return out


def _orthodox_metrics_for_package(package: dict[str, Any]) -> tuple[list[Any], str]:
    if package.get("theme_metrics") is not None:
        return deepcopy(package.get("theme_metrics") or []), "theme_metrics"
    if package.get("relationship_metrics") is not None:
        return deepcopy(package.get("relationship_metrics") or []), "relationship_metrics"
    return [], "none"


def orthodox_projection_view(package: dict[str, Any], *, source_graph_ref: str) -> dict[str, Any]:
    legacy_claims = package.get("evidence_graph") or []
    metrics, metrics_source = _orthodox_metrics_for_package(package)
    return {
        "view_type": "projected_semantic_view",
        "projection_profile": ORTHODOX_PROFILE_ID,
        "projection_profile_version": ORTHODOX_PROFILE_VERSION,
        "source_graph_ref": source_graph_ref,
        "ontology_policy": "ontology_preserving_with_orthodox_interpretive_annotations",
        "theme_metrics": metrics,
        "metric_source_field": metrics_source,
        "claim_candidates": [_convert_claim_candidate(claim) for claim in legacy_claims],
        "consumer_views": {
            "orthodox_astrology_report_v1": {
                "report_materials": deepcopy(package.get("report_materials") or {}),
            }
        },
        "materialization_notes": {
            "metric_source_field": metrics_source,
            "claim_source_field": "evidence_graph",
            "report_material_source_field": "report_materials",
            "legacy_aliases_serialized": False,
        },
    }



def _synthetic_package_graph(package: dict[str, Any], sensor_id: str, source_chart_ids: list[str] | tuple[str, ...] | None = None) -> dict[str, Any] | None:
    """Build a canonical source graph for package types without chart_graph shape."""
    objects: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    # Synastry: two namespaced object registries plus directional
    # contacts/overlays. Compact registry keys are resolved here for canonical
    # source operators, while orthodox theme registries remain downstream.
    if package.get("natal_synastry"):
        operator_registry = package.get("operator_registry") or {}
        id_maps: dict[str, dict[str, str]] = {"person_a": {}, "person_b": {}}

        for owner, registry in (package.get("object_registries") or {}).items():
            for object_id, source in (registry or {}).items():
                canonical_id = f"synastry:{owner}:{object_id}"
                id_maps.setdefault(owner, {})[str(object_id)] = canonical_id
                row = deepcopy(source)
                row["id"] = canonical_id
                row.setdefault("name", row.get("source_key") or str(object_id))
                row.setdefault("source_key", row.get("name"))
                row.setdefault("object_type", row.get("type") or "unknown")
                row["subject_owner"] = owner
                row["source_registry_object_id"] = str(object_id)
                row.setdefault("facts", {})
                owner_id = _object_owner_ref(row)
                if owner_id:
                    row["owner_object_ref"] = f"synastry:{owner}:{owner_id}"
                row.setdefault("transit_target", False)
                row.setdefault("semantic_operator_hints", [])
                objects.append(row)

        for collection_name, rows in (package.get("natal_synastry") or {}).items():
            direction = "a_to_b" if collection_name.startswith("a_to_b") else "b_to_a"
            source_owner = "person_a" if direction == "a_to_b" else "person_b"
            target_owner = "person_b" if direction == "a_to_b" else "person_a"
            for source in rows or []:
                row = deepcopy(source)
                row.setdefault("id", row.get("relationship_id") or f"synrel:{_stable_token(collection_name, row)}")
                row.setdefault("relationship_type", "HOUSE_OVERLAY" if "overlay" in collection_name else "SYNASTRY_ASPECT")
                raw_source_id = str(row.get("source_object_id") or row.get("source_id") or "unknown")
                raw_target_id = row.get("target_object_id") or row.get("target_id")
                row["source_id"] = id_maps.get(source_owner, {}).get(
                    raw_source_id, f"synastry:{source_owner}:{raw_source_id}"
                )
                if raw_target_id is not None:
                    raw_target_id = str(raw_target_id)
                    row["target_id"] = id_maps.get(target_owner, {}).get(
                        raw_target_id, f"synastry:{target_owner}:{raw_target_id}"
                    )
                else:
                    house_id = f"synastry:{target_owner}:house:{row.get('target_house')}"
                    row["target_id"] = house_id
                    if not any(obj.get("id") == house_id for obj in objects):
                        objects.append({
                            "id": house_id,
                            "name": f"{target_owner} house {row.get('target_house')}",
                            "source_key": f"house:{row.get('target_house')}",
                            "object_type": "house_cusp",
                            "subject_owner": target_owner,
                            "facts": {"house": row.get("target_house")},
                            "transit_target": False,
                            "semantic_operator_hints": [],
                        })

                operator_key = row.get("operator_key")
                if operator_key and operator_key in operator_registry:
                    row["semantic_operator_hints"] = deepcopy(operator_registry[operator_key])
                    row["operator_registry_ref"] = str(operator_key)
                else:
                    row.setdefault("semantic_operator_hints", [])
                row["source_collection"] = collection_name
                relationships.append(row)

    # Lunar-return range: each return is a time-event node and each nested
    # return chart is canonicalized into a registry for later projection.
    elif package.get("returns") is not None:
        target_id = ((package.get("target") or {}).get("chart_identity") or {}).get("chart_id")
        if target_id:
            objects.append({
                "id": str(target_id),
                "name": ((package.get("target") or {}).get("chart_identity") or {}).get("label") or str(target_id),
                "source_key": str(target_id),
                "object_type": "timing_target",
                "facts": deepcopy((package.get("target") or {}).get("chart_identity") or {}),
                "transit_target": False,
                "semantic_operator_hints": [],
            })
        return_chart_registry: dict[str, dict[str, Any]] = {}
        for ret in package.get("returns") or []:
            event = ret.get("return_event") or {}
            rid = str(ret.get("return_id"))
            objects.append({
                "id": rid,
                "name": f"Lunar Return {ret.get('sequence')}",
                "source_key": rid,
                "object_type": "timing_event",
                "facts": deepcopy(event),
                "transit_target": False,
                "semantic_operator_hints": [],
            })
            if target_id:
                relationships.append({
                    "id": f"rel:return:{_stable_token(target_id, rid)}",
                    "relationship_type": "LUNAR_RETURN_OF",
                    "source_id": rid,
                    "target_id": str(target_id),
                    "source_name": f"Lunar Return {ret.get('sequence')}",
                    "target_name": str(target_id),
                    "semantic_operator_hints": [{"operator": "return", "role": "timing_relation"}],
                })

            return_chart = ret.get("return_chart") or {}
            nested_graph = return_chart.get("semantic_graph")
            if isinstance(nested_graph, dict) and nested_graph.get("objects") is not None:
                return_chart_registry[rid] = canonicalize_graph(
                    nested_graph,
                    sensor_id=f"{sensor_id}:return:{rid}",
                    source_chart_ids=source_chart_ids,
                )

    # Eclipse/lunation range.
    elif package.get("events") is not None:
        target_id = ((package.get("target") or {}).get("chart_id")) if isinstance(package.get("target"), dict) else None
        for event in package.get("events") or []:
            event_id = str(event.get("event_id"))
            objects.append({
                "id": event_id,
                "name": str(event.get("event_type") or "lunation"),
                "source_key": event_id,
                "object_type": "timing_event",
                "facts": {k: deepcopy(event.get(k)) for k in (
                    "event_type", "event_utc", "lunation_lon", "node_distance",
                    "is_eclipse_window", "eclipse_type", "activation_window"
                )},
                "transit_target": False,
                "semantic_operator_hints": [{"operator": "activate", "role": "timing_event"}],
            })
            for contact in event.get("target_aspects") or []:
                relationships.append({
                    **deepcopy(contact),
                    "id": f"rel:lunation:{_stable_token(event_id, contact.get('target_id'), contact.get('aspect'))}",
                    "relationship_type": "LUNATION_ACTIVATION",
                    "source_id": event_id,
                    "target_id": contact.get("target_id"),
                    "source_name": str(event.get("event_type") or "lunation"),
                    "target_name": contact.get("target_name"),
                })

    # Annual profection.
    elif package.get("profection") is not None:
        prof = package.get("profection") or {}
        target_id = ((package.get("target") or {}).get("chart_identity") or {}).get("chart_id")
        event_id = f"profection:{target_id}:{prof.get('target_date')}"
        objects.append({
            "id": event_id,
            "name": "Annual Profection",
            "source_key": event_id,
            "object_type": "timing_event",
            "facts": deepcopy(prof),
            "transit_target": False,
            "semantic_operator_hints": [{"operator": "foreground", "role": "timing_relation"}],
        })
        if target_id:
            relationships.append({
                "id": f"rel:profection:{_stable_token(event_id, target_id)}",
                "relationship_type": "ANNUAL_PROFECTION_OF",
                "source_id": event_id,
                "target_id": str(target_id),
                "source_name": "Annual Profection",
                "target_name": str(target_id),
                "semantic_operator_hints": [{"operator": "foreground", "role": "timing_relation"}],
            })

    if not objects and not relationships:
        return None

    graph = {
        "graph_type": "canonical_astrology_graph",
        "graph_version": CANONICAL_GRAPH_VERSION,
        "source_sensor_id": sensor_id,
        "sensor_instance_id": sensor_id,
        "source_chart_ids": list(source_chart_ids or []),
        "source_chart_id": str((source_chart_ids or [None])[0]) if source_chart_ids else None,
        "projection_status": "pre_projection",
        "objects": objects,
        "relationships": relationships,
        "summary": {
            "object_count": len(objects),
            "relationship_count": len(relationships),
            "synthetic_package_graph": True,
        },
        "indexes": {
            "object_by_id": {str(obj.get("id")): i for i, obj in enumerate(objects)},
            "relationship_by_id": {str(rel.get("id")): i for i, rel in enumerate(relationships)},
        },
    }
    if "return_chart_registry" in locals() and return_chart_registry:
        graph["nested_canonical_graph_registry"] = return_chart_registry
        graph["summary"]["nested_canonical_graph_count"] = len(return_chart_registry)
    return graph

def _find_graph(package: dict[str, Any]) -> dict[str, Any] | None:
    direct = package.get("semantic_graph")
    if isinstance(direct, dict) and direct.get("objects") is not None:
        return direct

    for key in ("natal", "composite_chart", "davison_chart", "return_chart", "chart"):
        child = package.get(key)
        if isinstance(child, dict):
            graph = child.get("semantic_graph")
            if isinstance(graph, dict) and graph.get("objects") is not None:
                return graph
    return None


def _sensor_id(package: dict[str, Any]) -> str:
    return str(_semantic_identity(package)["sensor_instance_id"])


def _dual_annotate_graph(graph: dict[str, Any], sensor_id: str, source_chart_ids: list[str] | tuple[str, ...] | None = None) -> None:
    graph.setdefault("graph_layer", "legacy_semantic_graph")
    graph.setdefault("projection_profile", ORTHODOX_PROFILE_ID)
    graph.setdefault("dual_write_status", "temporary_chunk_1_inspection_cycle")
    objects = graph.get("objects", []) or []
    for obj in objects:
        _annotate_row_legacy_and_boundary(
            obj, sensor_id, "object", source_chart_ids=source_chart_ids, refresh_evidence=True
        )
    object_lookup = {
        str(obj.get("id")): obj for obj in objects if obj.get("id") is not None
    }
    for rel in graph.get("relationships", []) or []:
        _annotate_row_legacy_and_boundary(
            rel,
            sensor_id,
            "relationship",
            object_lookup,
            source_chart_ids,
            refresh_evidence=True,
        )



def _annotate_projection_fields_recursive(value: Any, sensor_id: str, source_chart_ids: list[str] | tuple[str, ...] | None = None) -> None:
    """Dual-write namespaced orthodox fields throughout package payloads.

    This catches compact contact/aspect/candidate rows that are not members of
    the chart graph itself.
    """
    if isinstance(value, list):
        for item in value:
            _annotate_projection_fields_recursive(item, sensor_id, source_chart_ids)
        return
    if not isinstance(value, dict):
        return

    looks_like_relation = bool(
        value.get("aspect")
        or value.get("relationship_type")
        or value.get("transit_body")
        or value.get("source_object_id")
        or value.get("target_object_id")
    )
    if "theme_tags" in value:
        value.setdefault("orthodox_astrology_theme_tags", deepcopy(value.get("theme_tags") or []))
    if "semantic_operator_hints" in value:
        value.setdefault("source_operator_hints", deepcopy(value.get("semantic_operator_hints") or []))
    if "relevance_score" in value:
        value.setdefault("orthodox_astrology_relevance_score", value.get("relevance_score"))
    if looks_like_relation:
        value.setdefault("evidence_metadata", _relationship_evidence_metadata(value, sensor_id, source_chart_ids=source_chart_ids))
        value.setdefault("structural_strength_score", structural_strength_score(value))

    for child in value.values():
        if isinstance(child, (dict, list)):
            _annotate_projection_fields_recursive(child, sensor_id, source_chart_ids)


LEGACY_SEMANTIC_ALIAS_FIELDS = (
    "semantic_graph",
    "theme_metrics",
    "relationship_metrics",
    "evidence_graph",
    "report_materials",
)


def canonical_graph_from_package(package: dict[str, Any]) -> dict[str, Any]:
    return package.get("canonical_astrology_graph") or _find_graph(package) or {}


def orthodox_view_from_package(package: dict[str, Any]) -> dict[str, Any]:
    return (package.get("projection_views") or {}).get(ORTHODOX_PROFILE_ID) or {}


def orthodox_metrics_from_package(package: dict[str, Any]) -> list[Any]:
    return list(orthodox_view_from_package(package).get("theme_metrics") or [])


def orthodox_claims_from_package(package: dict[str, Any]) -> list[dict[str, Any]]:
    return list(orthodox_view_from_package(package).get("claim_candidates") or [])


def orthodox_report_materials_from_package(package: dict[str, Any]) -> dict[str, Any]:
    return dict(
        (
            (orthodox_view_from_package(package).get("consumer_views") or {})
            .get("orthodox_astrology_report_v1", {})
            .get("report_materials")
        )
        or {}
    )


def _strip_nested_semantic_graphs(value: Any) -> None:
    """Remove duplicate legacy graph payloads after canonicalization."""
    if isinstance(value, list):
        for item in value:
            _strip_nested_semantic_graphs(item)
        return
    if not isinstance(value, dict):
        return
    value.pop("semantic_graph", None)
    for child in list(value.values()):
        if isinstance(child, (dict, list)):
            _strip_nested_semantic_graphs(child)


def _apply_full_materialization_policy(package: dict[str, Any]) -> None:
    for field in LEGACY_SEMANTIC_ALIAS_FIELDS:
        package.pop(field, None)
    _strip_nested_semantic_graphs(package)
    metadata = package.setdefault("metadata", {})
    metadata["materialization_policy"] = "full_canonical_projection_v1"
    metadata["legacy_semantic_aliases_materialized"] = False



def orthodox_row_annotation(row: dict[str, Any]) -> dict[str, Any]:
    """Return a report-facing orthodox annotation without mutating canonical data."""
    projected = deepcopy(row)
    source = (
        row.get("source_name")
        or row.get("source")
        or row.get("source_key")
        or row.get("transit_body")
    )
    target = (
        row.get("target_name")
        or row.get("target")
        or row.get("target_key")
        or row.get("natal_target_name")
        or row.get("natal_target")
    )
    aspect = row.get("aspect")
    tags = theme_tags(source, target, aspect=aspect)
    projected["theme_tags"] = tags
    projected["orthodox_astrology_theme_tags"] = list(tags)
    if row.get("operator_hints") and not projected.get("semantic_operator_hints"):
        projected["semantic_operator_hints"] = deepcopy(row.get("operator_hints") or [])
    elif row.get("source_operator_hints") and not projected.get("semantic_operator_hints"):
        projected["semantic_operator_hints"] = deepcopy(
            row.get("source_operator_hints") or []
        )
    return projected


def orthodox_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [orthodox_row_annotation(row) for row in rows]

def finalize_package_semantic_boundary(package: dict[str, Any]) -> dict[str, Any]:
    """Materialize canonical, structural, and explicit projection layers.

    The function is idempotent. Temporary legacy aliases are removed from the
    serialized package after their canonical/projection equivalents exist.
    """
    if not isinstance(package, dict):
        return package

    identity = _semantic_identity(package)
    sensor_id = str(identity["sensor_instance_id"])
    source_chart_ids = list(identity["source_chart_ids"])

    existing_canonical = package.get("canonical_astrology_graph")
    previous_canonical_source_chart_id = str(
        (existing_canonical or {}).get("source_chart_id") or ""
    )
    previous_canonical_sensor_id = str(
        (existing_canonical or {}).get("sensor_instance_id") or previous_canonical_source_chart_id
    )
    graph = None if existing_canonical else _find_graph(package)
    synthetic_graph = (
        None
        if (existing_canonical is not None or graph is not None)
        else _synthetic_package_graph(package, sensor_id, source_chart_ids)
    )

    # Orthodox projection material must be captured before legacy aliases are
    # removed. Refresh it on every call so finalization remains idempotent.
    if (
        package.get("theme_metrics") is not None
        or package.get("relationship_metrics") is not None
        or package.get("evidence_graph") is not None
        or package.get("report_materials") is not None
    ):
        package.setdefault("projection_views", {})
        has_legacy_projection_sources = any(
            field in package
            for field in (
                "theme_metrics",
                "relationship_metrics",
                "evidence_graph",
                "report_materials",
            )
        )
        if (
            ORTHODOX_PROFILE_ID not in package["projection_views"]
            or has_legacy_projection_sources
        ):
            package["projection_views"][ORTHODOX_PROFILE_ID] = orthodox_projection_view(
                package,
                source_graph_ref=(
                    "canonical_astrology_graph"
                    if (
                        existing_canonical is not None
                        or graph is not None
                        or synthetic_graph is not None
                    )
                    else "source_package"
                ),
            )

    _annotate_projection_fields_recursive(package, sensor_id, source_chart_ids)

    metadata = package.setdefault("metadata", {})
    metadata["semantic_boundary_version"] = "chunk1.5.v1"
    metadata["source_chart_id"] = identity["source_chart_id"]
    metadata["source_chart_ids"] = source_chart_ids
    metadata["sensor_instance_id"] = sensor_id
    metadata["semantic_identity_version"] = identity["identity_version"]
    metadata["canonical_graph_contract"] = "canonical_astrology_graph.v1"
    metadata["default_projection_profile"] = ORTHODOX_PROFILE_ID
    metadata["dual_write_legacy_semantics"] = False

    canonical: dict[str, Any] | None = None
    canonical_ref_map: dict[str, str] = {}
    if existing_canonical is not None:
        canonical = existing_canonical
        canonical_ref_map = _scope_graph_ids_in_place(
            canonical,
            str(identity["source_chart_id"] or ""),
        )
    elif graph is not None:
        canonical_ref_map = _scope_graph_ids_in_place(
            graph,
            str(identity["source_chart_id"] or ""),
        )
        _dual_annotate_graph(graph, sensor_id, source_chart_ids)
        canonical = canonicalize_graph(
            graph,
            sensor_id=sensor_id,
            source_chart_ids=source_chart_ids,
        )
    elif synthetic_graph is not None:
        canonical = synthetic_graph
        canonical_ref_map = _scope_graph_ids_in_place(
            canonical,
            str(identity["source_chart_id"] or ""),
        )
        canonical["graph_layer"] = "canonical_source_graph"
        objects = canonical.get("objects", []) or []
        for obj in objects:
            _annotate_row_legacy_and_boundary(
                obj,
                sensor_id,
                "object",
                source_chart_ids=source_chart_ids,
                refresh_evidence=True,
            )
            obj.pop("theme_tags", None)
            obj.pop("orthodox_astrology_theme_tags", None)
            obj.pop("relevance_score", None)
            obj.pop("orthodox_astrology_relevance_score", None)
            if "source_operator_hints" in obj:
                obj["operator_hints"] = deepcopy(obj["source_operator_hints"])

        object_lookup = {
            str(obj.get("id")): obj for obj in objects if obj.get("id") is not None
        }
        for rel in canonical.get("relationships", []) or []:
            _annotate_row_legacy_and_boundary(
                rel,
                sensor_id,
                "relationship",
                object_lookup,
                source_chart_ids,
                refresh_evidence=True,
            )
            rel.pop("theme_tags", None)
            rel.pop("orthodox_astrology_theme_tags", None)
            rel.pop("relevance_score", None)
            rel.pop("orthodox_astrology_relevance_score", None)
            if "source_operator_hints" in rel:
                rel["operator_hints"] = deepcopy(rel["source_operator_hints"])

    if canonical is not None:
        if canonical_ref_map:
            rewritten = _rewrite_exact_refs(package, canonical_ref_map)
            package.clear()
            package.update(rewritten)
            canonical = package.get("canonical_astrology_graph") or canonical
        if (
            previous_canonical_source_chart_id
            and previous_canonical_source_chart_id != identity["source_chart_id"]
        ):
            _refresh_rescoped_identity_provenance(
                package,
                previous_source_chart_id=previous_canonical_source_chart_id,
                source_chart_id=str(identity["source_chart_id"]),
                previous_sensor_id=previous_canonical_sensor_id,
                sensor_id=sensor_id,
            )
        canonical["source_chart_id"] = identity["source_chart_id"]
        canonical["source_chart_ids"] = source_chart_ids
        canonical["sensor_instance_id"] = sensor_id
        canonical.setdefault("identity_policy", {})["source_chart_id"] = identity["source_chart_id"]
        _dual_annotate_graph(canonical, sensor_id, source_chart_ids)
        _rebuild_graph_indexes(canonical)
        package["canonical_astrology_graph"] = canonical
        package["structural_evidence_graph"] = structural_evidence_from_graph(
            canonical,
            sensor_id=sensor_id,
            source_chart_ids=source_chart_ids,
            package=package,
        )

    _apply_full_materialization_policy(package)

    has_graph = canonical is not None
    package["semantic_boundary"] = {
        "canonical_layer": "canonical_astrology_graph" if has_graph else None,
        "structural_layer": "structural_evidence_graph" if has_graph else None,
        "default_projection_view": f"projection_views.{ORTHODOX_PROFILE_ID}",
        "source_chart_id": identity["source_chart_id"],
        "source_chart_ids": source_chart_ids,
        "sensor_instance_id": sensor_id,
        "semantic_identity_version": identity["identity_version"],
        "legacy_fields_dual_written": False,
        "legacy_removal_status": "completed_chunk1.5",
        "materialization_policy": "full_canonical_projection_v1",
    }
    return package


def rescope_natal_package_source_chart_id(
    package: dict[str, Any],
    source_chart_id: str,
) -> dict[str, Any]:
    """Deliberately migrate a finalized Natal package to a new chart identity."""
    metadata = package.get("metadata") if isinstance(package.get("metadata"), dict) else {}
    if str(metadata.get("analysis_type") or "") != "natal_dataset":
        raise ValueError("Source chart identity rescoping currently supports Natal packages only")

    # Validate the existing carrier set before modifying it, so this helper
    # never conceals a pre-existing identity conflict.
    _semantic_identity(package)
    new_source_chart_id = resolve_explicit_source_chart_id(
        (("source_chart_id", source_chart_id),)
    )
    assert new_source_chart_id is not None

    package.setdefault("metadata", {})["source_chart_id"] = new_source_chart_id
    for alias in ("target_chart_id", "chart_id"):
        if alias in package["metadata"]:
            package["metadata"][alias] = new_source_chart_id

    for field in ("person", "natal"):
        value = package.get(field)
        if isinstance(value, dict):
            value["source_chart_id"] = new_source_chart_id

    transitable_identity = (
        (package.get("transitable_chart") or {}).get("chart_identity")
        if isinstance(package.get("transitable_chart"), dict)
        else None
    )
    if isinstance(transitable_identity, dict):
        transitable_identity["chart_id"] = new_source_chart_id

    return finalize_package_semantic_boundary(package)


def finalize_view_semantic_boundary(
    view: dict[str, Any],
    source_package: dict[str, Any],
) -> dict[str, Any]:
    """Attach compact boundary summaries and explicit projection material."""
    finalize_package_semantic_boundary(source_package)

    for field in LEGACY_SEMANTIC_ALIAS_FIELDS:
        view.pop(field, None)

    view["semantic_boundary"] = deepcopy(
        source_package.get("semantic_boundary") or {}
    )
    view_metadata = view.setdefault("metadata", {})
    source_metadata = source_package.get("metadata") or {}
    for key in (
        "source_chart_id",
        "source_chart_ids",
        "sensor_instance_id",
        "semantic_identity_version",
        "semantic_boundary_version",
    ):
        if source_metadata.get(key) is not None:
            view_metadata[key] = deepcopy(source_metadata[key])

    view_type = str(view.get("view_type") or view_metadata.get("view_type") or "")
    is_streaming = "streaming" in view_type
    view_metadata["materialization_policy"] = (
        "streaming_registry_summary_v1"
        if is_streaming
        else "analysis_projection_summary_v1"
    )
    view_metadata["legacy_semantic_aliases_materialized"] = False

    graph = source_package.get("canonical_astrology_graph") or {}
    if graph:
        view["canonical_astrology_graph_summary"] = {
            "graph_type": graph.get("graph_type"),
            "graph_version": graph.get("graph_version"),
            "source_sensor_id": graph.get("source_sensor_id"),
            "sensor_instance_id": graph.get("sensor_instance_id"),
            "source_chart_id": graph.get("source_chart_id"),
            "source_chart_ids": deepcopy(graph.get("source_chart_ids") or []),
            "object_count": len(graph.get("objects", []) or []),
            "relationship_count": len(graph.get("relationships", []) or []),
            "nested_canonical_graph_count": len(
                graph.get("nested_canonical_graph_registry", {}) or {}
            ),
        }

    structural = source_package.get("structural_evidence_graph") or {}
    if structural:
        view["structural_evidence_summary"] = {
            "graph_type": structural.get("graph_type"),
            "graph_version": structural.get("graph_version"),
            "independence_group_count": structural.get("independence_group_count"),
            "record_independence_group_count": structural.get(
                "record_independence_group_count"
            ),
            "evidence_family_group_count": structural.get(
                "evidence_family_group_count"
            ),
            "source_chart_family_group_count": structural.get(
                "source_chart_family_group_count"
            ),
            "evidence_tier_counts": deepcopy(
                structural.get("evidence_tier_counts") or {}
            ),
            "derivation_family_counts": deepcopy(
                structural.get("derivation_family_counts") or {}
            ),
        }

    projected_views = source_package.get("projection_views") or {}
    if projected_views:
        summaries = {}
        for profile_id, projected in projected_views.items():
            summaries[profile_id] = {
                "view_type": projected.get("view_type"),
                "projection_profile": projected.get("projection_profile"),
                "projection_profile_version": projected.get(
                    "projection_profile_version"
                ),
                "source_graph_ref": projected.get("source_graph_ref"),
                "theme_metric_count": len(projected.get("theme_metrics") or []),
                "claim_candidate_count": len(
                    projected.get("claim_candidates") or []
                ),
                "metric_source_field": projected.get("metric_source_field"),
                "consumer_view_ids": sorted(
                    (projected.get("consumer_views") or {}).keys()
                ),
            }
        view["projection_view_summaries"] = summaries
        view.pop("projection_views", None)

    return view
