from __future__ import annotations

import hashlib
import logging
from typing import Any

from astro_analysis_sdk.common.aspects import find_aspect, relevance_score
from astro_analysis_sdk.common.geometry import deg_to_sign, format_zodiac, normalize, house_for_lon
from astro_analysis_sdk.common.io import clean_body_name
from astro_analysis_sdk.common.themes import operator_hints, theme_tags

GRAPH_SCHEMA_VERSION = "1.2.0"

logger = logging.getLogger(__name__)

# Canonical relationship ontology. Keep these stable; downstream consumers should
# branch on these values rather than ad-hoc labels embedded in facts.
REL_ASPECT = "ASPECT"
REL_ANTISCIA = "ANTISCIA"
REL_CONTRA_ANTISCIA = "CONTRA_ANTISCIA"
REL_DECLINATION_PARALLEL = "DECLINATION_PARALLEL"
REL_DECLINATION_CONTRAPARALLEL = "DECLINATION_CONTRAPARALLEL"
REL_HARMONIC_PROJECTION = "HARMONIC_PROJECTION"
REL_TRANSIT_ACTIVATION = "TRANSIT_ACTIVATION"
REL_HAS_DIGNITY = "HAS_DIGNITY"
REL_HAS_DECLINATION = "HAS_DECLINATION"
REL_HAS_ANTISCIA_POINT = "HAS_ANTISCIA_POINT"
REL_HAS_CONTRA_ANTISCIA_POINT = "HAS_CONTRA_ANTISCIA_POINT"
REL_HAS_HARMONIC_POINT = "HAS_HARMONIC_POINT"
REL_HAS_SECT = "HAS_SECT"
REL_LOT_DERIVED_FROM = "LOT_DERIVED_FROM"
REL_FIXED_STAR_CONJUNCTION = "FIXED_STAR_CONJUNCTION"
REL_ACTIVATES_NATAL_RELATIONSHIP = "ACTIVATES_NATAL_RELATIONSHIP"
REL_SYNASTRY_ASPECT = "SYNASTRY_ASPECT"
REL_HOUSE_OVERLAY = "HOUSE_OVERLAY"
REL_COMPOSITE_ASPECT = "COMPOSITE_ASPECT"

RELATIONSHIP_TYPES = {
    REL_ASPECT,
    REL_ANTISCIA,
    REL_CONTRA_ANTISCIA,
    REL_DECLINATION_PARALLEL,
    REL_DECLINATION_CONTRAPARALLEL,
    REL_HARMONIC_PROJECTION,
    REL_TRANSIT_ACTIVATION,
    REL_HAS_DIGNITY,
    REL_HAS_DECLINATION,
    REL_HAS_ANTISCIA_POINT,
    REL_HAS_CONTRA_ANTISCIA_POINT,
    REL_HAS_HARMONIC_POINT,
    REL_HAS_SECT,
    REL_LOT_DERIVED_FROM,
    REL_FIXED_STAR_CONJUNCTION,
    REL_ACTIVATES_NATAL_RELATIONSHIP,
    REL_SYNASTRY_ASPECT,
    REL_HOUSE_OVERLAY,
    REL_COMPOSITE_ASPECT,
}

LEGACY_RELATIONSHIP_TYPE_ALIASES = {
    "aspect": REL_ASPECT,
    "antiscia": REL_ANTISCIA,
    "contra_antiscia": REL_CONTRA_ANTISCIA,
    "declination_aspect": REL_DECLINATION_PARALLEL,
    "parallel": REL_DECLINATION_PARALLEL,
    "contra-parallel": REL_DECLINATION_CONTRAPARALLEL,
    "contra_parallel": REL_DECLINATION_CONTRAPARALLEL,
    "harmonic_projection": REL_HARMONIC_PROJECTION,
    "transit_to_natal_object_aspect": REL_TRANSIT_ACTIVATION,
    "dignity": REL_HAS_DIGNITY,
    "declination": REL_HAS_DECLINATION,
    "sect": REL_HAS_SECT,
    "lot": REL_LOT_DERIVED_FROM,
}

TRANSIT_TARGET_TYPES = {
    "planet_or_point",
    "angle",
    "angle_point",
    "calculated_point",
    "lot",
    "fixed_star",
    "antiscia_point",
    "contra_antiscia_point",
    "harmonic_point",
}


def canonical_relationship_type(value: str | None) -> str:
    if not value:
        return REL_ASPECT
    raw = str(value)
    upper = raw.upper().replace("-", "_")
    if upper in RELATIONSHIP_TYPES:
        return upper
    return LEGACY_RELATIONSHIP_TYPE_ALIASES.get(raw, LEGACY_RELATIONSHIP_TYPE_ALIASES.get(raw.lower(), upper))


def _safe_token(value: object) -> str:
    return str(value).replace(" ", "_").replace("/", "_").replace(":", "_")


def _object_id(name: str) -> str:
    clean = _safe_token(clean_body_name(name))
    return f"natal:{clean}"


def _aux_object_id(kind: str, owner: str, qualifier: object | None = None) -> str:
    parts = [kind, _safe_token(owner)]
    if qualifier is not None:
        parts.append(_safe_token(qualifier))
    return ":".join(parts)


def _as_lon(value: Any) -> float | None:
    try:
        return normalize(float(value))
    except Exception:
        return None


def semantic_payload(*tokens: object, aspect: str | None = None) -> dict[str, Any]:
    return {
        "theme_tags": theme_tags(*tokens, aspect=aspect),
        "semantic_operator_hints": operator_hints(*tokens, aspect=aspect),
    }


def _make_object(
    *,
    object_id: str,
    name: str,
    source_key: str,
    object_type: str,
    longitude: float | None = None,
    facts: dict[str, Any] | None = None,
    transit_target: bool | None = None,
    **extra: Any,
) -> dict[str, Any]:
    facts = facts or {}
    obj: dict[str, Any] = {
        "id": object_id,
        "name": name,
        "source_key": source_key,
        "object_type": object_type,
        "facts": facts,
        "transit_target": (object_type in TRANSIT_TARGET_TYPES) if transit_target is None else transit_target,
        **semantic_payload(name, object_type),
    }
    if longitude is not None:
        lon = normalize(longitude)
        sign_info = deg_to_sign(lon)
        obj.update({
            "longitude": lon,
            "pretty": facts.get("pretty") or format_zodiac(lon),
            "sign": sign_info["sign"],
            "sign_degree": sign_info["sign_degree"],
        })
    obj.update(extra)
    return obj


def _relationship(rel_type: str, source: dict[str, Any], target: dict[str, Any], **extra: Any) -> dict[str, Any]:
    canonical_type = canonical_relationship_type(rel_type)
    aspect = extra.get("aspect")
    return {
        "id": f"{canonical_type}:{source['id']}->{target['id']}:{extra.get('qualifier', '')}",
        "relationship_type": canonical_type,
        "legacy_relationship_type": rel_type if rel_type != canonical_type else None,
        "source_id": source["id"],
        "source_name": source["name"],
        "target_id": target["id"],
        "target_name": target["name"],
        **{k: v for k, v in extra.items() if k != "qualifier"},
        **semantic_payload(source["name"], target["name"], aspect=aspect),
    }


def build_chart_objects(natal: dict[str, Any]) -> list[dict[str, Any]]:
    logger.debug("Building chart graph objects for person=%s", natal.get("person"))
    objects: list[dict[str, Any]] = []
    core_objects: list[dict[str, Any]] = []

    for key, body in natal.get("bodies", {}).items():
        lon = _as_lon(body.get("lon"))
        if lon is None:
            continue
        clean = clean_body_name(key)
        obj_type = body.get("type", "planet_or_point")
        obj = _make_object(
            object_id=_object_id(key),
            name=clean,
            source_key=key,
            object_type=obj_type,
            longitude=lon,
            facts=body,
            house=body.get("house"),
            retrograde=body.get("retrograde", False),
            declination=body.get("declination"),
            right_ascension=body.get("right_ascension"),
        )
        objects.append(obj)
        core_objects.append(obj)

    for lot_name, lot in natal.get("lots", {}).items():
        lon = _as_lon(lot.get("lon"))
        if lon is None:
            continue
        key = f"n{lot_name}"
        obj = _make_object(
            object_id=_object_id(key),
            name=lot_name,
            source_key=key,
            object_type="lot",
            longitude=lon,
            facts=lot,
            house=lot.get("house"),
            retrograde=False,
            transit_target=True,
        )
        objects.append(obj)
        core_objects.append(obj)

    for star in natal.get("fixed_stars", []) or []:
        lon = _as_lon(star.get("lon"))
        if lon is None:
            continue
        name = str(star.get("name", "Fixed Star"))
        objects.append(_make_object(
            object_id=f"fixed_star:{_safe_token(name)}",
            name=name,
            source_key=name,
            object_type="fixed_star",
            longitude=lon,
            facts=star,
            house=star.get("house"),
            declination=star.get("declination"),
            right_ascension=star.get("right_ascension"),
            transit_target=True,
        ))

    # Promote previously nested body facts to first-class graph objects.
    for body in core_objects:
        facts = body.get("facts", {}) or {}
        if facts.get("dignity"):
            objects.append(_make_object(
                object_id=_aux_object_id("dignity", body["id"]),
                name=f"{body['name']} dignity",
                source_key=f"{body['source_key']}:dignity",
                object_type="dignity_state",
                facts=facts["dignity"],
                transit_target=False,
            ))
        if facts.get("declination") is not None:
            objects.append(_make_object(
                object_id=_aux_object_id("declination", body["id"]),
                name=f"{body['name']} declination",
                source_key=f"{body['source_key']}:declination",
                object_type="declination_position",
                facts={
                    "declination": facts.get("declination"),
                    "declination_pretty": facts.get("declination_pretty"),
                    "right_ascension": facts.get("right_ascension"),
                },
                transit_target=False,
            ))
        anti = facts.get("antiscia") or {}
        for obj_type, lon_key, pretty_key in (
            ("antiscia_point", "antiscia_lon", "antiscia_pretty"),
            ("contra_antiscia_point", "contra_antiscia_lon", "contra_antiscia_pretty"),
        ):
            lon = _as_lon(anti.get(lon_key))
            if lon is not None:
                objects.append(_make_object(
                    object_id=_aux_object_id(obj_type, body["id"]),
                    name=f"{body['name']} {obj_type.replace('_', ' ')}",
                    source_key=f"{body['source_key']}:{obj_type}",
                    object_type=obj_type,
                    longitude=lon,
                    facts={"lon": lon, "pretty": anti.get(pretty_key) or format_zodiac(lon), "owner_id": body["id"]},
                    house=None,
                    transit_target=True,
                ))
        for number, h in (facts.get("harmonics") or {}).items():
            lon = _as_lon(h.get("lon"))
            if lon is not None:
                objects.append(_make_object(
                    object_id=_aux_object_id("harmonic", body["id"], number),
                    name=f"{body['name']} harmonic {number}",
                    source_key=f"{body['source_key']}:harmonic:{number}",
                    object_type="harmonic_point",
                    longitude=lon,
                    facts={"harmonic": int(number), "lon": lon, "pretty": h.get("pretty") or format_zodiac(lon), "owner_id": body["id"]},
                    house=None,
                    transit_target=True,
                ))

    sect = natal.get("sect") or {}
    if sect:
        objects.append(_make_object(
            object_id="sect:chart",
            name="Chart sect",
            source_key="sect",
            object_type="sect_state",
            facts=sect,
            transit_target=False,
        ))

    logger.debug("Built %d chart graph objects", len(objects))
    return objects


def _by_source_and_id(objects: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    return {obj["source_key"]: obj for obj in objects}, {obj["id"]: obj for obj in objects}


def build_chart_relationships(objects: list[dict[str, Any]], natal: dict[str, Any]) -> list[dict[str, Any]]:
    logger.debug("Building chart graph relationships for %d objects", len(objects))
    by_key, by_id = _by_source_and_id(objects)
    rels: list[dict[str, Any]] = []

    for aspect_bucket in ("natal_planet_aspects", "natal_planet_angle_aspects", "natal_planet_point_aspects"):
        for asp in natal.get(aspect_bucket, []) or []:
            src = by_key.get(f"n{asp.get('source_body')}")
            tgt = by_key.get(f"n{asp.get('target_body')}")
            if src and tgt:
                rels.append(_relationship(REL_ASPECT, src, tgt, qualifier=asp.get("id"), **asp))

    aspect_existing = {(r["source_id"], r["target_id"], r.get("aspect")) for r in rels}
    longitude_objects = [obj for obj in objects if obj.get("longitude") is not None and obj.get("object_type") not in {"dignity_state", "declination_position", "sect_state"}]
    for i, src in enumerate(longitude_objects):
        for tgt in longitude_objects[i + 1:]:
            if src["object_type"] == "fixed_star" and tgt["object_type"] == "fixed_star":
                continue
            asp = find_aspect(src["name"], src["longitude"], tgt["name"], tgt["longitude"], include_minor=True)
            if not asp:
                continue
            key = (src["id"], tgt["id"], asp["aspect"])
            if key in aspect_existing:
                continue
            rel_type = REL_FIXED_STAR_CONJUNCTION if (src["object_type"] == "fixed_star" or tgt["object_type"] == "fixed_star") and asp["aspect"] == "conjunction" else REL_ASPECT
            rels.append(_relationship(
                rel_type,
                src,
                tgt,
                qualifier=f"generated:{asp.get('aspect')}:{src['id']}:{tgt['id']}",
                source_body=src["name"],
                target_body=tgt["name"],
                generated=True,
                weight=relevance_score(src["name"], f"n{tgt['name']}", asp),
                **asp,
            ))

    # Link bodies to promoted first-class facts/points.
    for body in objects:
        if body.get("source_key", "").startswith("n") and body["object_type"] in TRANSIT_TARGET_TYPES:
            for rel_type, obj_type in (
                (REL_HAS_DIGNITY, "dignity"),
                (REL_HAS_DECLINATION, "declination"),
                (REL_HAS_ANTISCIA_POINT, "antiscia_point"),
                (REL_HAS_CONTRA_ANTISCIA_POINT, "contra_antiscia_point"),
            ):
                target = by_id.get(_aux_object_id(obj_type, body["id"]))
                if target:
                    rels.append(_relationship(rel_type, body, target, qualifier=obj_type))
            for target in objects:
                if target.get("object_type") == "harmonic_point" and target.get("facts", {}).get("owner_id") == body["id"]:
                    rels.append(_relationship(REL_HAS_HARMONIC_POINT, body, target, qualifier=target.get("facts", {}).get("harmonic"), harmonic=target.get("facts", {}).get("harmonic")))

    sect_obj = by_id.get("sect:chart")
    if sect_obj:
        for key in ("nSun", "nMoon"):
            if key in by_key:
                rels.append(_relationship(REL_HAS_SECT, by_key[key], sect_obj, qualifier=key))

    for lot_name in (natal.get("lots") or {}):
        lot_obj = by_key.get(f"n{lot_name}")
        if lot_obj:
            for key in ("nASC", "nSun", "nMoon", "nVenus", "nMars", "nJupiter", "nSaturn"):
                if key in by_key:
                    rels.append(_relationship(REL_LOT_DERIVED_FROM, lot_obj, by_key[key], qualifier=key))

    for row in natal.get("declination_aspects", []) or []:
        src = by_key.get(row.get("a"))
        tgt = by_key.get(row.get("b"))
        if src and tgt:
            rel_type = REL_DECLINATION_CONTRAPARALLEL if row.get("type") in {"contra-parallel", "contra_parallel"} else REL_DECLINATION_PARALLEL
            rels.append(_relationship(rel_type, src, tgt, qualifier=row.get("type"), **row))

    # Compatibility relationships retaining the old longitude-only antiscia/harmonic projection view.
    for body in objects:
        if body.get("object_type") not in TRANSIT_TARGET_TYPES:
            continue
        anti = body.get("facts", {}).get("antiscia") or {}
        for rel_type, lon_key, pretty_key in ((REL_ANTISCIA, "antiscia_lon", "antiscia_pretty"), (REL_CONTRA_ANTISCIA, "contra_antiscia_lon", "contra_antiscia_pretty")):
            lon = _as_lon(anti.get(lon_key))
            if lon is not None:
                rels.append({
                    "id": f"{rel_type}:{body['id']}",
                    "relationship_type": rel_type,
                    "source_id": body["id"],
                    "source_name": body["name"],
                    "target_longitude": lon,
                    "target_pretty": anti.get(pretty_key) or format_zodiac(lon),
                    **semantic_payload(body["name"], rel_type),
                })
        for number, h in (body.get("facts", {}).get("harmonics") or {}).items():
            lon = _as_lon(h.get("lon"))
            if lon is not None:
                rels.append({
                    "id": f"{REL_HARMONIC_PROJECTION}:{number}:{body['id']}",
                    "relationship_type": REL_HARMONIC_PROJECTION,
                    "source_id": body["id"],
                    "source_name": body["name"],
                    "harmonic": int(number),
                    "target_longitude": lon,
                    "target_pretty": h.get("pretty") or format_zodiac(lon),
                    **semantic_payload(body["name"], f"harmonic_{number}"),
                })

    normalized = normalize_relationship_list(rels)
    logger.debug("Built %d raw relationships; %d after normalization", len(rels), len(normalized))
    return normalized


def _stable_relationship_id(rel: dict[str, Any]) -> str:
    payload = "|".join([
        str(rel.get("relationship_type") or ""),
        str(rel.get("source_id") or ""),
        str(rel.get("target_id") or ""),
        f"{float(rel.get('target_longitude')):.8f}" if rel.get("target_longitude") is not None else "",
        str(rel.get("aspect") or ""),
        str(rel.get("harmonic") or ""),
        str(rel.get("type") or ""),
    ])
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]
    return f"rel:{str(rel.get('relationship_type') or 'UNKNOWN').lower()}:{digest}"


def normalize_relationship_list(rels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen = set()
    for original in rels:
        rel = dict(original)
        old = rel.get("relationship_type")
        new = canonical_relationship_type(old)
        if old != new and rel.get("legacy_relationship_type") is None:
            rel["legacy_relationship_type"] = old
        rel["relationship_type"] = new
        key = (
            new,
            str(rel.get("source_id") or ""),
            str(rel.get("target_id") or ""),
            round(float(rel.get("target_longitude")), 8) if rel.get("target_longitude") is not None else None,
            str(rel.get("aspect") or ""),
            str(rel.get("harmonic") or ""),
            str(rel.get("type") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        rel["id"] = _stable_relationship_id(rel)
        normalized.append(rel)
    normalized.sort(key=lambda rel: (
        str(rel.get("relationship_type") or ""),
        str(rel.get("source_id") or ""),
        str(rel.get("target_id") or ""),
        float(rel.get("target_longitude") or -1),
        str(rel.get("aspect") or ""),
        str(rel.get("harmonic") or ""),
        str(rel.get("id") or ""),
    ))
    return normalized


def normalize_relationship_types(graph: dict[str, Any]) -> dict[str, Any]:
    graph["relationships"] = normalize_relationship_list(graph.get("relationships", []) or [])
    graph.setdefault("summary", {})["relationship_types"] = sorted({r["relationship_type"] for r in graph.get("relationships", [])})
    return graph


def build_chart_graph(natal: dict[str, Any]) -> dict[str, Any]:
    logger.info("Building semantic chart graph for person=%s", natal.get("person"))
    objects = sorted(build_chart_objects(natal), key=lambda obj: (str(obj.get("id")), str(obj.get("source_key"))))
    relationships = build_chart_relationships(objects, natal)
    object_relationships: dict[str, list[int]] = {obj["id"]: [] for obj in objects}
    for i, rel in enumerate(relationships):
        if rel.get("source_id") in object_relationships:
            object_relationships[rel["source_id"]].append(i)
        if rel.get("target_id") in object_relationships:
            object_relationships[rel["target_id"]].append(i)
    graph = {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "graph_type": "natal_chart_semantic_graph",
        "relationship_type_ontology": sorted(RELATIONSHIP_TYPES),
        "objects": objects,
        "relationships": relationships,
        "indexes": {
            "objects_by_id": {obj["id"]: i for i, obj in enumerate(objects)},
            "objects_by_source_key": {obj["source_key"]: obj["id"] for obj in objects},
            "relationships_by_type": {rel_type: [i for i, rel in enumerate(relationships) if rel["relationship_type"] == rel_type] for rel_type in sorted({rel["relationship_type"] for rel in relationships})},
            "relationships_by_object_id": object_relationships,
        },
        "summary": {
            "object_count": len(objects),
            "relationship_count": len(relationships),
            "transit_target_count": sum(1 for obj in objects if obj.get("transit_target")),
            "object_types": sorted(set(obj["object_type"] for obj in objects)),
            "relationship_types": sorted(set(rel["relationship_type"] for rel in relationships)),
        },
    }
    logger.info("Semantic chart graph complete: objects=%d relationships=%d transit_targets=%d", graph["summary"]["object_count"], graph["summary"]["relationship_count"], graph["summary"]["transit_target_count"])
    return graph


def transit_targets_from_graph(natal: dict[str, Any]) -> list[dict[str, Any]]:
    logger.debug("Extracting transit targets from graph")
    graph = natal.get("semantic_graph") or build_chart_graph(natal)
    graph = normalize_relationship_types(graph)
    targets = [obj for obj in graph.get("objects", []) if obj.get("transit_target") and obj.get("longitude") is not None]
    logger.info("Transit targets extracted: %d", len(targets))
    return targets


def relationship_summaries_for_object(graph: dict[str, Any], object_id: str, limit: int = 12) -> list[dict[str, Any]]:
    graph = normalize_relationship_types(graph)
    rel_indexes = graph.get("indexes", {}).get("relationships_by_object_id", {}).get(object_id)
    if rel_indexes is None:
        rel_indexes = [i for i, rel in enumerate(graph.get("relationships", [])) if rel.get("source_id") == object_id or rel.get("target_id") == object_id]
    candidate_rels = [graph["relationships"][i] for i in rel_indexes]
    candidate_rels.sort(key=lambda rel: (
        float(rel.get("orb") or 999),
        str(rel.get("relationship_type") or ""),
        str(rel.get("source_id") or ""),
        str(rel.get("target_id") or ""),
        str(rel.get("id") or ""),
    ))
    summaries = []
    for rel in candidate_rels[:limit]:
        summaries.append({
            "relationship_id": rel.get("id"),
            "relationship_type": rel.get("relationship_type"),
            "source_id": rel.get("source_id"),
            "target_id": rel.get("target_id"),
            "aspect": rel.get("aspect"),
            "orb": rel.get("orb"),
            "theme_tags": rel.get("theme_tags", []),
            "semantic_operator_hints": rel.get("semantic_operator_hints", []),
        })
    return summaries


def transit_candidate_from_target(
    transit_body: str,
    transit_pos: dict[str, Any],
    target: dict[str, Any],
    cusps: list[float],
    aspect: dict[str, Any],
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target_name = target["source_key"] if str(target["source_key"]).startswith("n") else f"n{target['name']}"
    score = relevance_score(transit_body, target_name, aspect)
    candidate = {
        "orb": aspect["orb"],
        "relevance_score": score,
        "transit_body": transit_body,
        "natal_target": target_name,
        "natal_target_id": target["id"],
        "natal_target_name": target["name"],
        "natal_target_type": target["object_type"],
        "aspect": aspect["aspect"],
        "distance": aspect["distance"],
        "exact_angle": aspect["exact_angle"],
        "major": aspect["major"],
        "strength": aspect["strength"],
        "transit_house_in_natal_chart": house_for_lon(transit_pos["lon"], cusps),
        "natal_target_house": target.get("house"),
        "natal_target_pretty": target.get("pretty"),
        "relationship_type": REL_TRANSIT_ACTIVATION,
        **semantic_payload(transit_body, target["name"], target.get("house"), aspect=aspect["aspect"]),
    }
    if graph is not None:
        candidate["activated_natal_relationships"] = relationship_summaries_for_object(graph, target["id"])
    return candidate
