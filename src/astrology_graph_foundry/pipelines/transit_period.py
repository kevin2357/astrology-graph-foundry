from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from astrology_graph_foundry.common.graph_compiler import GraphCompiler
from astrology_graph_foundry.common.themes import operator_hints, theme_tags
from astrology_graph_foundry.common.semantic_layers import (
    canonical_graph_from_package,
    finalize_package_semantic_boundary,
    finalize_view_semantic_boundary,
    orthodox_claims_from_package,
    orthodox_metrics_from_package,
    orthodox_report_materials_from_package,
    orthodox_row_annotation,
)
from astrology_graph_foundry.ephemeris.models import ProviderConfig
from astrology_graph_foundry.ephemeris.providers import EphemerisProvider, create_provider

SCHEMA_VERSION = "2.0.0"
PIPELINE_VERSION = "transit_period_pipeline_v2.0.0_transitable_chart"

logger = logging.getLogger(__name__)


STREAMING_PROFILES = ("standard", "compact", "game")
TRANSIT_TARGET_SETS = ("core", "expanded", "all", "gameplay")
_GAMEPLAY_TARGET_NAMES = {
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "True Node", "ASC", "DSC", "MC", "IC",
}
_GAMEPLAY_TRANSITING_BODIES = {
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "True Node",
}
_ZODIAC_SIGNS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)


def _normalize_target_name(candidate: dict[str, Any]) -> str:
    raw = str(candidate.get("target_name") or candidate.get("target") or "").strip()
    return raw[1:] if raw.startswith("n") else raw


def _target_set_accepts(candidate: dict[str, Any], target_set: str) -> bool:
    if target_set == "all":
        return True
    name = _normalize_target_name(candidate)
    target_type = str(candidate.get("target_type") or "")
    if target_set == "gameplay":
        return name in _GAMEPLAY_TARGET_NAMES
    if target_set == "core":
        return name in _GAMEPLAY_TARGET_NAMES
    if target_set == "expanded":
        return target_type not in {"harmonic_point"}
    raise ValueError(f"Unknown transit target set: {target_set!r}")



def _materializable_days(package: dict[str, Any], daily_sky_source: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return full-like daily rows from full or standard streaming Transit artifacts."""
    sky_by_date = {
        str(day.get("date")): day
        for day in ((daily_sky_source or {}).get("daily_windows", []) or [])
    }
    if package.get("daily_windows"):
        return [dict(day) for day in package.get("daily_windows", []) or []]

    if package.get("days"):
        registry = package.get("candidate_registry") or {}
        rows: list[dict[str, Any]] = []
        for day in package.get("days", []) or []:
            candidates: list[dict[str, Any]] = []
            for mutable in day.get("candidate_refs", []) or []:
                candidate_id = str(mutable.get("candidate_id") or "")
                static = dict(registry.get(candidate_id) or {})
                candidates.append({**static, **mutable})
            daily_sky = day.get("daily_sky") or {}
            sky_day = sky_by_date.get(str(day.get("date"))) or {}
            rows.append(
                {
                    "date": day.get("date"),
                    "transit_datetime": day.get("transit_datetime"),
                    "candidates": candidates,
                    "positions": (
                        day.get("positions")
                        or daily_sky.get("positions")
                        or sky_day.get("positions")
                        or {}
                    ),
                    "daily_sky": daily_sky,
                }
            )
        return rows

    if package.get("days_by_date"):
        registry = package.get("candidate_registry") or {}
        rows = []
        for date, day in sorted((package.get("days_by_date") or {}).items()):
            candidates = []
            for mutable in day.get("contacts", []) or []:
                candidate_id = str(mutable.get("candidate_id") or "")
                static = dict(registry.get(candidate_id) or {})
                candidates.append({**static, **mutable})
            daily_sky = day.get("daily_sky") or {}
            rows.append(
                {
                    "date": date,
                    "transit_datetime": day.get("transit_datetime"),
                    "candidates": candidates,
                    "positions": daily_sky.get("positions") or {},
                    "daily_sky": daily_sky,
                }
            )
        return rows

    return []


def transit_candidate_matches_target_set(candidate: dict[str, Any], target_set: str) -> bool:
    """Public, auditable target-set policy used by materializers and exporters."""
    return _target_set_accepts(candidate, target_set)


def _target_cusps(package: dict[str, Any]) -> list[float]:
    chart = ((package.get("target") or {}).get("chart") or {})
    houses = chart.get("houses") or {}
    try:
        return [float(houses[str(i)]["lon"]) for i in range(1, 13)]
    except (KeyError, TypeError, ValueError):
        return []


def _sign_for_lon(lon: float | None) -> str | None:
    if lon is None:
        return None
    return _ZODIAC_SIGNS[int(float(lon) % 360 // 30)]


def _daily_sky_record(day: dict[str, Any], package: dict[str, Any]) -> dict[str, Any]:
    from astrology_graph_foundry.common.geometry import house_for_lon

    cusps = _target_cusps(package)
    positions: dict[str, dict[str, Any]] = {}
    for body, row in sorted((day.get("positions") or {}).items()):
        clean = str(body)[1:] if str(body).startswith("n") else str(body)
        if clean not in _GAMEPLAY_TRANSITING_BODIES:
            continue
        lon = row.get("lon")
        positions[clean] = {
            "longitude": lon,
            "sign": _sign_for_lon(lon),
            "house": house_for_lon(float(lon), cusps) if lon is not None and len(cusps) == 12 else None,
            "retrograde": bool(row.get("retrograde", False)),
            "speed_longitude": row.get("speed_lon"),
        }
    return {
        "transit_datetime": day.get("transit_datetime"),
        "positions": positions,
    }


def _compact_candidate_registry_entry(candidate: dict[str, Any], *, game: bool = False) -> dict[str, Any]:
    row = {
        "candidate_id": _candidate_id(candidate),
        "transit_body": candidate.get("transit_body"),
        "aspect": candidate.get("aspect"),
        "target_id": candidate.get("target_id"),
        "target_name": _normalize_target_name(candidate),
        "target_type": candidate.get("target_type"),
        "target_house": candidate.get("target_house"),
        "transit_house_in_target_chart": candidate.get("transit_house_in_target_chart"),
        "relationship_type": candidate.get("relationship_type", "TRANSIT_ACTIVATION"),
        "theme_tags": candidate.get("theme_tags", []),
        "semantic_operator_hints": candidate.get("semantic_operator_hints", []),
    }
    if not game:
        row["activated_target_relationship_refs"] = candidate.get("activated_target_relationship_refs", [])
    return row


def _compact_activation_ref(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": _candidate_id(candidate),
        "rank": candidate.get("rank"),
        "orb": candidate.get("orb"),
        "relevance_score": candidate.get("relevance_score"),
        "phase": candidate.get("phase"),
        "strength_label": candidate.get("strength"),
    }


def _profiled_candidates(day: dict[str, Any], target_set: str) -> list[dict[str, Any]]:
    return [c for c in (day.get("candidates") or []) if _target_set_accepts(c, target_set)]


def _compact_relationship_registry(
    package: dict[str, Any],
    candidate_rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    wanted = {
        str(ref)
        for candidate in candidate_rows
        for ref in (candidate.get("activated_target_relationship_refs") or [])
    }
    source = package.get("activated_target_relationship_registry") or {}
    out: dict[str, dict[str, Any]] = {}
    for ref in sorted(wanted):
        row = source.get(ref)
        if not row:
            continue
        out[ref] = {
            "relationship_id": row.get("relationship_id") or ref,
            "relationship_type": row.get("relationship_type"),
            "source_object_id": row.get("source_object_id"),
            "target_object_id": row.get("target_object_id"),
            "structural_strength_score": row.get("structural_strength_score"),
        }
    return out



def _enrich(candidate: dict[str, Any]) -> dict[str, Any]:
    out = dict(candidate)
    out["theme_tags"] = theme_tags(
        out.get("transit_body"),
        out.get("target"),
        out.get("target_house"),
        out.get("transit_house_in_target_chart"),
        out.get("target_type"),
        aspect=out.get("aspect"),
    )
    out["semantic_operator_hints"] = operator_hints(
        out.get("transit_body"),
        out.get("target"),
        out.get("target_type"),
        aspect=out.get("aspect"),
    )
    return out


def _candidate_is_compiled(candidate: dict[str, Any]) -> bool:
    has_refs = "activated_target_relationship_refs" in candidate or "activated_target_relationships" in candidate
    return bool(candidate.get("target_id") and candidate.get("target_type") and has_refs)


def _relationship_registry(compiler: GraphCompiler) -> dict[str, dict[str, Any]]:
    """One copy of activated target relationship summaries, keyed by id.

    Previous long-range transit builds embedded the same activated relationship
    summaries inside every candidate on every day and then duplicated them again
    in arcs/evidence/report materials. This registry preserves the semantic
    reasoning context without reserializing identical relationship summaries
    thousands of times.
    """
    registry: dict[str, dict[str, Any]] = {}
    for target in compiler.targets:
        for rel in target.activated_relationships:
            rel_id = rel.get("relationship_id")
            if rel_id:
                registry[str(rel_id)] = dict(rel)
    return dict(sorted(registry.items()))


def _compact_relationship_refs(candidate: dict[str, Any]) -> dict[str, Any]:
    out = dict(candidate)
    if "activated_target_relationship_refs" not in out:
        refs = [
            str(rel["relationship_id"])
            for rel in out.get("activated_target_relationships", []) or []
            if rel.get("relationship_id")
        ]
        out["activated_target_relationship_refs"] = refs
    out.pop("activated_target_relationships", None)
    return out


def _daily_candidates(day: Any, compiler: GraphCompiler, top_n_per_day: int) -> list[dict[str, Any]]:
    existing = list(getattr(day, "reverse_read_candidates", []) or [])
    if existing and all(_candidate_is_compiled(candidate) for candidate in existing[: min(len(existing), top_n_per_day)]):
        return [_compact_relationship_refs(_enrich(candidate)) for candidate in existing[:top_n_per_day]]
    positions = getattr(day, "positions", {}) or {}
    if positions:
        _, ranked = compiler.transit_to_target_candidates(positions, top_n=top_n_per_day)
        return [_compact_relationship_refs(_enrich(candidate)) for candidate in ranked]
    return [_compact_relationship_refs(_enrich(candidate)) for candidate in existing[:top_n_per_day]]


def _candidate_id(candidate: dict[str, Any]) -> str:
    transit_body = str(candidate.get("transit_body", "unknown")).replace(" ", "_")
    aspect = str(candidate.get("aspect", "unknown")).replace(" ", "_")
    target_id = str(candidate.get("target_id") or candidate.get("target") or "unknown").replace(" ", "_").replace(":", "_")
    return f"tc:{transit_body}:{aspect}:{target_id}"


def _candidate_ref(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": _candidate_id(candidate),
        "rank": candidate.get("rank"),
        "transit_body": candidate.get("transit_body"),
        "aspect": candidate.get("aspect"),
        "target": candidate.get("target"),
        "target_id": candidate.get("target_id"),
        "target_type": candidate.get("target_type"),
        "orb": candidate.get("orb"),
        "relevance_score": candidate.get("relevance_score"),
        "theme_tags": candidate.get("theme_tags", []),
        "semantic_operator_hints": candidate.get("semantic_operator_hints", []),
        "activated_target_relationship_refs": candidate.get("activated_target_relationship_refs", []),
    }


def _candidate_registry_entry(candidate: dict[str, Any]) -> dict[str, Any]:
    # Static semantic material shared by every daily activation of this transit/target/aspect.
    return {
        "candidate_id": _candidate_id(candidate),
        "transit_body": candidate.get("transit_body"),
        "aspect": candidate.get("aspect"),
        "target": candidate.get("target"),
        "target_id": candidate.get("target_id"),
        "target_name": candidate.get("target_name"),
        "target_type": candidate.get("target_type"),
        "target_house": candidate.get("target_house"),
        "target_pretty": candidate.get("target_pretty"),
        "transit_house_in_target_chart": candidate.get("transit_house_in_target_chart"),
        "relationship_type": candidate.get("relationship_type", "TRANSIT_ACTIVATION"),
        "exact_angle": candidate.get("exact_angle"),
        "major": candidate.get("major"),
        "theme_tags": candidate.get("theme_tags", []),
        "semantic_operator_hints": candidate.get("semantic_operator_hints", []),
        "activated_target_relationship_refs": candidate.get("activated_target_relationship_refs", []),
    }


def _candidate_activation_ref(candidate: dict[str, Any]) -> dict[str, Any]:
    # Per-day mutable values only; consumers resolve candidate_id through candidate_registry.
    return {
        "candidate_id": _candidate_id(candidate),
        "rank": candidate.get("rank"),
        "orb": candidate.get("orb"),
        "distance": candidate.get("distance"),
        "relevance_score": candidate.get("relevance_score"),
        "strength": candidate.get("strength"),
    }


def _candidate_registry(package: dict[str, Any]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for day in package.get("daily_windows", []) or []:
        for candidate in day.get("candidates", []) or []:
            cid = _candidate_id(candidate)
            if cid not in registry:
                registry[cid] = _candidate_registry_entry(candidate)
    return dict(sorted(registry.items()))


def _day_ref(day: dict[str, Any], *, candidate_limit: int = 5, registry_refs_only: bool = False) -> dict[str, Any]:
    candidates = day.get("candidates", [])[:candidate_limit]
    candidate_rows = [_candidate_activation_ref(c) if registry_refs_only else _candidate_ref(c) for c in candidates]
    top = None
    if day.get("candidates"):
        top = _candidate_activation_ref(day["candidates"][0]) if registry_refs_only else _candidate_ref(day["candidates"][0])
    return {
        "date": day["date"],
        "transit_datetime": day.get("transit_datetime"),
        "candidate_count": len(day.get("candidates", [])),
        "top_candidate": top,
        "candidate_refs": candidate_rows,
    }


def _arc_ref(arc: dict[str, Any], *, registry_refs_only: bool = False) -> dict[str, Any]:
    out = {
        "arc_id": arc.get("arc_id"),
        "candidate_id": arc.get("candidate_id"),
        "transit_body": arc.get("transit_body"),
        "aspect": arc.get("aspect"),
        "target": arc.get("target"),
        "target_id": arc.get("target_id"),
        "target_type": arc.get("target_type"),
        "start_date": arc.get("start_date"),
        "end_date": arc.get("end_date"),
        "active_days": arc.get("active_days"),
        "closest_orb": arc.get("closest_orb"),
        "average_rank": arc.get("average_rank"),
        "max_relevance_score": arc.get("max_relevance_score"),
        "observation_dates": arc.get("observation_dates", []),
    }
    if not registry_refs_only:
        out.update({
            "theme_tags": arc.get("theme_tags", []),
            "dominant_operators": arc.get("dominant_operators", []),
            "activated_target_relationship_refs": arc.get("activated_target_relationship_refs", []),
        })
    return out


def _summarize(rows: list[dict[str, Any]], arc_id: str) -> dict[str, Any]:
    dates = [r["date"] for r in rows]
    orbs = [float(r["orb"]) for r in rows if r.get("orb") is not None]
    ranks = [float(r["rank"]) for r in rows if r.get("rank") is not None]
    scores = [float(r["relevance_score"]) for r in rows if r.get("relevance_score") is not None]
    sample = rows[0]
    theme_counter: dict[str, int] = defaultdict(int)
    operator_counter: dict[str, int] = defaultdict(int)
    target_type_counter: dict[str, int] = defaultdict(int)
    activated_relationship_type_counter: dict[str, int] = defaultdict(int)
    activated_refs: set[str] = set()
    closest = min(rows, key=lambda row: float(row.get("orb") or 999))
    strongest = max(rows, key=lambda row: float(row.get("relevance_score") or 0))
    for row in rows:
        target_type_counter[row.get("target_type", "unknown")] += 1
        activated_refs.update(str(ref) for ref in row.get("activated_target_relationship_refs", []) or [])
        for tag in row.get("theme_tags", []):
            theme_counter[tag] += 1
        for hint in row.get("semantic_operator_hints", []):
            operator_counter[hint["operator"]] += 1
        # Expanded relationship summaries are accepted before registry compaction.
        for activated in row.get("activated_target_relationships", []) or []:
            activated_relationship_type_counter[activated.get("relationship_type", "UNKNOWN")] += 1
            if activated.get("relationship_id"):
                activated_refs.add(str(activated["relationship_id"]))
    return {
        "arc_id": arc_id,
        "candidate_id": _candidate_id(sample),
        "transit_body": sample.get("transit_body"),
        "aspect": sample.get("aspect"),
        "target": sample.get("target"),
        "target_id": sample.get("target_id"),
        "target_type": sample.get("target_type"),
        "target_house": sample.get("target_house"),
        "transit_house_in_target_chart": sample.get("transit_house_in_target_chart"),
        "relationship_type": sample.get("relationship_type", "TRANSIT_ACTIVATION"),
        "start_date": min(dates),
        "end_date": max(dates),
        "active_days": len(rows),
        "observation_dates": dates,
        "closest_observation": {"date": closest["date"], **_candidate_ref(closest)},
        "strongest_observation": {"date": strongest["date"], **_candidate_ref(strongest)},
        "closest_orb": min(orbs) if orbs else None,
        "average_orb": sum(orbs) / len(orbs) if orbs else None,
        "average_rank": sum(ranks) / len(ranks) if ranks else None,
        "max_relevance_score": max(scores) if scores else None,
        "average_relevance_score": sum(scores) / len(scores) if scores else None,
        "theme_tags": [k for k, _ in sorted(theme_counter.items(), key=lambda kv: (-kv[1], kv[0]))],
        "dominant_operators": [k for k, _ in sorted(operator_counter.items(), key=lambda kv: (-kv[1], kv[0]))],
        "target_type_counts": dict(sorted(target_type_counter.items())),
        "activated_relationship_type_counts": dict(sorted(activated_relationship_type_counter.items())),
        "activated_target_relationship_refs": sorted(activated_refs),
    }


def _monthly(days: list[dict[str, Any]]) -> list[dict[str, Any]]:
    months: dict[str, dict[str, Any]] = {}
    for day in days:
        month = day["date"][:7]
        bucket = months.setdefault(month, {"month": month, "days": 0, "candidate_count": 0, "theme_scores": defaultdict(float), "target_type_counts": defaultdict(int)})
        bucket["days"] += 1
        bucket["candidate_count"] += len(day["candidates"])
        for candidate in day["candidates"]:
            bucket["target_type_counts"][candidate.get("target_type", "unknown")] += 1
            for tag in candidate.get("theme_tags", []):
                bucket["theme_scores"][tag] += float(candidate.get("relevance_score", 0))
    return [
        {
            "month": month,
            "days": bucket["days"],
            "candidate_count": bucket["candidate_count"],
            "target_type_counts": dict(sorted(bucket["target_type_counts"].items())),
            "top_themes": [{"theme": k, "score": round(v, 3)} for k, v in sorted(bucket["theme_scores"].items(), key=lambda kv: -kv[1])[:10]],
        }
        for month, bucket in sorted(months.items())
    ]



def _orthodox_relationship_registry(
    registry: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {
        key: orthodox_row_annotation(row)
        for key, row in registry.items()
    }

def _analysis_view(package: dict[str, Any]) -> dict[str, Any]:
    logger.debug("Creating compact analysis view for transit package")
    graph = canonical_graph_from_package(package)
    top_arcs = package["transit_arcs"][:100]
    return {
        "view_type": "analysis",
        "metadata": package["metadata"],
        "period": package["period"],
        "canonical_graph_summary": graph.get("summary", {}),
        "relationship_type_ontology": graph.get("relationship_type_ontology", []),
        "activated_target_relationship_registry": _orthodox_relationship_registry(package.get("activated_target_relationship_registry", {})),
        "transit_arcs": [_arc_ref(arc) for arc in top_arcs],
        "monthly_summary": package["monthly_summary"],
        "target_type_metrics": package["target_type_metrics"],
        "activated_relationship_type_metrics": package["activated_relationship_type_metrics"],
        "orthodox_projection_extract": {
            "theme_metrics": orthodox_metrics_from_package(package),
            "claim_candidates": orthodox_claims_from_package(package),
            "report_materials": {
                **orthodox_report_materials_from_package(package),
                "top_transit_arcs": [_arc_ref(arc) for arc in package["transit_arcs"][:20]],
                "top_daily_windows": [_day_ref(day) for day in package["daily_windows"][:10]],
            },
        },
    }


def _streaming_index(
    package: dict[str, Any],
    *,
    profile: str = "standard",
    target_set: str | None = None,
    daily_sky_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if profile not in STREAMING_PROFILES:
        raise ValueError(f"Unknown streaming profile {profile!r}; expected one of {STREAMING_PROFILES}")
    if target_set is None:
        target_set = "gameplay" if profile == "game" else "all"
    if target_set not in TRANSIT_TARGET_SETS:
        raise ValueError(f"Unknown transit target set {target_set!r}; expected one of {TRANSIT_TARGET_SETS}")

    days = _materializable_days(package, daily_sky_source=daily_sky_source)
    logger.info(
        "Creating streaming index: profile=%s target_set=%s days=%d arcs=%d",
        profile,
        target_set,
        len(days),
        len(package.get("transit_arcs", [])),
    )

    if profile == "standard":
        registry = _candidate_registry(package)
        return {
            "view_type": "streaming_index",
            "streaming_profile": "standard",
            "target_set": "all",
            "metadata": {**package["metadata"], "streaming_index_compaction": "candidate_registry_v1"},
            "period": package["period"],
            "canonical_graph_summary": canonical_graph_from_package(package).get("summary", {}),
            "candidate_registry": registry,
            "activated_target_relationship_registry": _orthodox_relationship_registry(package.get("activated_target_relationship_registry", {})),
            "days": [
                {
                    **_day_ref(day, candidate_limit=25, registry_refs_only=True),
                    "daily_sky": _daily_sky_record(day, package),
                }
                for day in days
            ],
            "arcs": [_arc_ref(arc, registry_refs_only=True) for arc in package["transit_arcs"]],
            "arcs_by_target_type": package["target_type_metrics"],
            "arcs_by_activated_relationship_type": package["activated_relationship_type_metrics"],
            "months": package["monthly_summary"],
        }

    selected: list[dict[str, Any]] = []
    days_by_date: dict[str, dict[str, Any]] = {}
    for day in days:
        candidates = _profiled_candidates(day, target_set)
        if profile == "game":
            candidates = [
                candidate
                for candidate in candidates
                if str(candidate.get("transit_body") or "").replace("_", " ") in _GAMEPLAY_TRANSITING_BODIES
            ]
        selected.extend(candidates)
        day_row: dict[str, Any] = {
            "transit_datetime": day.get("transit_datetime"),
            "candidate_count": len(candidates),
            "contacts": [_compact_activation_ref(c) for c in candidates],
        }
        if profile == "game":
            generated_sky = _daily_sky_record(day, package)
            if not generated_sky.get("positions") and day.get("daily_sky"):
                generated_sky = dict(day.get("daily_sky") or {})
            day_row["daily_sky"] = generated_sky
        days_by_date[str(day["date"])] = day_row

    registry: dict[str, dict[str, Any]] = {}
    for candidate in selected:
        cid = _candidate_id(candidate)
        registry.setdefault(cid, _compact_candidate_registry_entry(candidate, game=profile == "game"))

    out: dict[str, Any] = {
        "view_type": "streaming_index",
        "streaming_profile": profile,
        "target_set": target_set,
        "metadata": {
            **package["metadata"],
            "streaming_index_compaction": f"{profile}_registry_v1",
            "gameplay_filtering_policy": (
                "Foundry retains every source candidate eligible under the gameplay target set; "
                "the game applies final mechanics thresholds."
                if profile == "game"
                else None
            ),
            "daily_sky_source": (
                "embedded_standard_or_full"
                if any((day.get("daily_sky") or {}).get("positions") or day.get("positions") for day in days)
                else "unavailable_in_source"
            ),
        },
        "period": package["period"],
        "candidate_registry": dict(sorted(registry.items())),
        "days_by_date": dict(sorted(days_by_date.items())),
    }

    if profile == "compact":
        out["canonical_graph_summary"] = canonical_graph_from_package(package).get("summary", {})
        out["activated_target_relationship_registry"] = _compact_relationship_registry(package, selected)
        accepted_ids = set(registry)
        out["arcs"] = [
            {
                "arc_id": arc.get("arc_id"),
                "candidate_id": arc.get("candidate_id"),
                "start_date": arc.get("start_date"),
                "end_date": arc.get("end_date"),
                "active_days": arc.get("active_days"),
                "closest_orb": arc.get("closest_orb"),
                "max_relevance_score": arc.get("max_relevance_score"),
            }
            for arc in package.get("transit_arcs", [])
            if str(arc.get("candidate_id")) in accepted_ids
        ]
        out["months"] = package.get("monthly_summary", [])
    return out


def build_from_provider(provider: EphemerisProvider, start: str, end: str, top_n_per_day: int = 20, min_arc_days: int = 2) -> dict[str, Any]:
    logger.info("Building transit package: person=%s start=%s end=%s top_n_per_day=%d min_arc_days=%d", provider.target_metadata().get("target_label") or provider.target_metadata().get("person"), start, end, top_n_per_day, min_arc_days)
    compiler = GraphCompiler.from_provider(provider)
    graph = compiler.graph
    provider.target_chart()["semantic_graph"] = graph
    relationship_registry = _relationship_registry(compiler)
    logger.info("Target graph compiled: objects=%d relationships=%d targets=%d relationship_registry=%d", len(graph.get("objects", [])), len(graph.get("relationships", [])), len(compiler.targets), len(relationship_registry))
    days: list[dict[str, Any]] = []
    arc_rows: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    processed_days = 0
    for day in provider.iter_days():
        if day.date_local < start or day.date_local > end:
            continue
        processed_days += 1
        candidates = _daily_candidates(day, compiler, top_n_per_day)
        if processed_days == 1 or processed_days % 10 == 0:
            logger.info("Transit-period progress: processed_day=%d current_date=%s candidates=%d positions=%d arc_keys=%d", processed_days, day.date_local, len(candidates), len(day.positions), len(arc_rows))
        days.append({
            "date": day.date_local,
            "transit_datetime": day.local_datetime,
            "candidates": candidates,
            "top_candidate": _candidate_ref(candidates[0]) if candidates else None,
            "top_candidate_ref": _candidate_ref(candidates[0]) if candidates else None,
            "positions": day.positions,
            "transit_to_transit_aspects": day.transit_to_transit_aspects,
        })
        for candidate in candidates:
            arc_key = (str(candidate.get("transit_body")), str(candidate.get("aspect")), str(candidate.get("target_id") or candidate.get("target")))
            arc_rows[arc_key].append({"date": day.date_local, **candidate})

    logger.info("Finished daily window collection: days=%d arc_keys=%d", len(days), len(arc_rows))
    arcs = [
        _summarize(rows, f"arc:{_candidate_id(rows[0])}")
        for _, rows in sorted(arc_rows.items(), key=lambda item: item[0])
        if len(rows) >= min_arc_days
    ]
    logger.info("Summarized transit arcs: %d", len(arcs))
    arcs.sort(key=lambda r: (
        -(r.get("active_days") or 0),
        r.get("average_rank") or 99,
        r.get("closest_orb") or 99,
        str(r.get("candidate_id") or ""),
        str(r.get("arc_id") or ""),
    ))

    theme_scores: dict[str, float] = defaultdict(float)
    target_type_counts: dict[str, int] = defaultdict(int)
    activated_relationship_type_counts: dict[str, int] = defaultdict(int)
    rel_type_by_id = {rel_id: rel.get("relationship_type", "UNKNOWN") for rel_id, rel in relationship_registry.items()}
    for arc in arcs:
        score = float(arc.get("max_relevance_score") or 0) * float(arc.get("active_days") or 0)
        target_type_counts[arc.get("target_type", "unknown")] += arc.get("active_days", 0)
        for rel_id in arc.get("activated_target_relationship_refs", []) or []:
            activated_relationship_type_counts[rel_type_by_id.get(rel_id, "UNKNOWN")] += arc.get("active_days", 0)
        for rel_type, count in arc.get("activated_relationship_type_counts", {}).items():
            activated_relationship_type_counts[rel_type] += count
        for tag in arc.get("theme_tags", []):
            theme_scores[tag] += score

    evidence = [
        {
            "id": f"period_claim_{i:04d}",
            "theme": theme,
            "claim": f"The period has a strong {theme.replace('_', ' ')} transit signature.",
            "confidence": min(.99, .45 + score / 10000),
            "supporting_arc_refs": [_arc_ref(arc) for arc in arcs if theme in arc.get("theme_tags", [])][:8],
        }
        for i, (theme, score) in enumerate(sorted(theme_scores.items(), key=lambda kv: (-kv[1], kv[0])), 1)
    ]

    logger.info("Building transit package dictionary: daily_windows=%d arcs=%d evidence=%d", len(days), len(arcs), len(evidence))
    package = {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": PIPELINE_VERSION,
            "analysis_type": "transit_period_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "target_label": provider.target_metadata().get("target_label") or provider.target_metadata().get("person"),
            "target_chart_id": provider.target_metadata().get("target_chart_id"),
            "target_chart_type": provider.target_metadata().get("chart_type"),
            "target_subject_scope": provider.target_metadata().get("subject_scope"),
            "semantic_scope": provider.target_metadata().get("semantic_scope"),
            "provider": provider.target_metadata().get("provider", "cached_or_unknown"),
            "start_date": start,
            "end_date": end,
            "top_n_per_day": top_n_per_day,
            "min_arc_days": min_arc_days,
            "available_views": ["full", "analysis", "streaming_index"],
            "default_cli_outputs": ["analysis", "streaming_index"],
            "graph_compiler": compiler.metadata(),
        },
        "target": {"metadata": provider.target_metadata(), "chart": provider.target_chart()},
        "semantic_graph": graph,
        "compiled_graph": compiler.metadata(),
        "activated_target_relationship_registry": relationship_registry,
        "period": {"start_date": start, "end_date": end, "day_count": len(days)},
        "daily_windows": days,
        "transit_arcs": arcs,
        "monthly_summary": _monthly(days),
        "theme_metrics": [{"theme": k, "score": round(v, 3)} for k, v in sorted(theme_scores.items(), key=lambda kv: (-kv[1], kv[0]))],
        "target_type_metrics": [{"target_type": k, "candidate_count": v} for k, v in sorted(target_type_counts.items())],
        "activated_relationship_type_metrics": [{"relationship_type": k, "activation_count": v} for k, v in sorted(activated_relationship_type_counts.items())],
        "evidence_graph": evidence,
        "report_materials": {
            "recommended_sections": [
                "Source and Extraction Summary",
                "Period Executive Summary",
                "Dominant Transit Arcs",
                "Daily Transit Windows",
                "Monthly / Seasonal Transit Weather",
                "Transit-Family Ranking",
                "Target Semantic Graph Activation Analysis",
                "Theme Metrics",
                "Technical Appendix",
            ],
            "top_transit_arcs": [_arc_ref(arc) for arc in arcs[:20]],
            "top_daily_windows": [_day_ref(day) for day in days[:10]],
            "top_evidence_claims": evidence[:12],
        },
    }
    package["package_views"] = {
        "full": {
            "view_type": "full",
            "materialized_inline": True,
            "note": "The top-level package is the full view. CLI full output is explicit opt-in via --out-full.",
        },
        "analysis": {
            "view_type": "analysis",
            "materialized_inline": False,
            "note": "Use transit_period.analysis_view(package) or CLI --out-analysis/default output to materialize this compact view.",
        },
        "streaming_index": {
            "view_type": "streaming_index",
            "materialized_inline": False,
            "note": "Use transit_period.streaming_index(package) or CLI --out-streaming-index/default output to materialize this compact view.",
        },
    }
    logger.info("Transit-period package complete: days=%d arcs=%d", len(days), len(arcs))
    return finalize_package_semantic_boundary(package)


def analysis_view(package: dict[str, Any]) -> dict[str, Any]:
    """Materialize the compact analysis view for report/downstream consumers."""
    return finalize_view_semantic_boundary(_analysis_view(package), package)


def streaming_index(
    package: dict[str, Any],
    *,
    profile: str = "standard",
    target_set: str | None = None,
    daily_sky_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Materialize a deterministic date-indexed Transit view.

    Profiles:
    - standard: legacy rich streaming/index artifact.
    - compact: reduced general-purpose date index and registries.
    - game: gameplay target set, daily sky state, and active contacts only.
    """
    return finalize_view_semantic_boundary(
        _streaming_index(
            package,
            profile=profile,
            target_set=target_set,
            daily_sky_source=daily_sky_source,
        ),
        package,
    )


def build(
    *,
    start: str,
    end: str,
    provider: str = "cached",
    person_jsonl: str | None = None,
    target_dataset: str | None = None,
    global_jsonl: str | None = None,
    snapshot_timezone: str = "America/Denver",
    snapshot_time: str = "12:00",
    ephe_path: str = ".",
    top_n_per_day: int = 20,
    min_arc_days: int = 2,
):
    logger.info("transit_period.build called provider=%s start=%s end=%s", provider, start, end)
    ep = create_provider(provider, person_jsonl=person_jsonl, target_dataset=target_dataset, global_jsonl=global_jsonl, config=ProviderConfig(start=start, end=end, snapshot_timezone=snapshot_timezone, snapshot_time=snapshot_time, ephe_path=ephe_path))
    return build_from_provider(ep, start, end, top_n_per_day, min_arc_days)
