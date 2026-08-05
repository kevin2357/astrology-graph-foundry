from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from astrology_graph_foundry.common.aspects import all_aspects
from astrology_graph_foundry.common.chart_graph import build_chart_graph
from astrology_graph_foundry.common.transitable_chart import descriptor_for_package
from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary
from astrology_graph_foundry.common.geometry import deg_to_sign, format_zodiac, house_for_lon, midpoint
from astrology_graph_foundry.common.io import read_json
from astrology_graph_foundry.common.identity import (
    RELATIONSHIP_CHART_IDENTITY_VERSION,
    derive_relationship_source_chart_id,
    source_chart_id_from_natal_package,
)
from astrology_graph_foundry.common.themes import operator_hints, theme_tags
from astrology_graph_foundry.ephemeris.models import BirthData, ProviderConfig
from astrology_graph_foundry.ephemeris.providers import create_provider
from astrology_graph_foundry.pipelines.natal import build as build_natal

SCHEMA_VERSION = "1.1.0"
PIPELINE_VERSION = "composite_pipeline_v1.0.0"
logger = logging.getLogger(__name__)

CORE_BODY_ORDER = [
    "nSun", "nMoon", "nMercury", "nVenus", "nMars", "nJupiter", "nSaturn",
    "nUranus", "nNeptune", "nPluto", "nNorth Node", "nSouth Node", "nASC", "nDSC", "nMC", "nIC",
]


def _load_dataset(path_or_data: str | dict[str, Any]) -> dict[str, Any]:
    return read_json(path_or_data) if isinstance(path_or_data, str) else path_or_data


def _natal_from_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    natal = dataset.get("natal", dataset)
    graph = dataset.get("canonical_astrology_graph") or natal.get("semantic_graph")
    if graph is None:
        graph = build_chart_graph(natal)
    natal["semantic_graph"] = graph
    return natal


def _person_name(dataset: dict[str, Any], fallback: str) -> str:
    return (
        dataset.get("metadata", {}).get("person")
        or dataset.get("person", {}).get("person")
        or dataset.get("person", fallback)
        or fallback
    )


def _dataset_from_live(prefix: str, kwargs: dict[str, Any]) -> dict[str, Any] | None:
    provider = kwargs.get(f"{prefix}_provider")
    natal_dataset = kwargs.get(f"{prefix}_natal_dataset")
    person_jsonl = kwargs.get(f"{prefix}_jsonl")
    if natal_dataset:
        return _load_dataset(natal_dataset)
    if provider == "cached" and person_jsonl:
        ep = create_provider(
            "cached",
            person_jsonl=person_jsonl,
            config=ProviderConfig(
                start=kwargs.get("start"),
                end=kwargs.get("end"),
                snapshot_timezone=kwargs.get("snapshot_timezone", "America/Denver"),
                snapshot_time=kwargs.get("snapshot_time", "12:00"),
                ephe_path=kwargs.get("ephe_path", "."),
                house_system=kwargs.get("house_system", "P"),
            ),
        )
        return {"metadata": ep.person_metadata(), "person": ep.person_metadata(), "natal": ep.natal_chart()}
    if provider == "live":
        name = kwargs.get(f"{prefix}_name")
        birth_local = kwargs.get(f"{prefix}_birth_local")
        birth_timezone = kwargs.get(f"{prefix}_birth_timezone")
        birth_lat = kwargs.get(f"{prefix}_birth_lat")
        birth_lon = kwargs.get(f"{prefix}_birth_lon")
        if not all(v is not None and v != "" for v in [name, birth_local, birth_timezone, birth_lat, birth_lon]):
            raise ValueError(f"{prefix}_provider='live' requires {prefix}_name, birth_local, birth_timezone, birth_lat, and birth_lon")
        return build_natal(
            provider="live",
            name=name,
            birth_local=birth_local,
            birth_timezone=birth_timezone,
            birth_lat=float(birth_lat),
            birth_lon=float(birth_lon),
            birth_location_label=kwargs.get(f"{prefix}_birth_location_label", ""),
            source_chart_id=kwargs.get(f"{prefix}_source_chart_id"),
            snapshot_timezone=kwargs.get("snapshot_timezone", "America/Denver"),
            snapshot_time=kwargs.get("snapshot_time", "12:00"),
            ephe_path=kwargs.get("ephe_path", "."),
            house_system=kwargs.get("house_system", "P"),
        )
    return None


def resolve_pair_inputs(**kwargs: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    a = kwargs.get("person_a_dataset") or kwargs.get("person_a_natal_dataset")
    b = kwargs.get("person_b_dataset") or kwargs.get("person_b_natal_dataset")
    data_a = _load_dataset(a) if a else _dataset_from_live("person_a", kwargs)
    data_b = _load_dataset(b) if b else _dataset_from_live("person_b", kwargs)
    if data_a is None or data_b is None:
        raise ValueError("Composite/synastry pipelines require two natal datasets or two provider-backed natal inputs.")
    return data_a, data_b


def _body_map(natal: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {k: v for k, v in (natal.get("bodies") or {}).items() if isinstance(v, dict) and v.get("lon") is not None}


def _house_cusps(natal: dict[str, Any]) -> list[float]:
    houses = natal.get("houses") or {}
    return [float(houses[str(i)]["lon"]) for i in range(1, 13) if str(i) in houses]


def _birth_utc(natal: dict[str, Any]) -> datetime:
    if natal.get("birth_utc"):
        return datetime.fromisoformat(str(natal["birth_utc"]).replace("Z", "+00:00")).astimezone(timezone.utc)
    local = datetime.fromisoformat(str(natal["birth_local"])).replace(tzinfo=ZoneInfo(str(natal["birth_timezone"])))
    return local.astimezone(timezone.utc)


def _composite_reference_event(natal_a: dict[str, Any], natal_b: dict[str, Any]) -> dict[str, Any]:
    """Synthetic midpoint anchor used only to locate annual returns to composite positions.

    Minimal in-memory charts used by tests/consumers may omit birth provenance;
    in that case the composite remains transitable but does not advertise
    solar-return capability until a reference event is supplied.
    """
    required = ("birth_local", "birth_timezone", "birth_lat", "birth_lon")
    if not all(natal_a.get(key) is not None and natal_b.get(key) is not None for key in required):
        return {
            "midpoint_utc": None,
            "midpoint_lat": None,
            "midpoint_lon": None,
            "timezone": "UTC",
            "location_label": "Composite synthetic midpoint reference unavailable",
            "method": "unavailable: source birth provenance missing",
        }
    a_utc, b_utc = _birth_utc(natal_a), _birth_utc(natal_b)
    midpoint_utc = datetime.fromtimestamp((a_utc.timestamp() + b_utc.timestamp()) / 2.0, tz=timezone.utc)
    lat = (float(natal_a["birth_lat"]) + float(natal_b["birth_lat"])) / 2.0
    lon = (float(natal_a["birth_lon"]) + float(natal_b["birth_lon"])) / 2.0
    return {
        "midpoint_utc": midpoint_utc.isoformat(),
        "midpoint_lat": lat,
        "midpoint_lon": lon,
        "timezone": "UTC",
        "location_label": "Composite synthetic midpoint reference",
        "method": "midpoint of source birth timestamps and coordinates; used as an annual-return search anchor, not as the composite construction itself",
    }


def _composite_bodies(natal_a: dict[str, Any], natal_b: dict[str, Any]) -> dict[str, dict[str, Any]]:
    bodies_a = _body_map(natal_a)
    bodies_b = _body_map(natal_b)
    out: dict[str, dict[str, Any]] = {}
    common = [key for key in CORE_BODY_ORDER if key in bodies_a and key in bodies_b]
    common.extend(sorted((set(bodies_a) & set(bodies_b)) - set(common)))
    for key in common:
        lon = midpoint(float(bodies_a[key]["lon"]), float(bodies_b[key]["lon"]))
        info = deg_to_sign(lon)
        out[key] = {
            "lon": lon,
            "pretty": format_zodiac(lon),
            "sign": info["sign"],
            "sign_degree": info["sign_degree"],
            "type": bodies_a[key].get("type") or bodies_b[key].get("type") or "planet_or_point",
            "source": "midpoint_composite",
            "source_a_lon": bodies_a[key].get("lon"),
            "source_b_lon": bodies_b[key].get("lon"),
        }
    return out


def _composite_houses(natal_a: dict[str, Any], natal_b: dict[str, Any]) -> dict[str, dict[str, Any]]:
    houses_a = natal_a.get("houses") or {}
    houses_b = natal_b.get("houses") or {}
    out: dict[str, dict[str, Any]] = {}
    for i in range(1, 13):
        if str(i) not in houses_a or str(i) not in houses_b:
            continue
        lon = midpoint(float(houses_a[str(i)]["lon"]), float(houses_b[str(i)]["lon"]))
        info = deg_to_sign(lon)
        out[str(i)] = {"lon": lon, "pretty": format_zodiac(lon), "sign": info["sign"], "sign_degree": info["sign_degree"]}
    return out


def _element_modality_balance(bodies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modalities = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    sign_to_element = {
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
    }
    sign_to_modality = {
        "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
        "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
        "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable",
    }
    for body in bodies.values():
        sign = body.get("sign") or deg_to_sign(body["lon"])["sign"]
        elements[sign_to_element.get(sign, "Air")] += 1
        modalities[sign_to_modality.get(sign, "Mutable")] += 1
    return {"elements": elements, "modalities": modalities}


def _theme_metrics(aspects: list[dict[str, Any]], bodies: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    scores: dict[str, float] = defaultdict(float)
    for row in aspects:
        for tag in row.get("theme_tags", []):
            scores[tag] += float(row.get("weight") or 0)
    for key, body in bodies.items():
        for tag in theme_tags(key, body.get("sign"), body.get("house")):
            scores[tag] += 3.0
    return [{"theme": k, "score": round(v, 3)} for k, v in sorted(scores.items(), key=lambda kv: -kv[1])]


def build_from_datasets(person_a_dataset: dict[str, Any], person_b_dataset: dict[str, Any]) -> dict[str, Any]:
    name_a = _person_name(person_a_dataset, "Person A")
    name_b = _person_name(person_b_dataset, "Person B")
    logger.info("Building composite dataset for %s + %s", name_a, name_b)
    natal_a = _natal_from_dataset(person_a_dataset)
    natal_b = _natal_from_dataset(person_b_dataset)
    participant_source_chart_ids = [
        source_chart_id_from_natal_package(person_a_dataset, fallback_name=name_a),
        source_chart_id_from_natal_package(person_b_dataset, fallback_name=name_b),
    ]
    source_chart_id = derive_relationship_source_chart_id("composite", participant_source_chart_ids)
    bodies = _composite_bodies(natal_a, natal_b)
    houses = _composite_houses(natal_a, natal_b)
    cusps = [houses[str(i)]["lon"] for i in range(1, 13) if str(i) in houses]
    if len(cusps) == 12:
        for body in bodies.values():
            body["house"] = house_for_lon(body["lon"], cusps)
    aspects = all_aspects(bodies, bodies, "composite", "composite", include_minor=True)
    for row in aspects:
        row["relationship_type"] = "COMPOSITE_ASPECT"
        row["theme_tags"] = theme_tags(row.get("source_body"), row.get("target_body"), aspect=row.get("aspect"))
        row["semantic_operator_hints"] = operator_hints(row.get("source_body"), row.get("target_body"), aspect=row.get("aspect"))
    composite_natal = {
        "person": f"Composite: {name_a} + {name_b}",
        "bodies": bodies,
        "houses": houses,
        "natal_planet_aspects": aspects,
        "natal_planet_angle_aspects": [],
        "natal_planet_point_aspects": [],
        "declination_aspects": [],
        "lots": {},
        "fixed_stars": [],
    }
    graph = build_chart_graph(composite_natal)
    metrics = _theme_metrics(aspects, bodies)
    evidence = [
        {
            "id": f"composite_claim_{i:04d}",
            "theme": m["theme"],
            "claim": f"The composite chart has a strong {m['theme'].replace('_', ' ')} signature.",
            "confidence": min(0.98, 0.45 + float(m["score"]) / 100),
            "supporting_aspect_refs": [a["id"] for a in aspects if m["theme"] in a.get("theme_tags", [])][:10],
        }
        for i, m in enumerate(metrics[:20], 1)
    ]
    package = {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "analysis_type": "composite_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "person_a": name_a,
            "person_b": name_b,
            "source_chart_id": source_chart_id,
            "participant_source_chart_ids": participant_source_chart_ids,
            "relationship_chart_identity_version": RELATIONSHIP_CHART_IDENTITY_VERSION,
            "composite_method": "midpoint_longitude",
        },
        "person_a": {"metadata": person_a_dataset.get("metadata", {}), "natal_summary": natal_a.get("semantic_graph", {}).get("summary", {})},
        "person_b": {"metadata": person_b_dataset.get("metadata", {}), "natal_summary": natal_b.get("semantic_graph", {}).get("summary", {})},
        "composite_reference_event": _composite_reference_event(natal_a, natal_b),
        "composite_chart": composite_natal,
        "semantic_graph": graph,
        "composite_aspects": aspects,
        "balance_metrics": _element_modality_balance(bodies),
        "theme_metrics": metrics,
        "evidence_graph": evidence,
        "report_materials": {
            "recommended_sections": [
                "Composite Relationship Entity Executive Summary",
                "Composite Big Three",
                "Composite Planet-by-Planet",
                "Composite Houses",
                "Composite Aspect Synthesis",
                "Composite Theme Metrics",
                "Evidence Graph Appendix",
            ],
            "top_composite_aspects": aspects[:30],
            "top_evidence_claims": evidence[:12],
        },
    }
    package["transitable_chart"] = descriptor_for_package(package)
    logger.info("Composite dataset complete: bodies=%d aspects=%d graph_objects=%d graph_relationships=%d", len(bodies), len(aspects), len(graph.get("objects", [])), len(graph.get("relationships", [])))
    return finalize_package_semantic_boundary(package)


def build(**kwargs: Any) -> dict[str, Any]:
    data_a, data_b = resolve_pair_inputs(**kwargs)
    return build_from_datasets(data_a, data_b)
