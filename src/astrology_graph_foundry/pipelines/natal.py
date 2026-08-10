from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from astrology_graph_foundry.calculation_provenance import build_calculation_provenance
from astrology_graph_foundry.common.chart_graph import build_chart_graph
from astrology_graph_foundry.common.semantic_layers import (
    canonical_graph_from_package,
    finalize_package_semantic_boundary,
    finalize_view_semantic_boundary,
    orthodox_claims_from_package,
    orthodox_metrics_from_package,
    orthodox_report_materials_from_package,
    orthodox_row_annotation,
)
from astrology_graph_foundry.common.themes import operator_hints, theme_tags
from astrology_graph_foundry.common.transitable_chart import descriptor_for_package
from astrology_graph_foundry.ephemeris.models import BirthData, BirthTimeBasis, BoundedBirthData, ProviderConfig
from astrology_graph_foundry.ephemeris.providers import create_provider

SCHEMA_VERSION = "1.1.0"

logger = logging.getLogger(__name__)

def _aggregate_long_running_transits(provider, min_days: int = 14) -> list[dict[str, Any]]:
    logger.info("Aggregating long-running transits min_days=%d", min_days)
    agg = {}
    processed = 0
    for day in provider.iter_days():
        processed += 1
        if processed == 1 or processed % 10 == 0:
            logger.info("Natal transit climate aggregation day %d %s", processed, day.date_local)
        for cand in day.reverse_read_candidates[:15]:
            key = (cand.get("transit_body"), cand.get("aspect"), cand.get("natal_target"))
            row = agg.setdefault(key, {"dates": [], "orbs": [], "ranks": [], "scores": [], **cand})
            row["dates"].append(day.date_local)
            row["orbs"].append(float(cand.get("orb", 99)))
            row["ranks"].append(float(cand.get("rank", 99)))
            row["scores"].append(float(cand.get("relevance_score", 0)))
    out = []
    for row in agg.values():
        if len(row["dates"]) < min_days:
            continue
        out.append({
            "transit_body": row.get("transit_body"),
            "aspect": row.get("aspect"),
            "natal_target": row.get("natal_target"),
            "count_days_top15": len(row["dates"]),
            "first_date": min(row["dates"]),
            "last_date": max(row["dates"]),
            "closest_orb": min(row["orbs"]),
            "average_rank": sum(row["ranks"]) / len(row["ranks"]),
            "max_relevance_score": max(row["scores"]),
            "natal_target_house": row.get("natal_target_house"),
            "transit_house_in_natal_chart": row.get("transit_house_in_natal_chart"),
            "theme_tags": theme_tags(row.get("transit_body"), row.get("natal_target"), row.get("natal_target_house"), aspect=row.get("aspect")),
            "semantic_operator_hints": operator_hints(row.get("transit_body"), row.get("natal_target"), aspect=row.get("aspect")),
        })
    logger.info("Long-running transit aggregation complete: days=%d arc_count=%d", processed, len(out))
    out.sort(key=lambda r: (-r["count_days_top15"], r["average_rank"], r["closest_orb"]))
    return out

def build(
    *,
    provider: str = "cached",
    person_jsonl: str | None = None,
    natal_dataset: str | None = None,
    global_jsonl: str | None = None,
    name: str | None = None,
    birth_local: str | None = None,
    birth_local_earliest: str | None = None,
    birth_local_latest: str | None = None,
    birth_date: str | None = None,
    birth_time_unknown: bool = False,
    birth_timezone: str | None = None,
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    birth_location_label: str = "",
    source_chart_id: str | None = None,
    start: str | None = None,
    end: str | None = None,
    snapshot_timezone: str = "America/Denver",
    snapshot_time: str = "12:00",
    ephe_path: str = ".",
    house_system: str = "P",
    ephemeris_mode: str = "auto",
    include_optional_points: bool = True,
) -> dict[str, Any]:
    logger.info("Building natal package provider=%s name=%s natal_dataset=%s start=%s end=%s", provider, name, natal_dataset, start, end)
    birth_data = None
    if provider == "live" and natal_dataset is None:
        bounded_carriers = any((birth_local_earliest, birth_local_latest, birth_date, birth_time_unknown))
        if birth_local and bounded_carriers:
            raise ValueError("Exact --birth-local cannot be combined with bounded or unknown-time birth inputs")
        missing = [
            flag for flag, value in {
                "name": name,
                "birth_time": birth_local or birth_local_earliest or (birth_date if birth_time_unknown else None),
                "birth_timezone": birth_timezone,
                "birth_lat": birth_lat,
                "birth_lon": birth_lon,
            }.items()
            if value is None or value == ""
        ]
        if missing:
            raise ValueError(
                "provider='live' requires either natal_dataset or complete birth data. Missing: "
                + ", ".join(missing)
            )
        if bounded_carriers:
            if birth_time_unknown:
                if not birth_date or birth_local_earliest or birth_local_latest:
                    raise ValueError("unknown-time input requires --birth-time-unknown and --birth-date only")
                basis = BirthTimeBasis(mode="unknown_time", birth_date=birth_date)
            else:
                if birth_date or not birth_local_earliest or not birth_local_latest:
                    raise ValueError("bounded input requires both birth_local_earliest and birth_local_latest")
                basis = BirthTimeBasis(
                    mode="bounded",
                    earliest_local=birth_local_earliest,
                    latest_local=birth_local_latest,
                )
            BoundedBirthData(
                name=name or "Unknown",
                birth_time_basis=basis,
                birth_timezone=birth_timezone or "",
                birth_lat=float(birth_lat),
                birth_lon=float(birth_lon),
                birth_location_label=birth_location_label,
                source_chart_id=source_chart_id,
            )
            raise NotImplementedError(
                "Bounded birth-time input is valid, but bounded Natal calculation is not implemented until Slice 3"
            )
        birth_data = BirthData(
            name=name or "Unknown",
            birth_local=birth_local or "",
            birth_timezone=birth_timezone or "",
            birth_lat=float(birth_lat),
            birth_lon=float(birth_lon),
            birth_location_label=birth_location_label,
            source_chart_id=source_chart_id,
        )

    provider_config = ProviderConfig(
        start=start,
        end=end,
        snapshot_timezone=snapshot_timezone,
        snapshot_time=snapshot_time,
        ephe_path=ephe_path,
        house_system=house_system,
        ephemeris_mode=ephemeris_mode,
        include_optional_points=include_optional_points,
    )
    ep = create_provider(
        provider,
        person_jsonl=person_jsonl,
        target_dataset=natal_dataset,
        birth_data=birth_data,
        global_jsonl=global_jsonl,
        config=provider_config,
    )
    existing_graph = ep.natal_chart().get("semantic_graph")
    if existing_graph:
        logger.info("Reusing provider-compiled natal semantic graph")
        graph = existing_graph
    else:
        logger.info("Building natal semantic graph")
        graph = build_chart_graph(ep.natal_chart())
        ep.natal_chart()["semantic_graph"] = graph
    long_transits = _aggregate_long_running_transits(ep) if start and end else []
    themes: dict[str, dict[str, Any]] = {}
    for tr in long_transits[:50]:
        for tag in tr["theme_tags"]:
            themes.setdefault(tag, {"score": 0, "evidence": []})
            themes[tag]["score"] += tr["count_days_top15"]
            themes[tag]["evidence"].append(tr)

    evidence_graph = [
        {
            "id": f"claim_{i:04d}",
            "theme": theme,
            "claim": f"{ep.person_metadata().get('person')} has a strong {theme.replace('_', ' ')} transit activation signature.",
            "confidence": min(0.99, 0.45 + data["score"] / 365),
            "supporting_observations": data["evidence"][:8],
        }
        for i, (theme, data) in enumerate(sorted(themes.items(), key=lambda kv: -kv[1]["score"]), 1)
    ]

    logger.info("Natal package complete person=%s graph_objects=%d graph_relationships=%d long_transits=%d", ep.person_metadata().get("person"), len(graph.get("objects", [])), len(graph.get("relationships", [])), len(long_transits))
    provider_chart_id = ep.person_metadata().get("target_chart_id") or ep.person_metadata().get("source_chart_id")
    runtime_provenance = getattr(ep, "calculation_runtime_provenance", None)
    provider_runtime = (
        runtime_provenance()
        if callable(runtime_provenance)
        else {
            "mode": "live_calculation" if birth_data is not None else "cached_replay",
            "provider": ep.person_metadata().get("provider") or "unknown",
            "calculation_runtime": "not_reported_by_provider",
        }
    )
    package = {
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "analysis_type": "natal_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "person": ep.person_metadata().get("person"),
            **({"source_chart_id": provider_chart_id} if provider_chart_id else {}),
            "provider": ep.person_metadata().get("provider"),
            "start_date": start,
            "end_date": end,
            "live_natal_computation": provider == "live" and natal_dataset is None,
            "calculation_provenance": build_calculation_provenance(
                birth_data=birth_data,
                natal_chart=ep.natal_chart(),
                config=provider_config,
                    provider_runtime=provider_runtime,
            ),
        },
        "person": ep.person_metadata(),
        "natal": ep.natal_chart(),
        "semantic_graph": graph,
        "transit_climate": {"long_running_transits": long_transits},
        "theme_metrics": themes,
        "evidence_graph": evidence_graph,
        "report_materials": {
            "recommended_sections": [
                "Source and Extraction Summary",
                "Natal Core",
                "Big Three",
                "Planet-by-Planet",
                "House Analysis",
                "Aspect Synthesis",
                "Transit Climate",
                "Technical Appendix",
            ],
            "top_evidence": evidence_graph[:12],
        },
    }
    package["transitable_chart"] = descriptor_for_package(package)
    return finalize_package_semantic_boundary(package)


def analysis_view(package: dict[str, Any], *, top_relationship_limit: int = 80, top_object_limit: int = 80) -> dict[str, Any]:
    """Compact natal view for lightweight report/game/infographic consumers."""
    graph = canonical_graph_from_package(package)
    objects = graph.get("objects", []) or []
    relationships = graph.get("relationships", []) or []
    def object_weight(obj: dict[str, Any]) -> tuple[int, str]:
        priority = {
            "planet_or_point": 0,
            "angle": 1,
            "calculated_point": 2,
            "lot": 3,
            "dignity_state": 4,
            "antiscia_point": 5,
            "contra_antiscia_point": 6,
            "harmonic_point": 7,
        }.get(str(obj.get("object_type")), 9)
        return priority, str(obj.get("id") or obj.get("name"))
    compact_objects = [
        {k: obj.get(k) for k in ("id", "object_type", "name", "source_key", "longitude", "sign", "house", "pretty", "element", "modality", "ruler", "dignity_state") if obj.get(k) is not None}
        for obj in sorted(objects, key=object_weight)[:top_object_limit]
    ]
    compact_relationships = []
    for rel in relationships[:top_relationship_limit]:
        projected = orthodox_row_annotation(rel)
        compact_relationships.append({
            k: projected.get(k)
            for k in (
                "id", "relationship_id", "relationship_type", "source",
                "target", "source_id", "target_id", "source_name",
                "target_name", "aspect", "orb", "weight", "theme_tags",
                "orthodox_astrology_theme_tags", "semantic_operator_hints",
            )
            if projected.get(k) is not None
        })
    view = {
        "metadata": {**package.get("metadata", {}), "view_type": "natal_analysis", "view_compaction": "semantic_graph_summary_v1"},
        "person": package.get("person"),
        "natal_summary": {
            "bodies": package.get("natal", {}).get("bodies", {}),
            "houses": package.get("natal", {}).get("houses", {}),
            "angles": package.get("natal", {}).get("angles", {}),
            "lots": package.get("natal", {}).get("lots", {}),
            "sect": package.get("natal", {}).get("sect", {}),
        },
        "canonical_graph_summary": graph.get("summary", {}),
        "top_objects": compact_objects,
        "top_relationships": compact_relationships,
        "transit_climate_summary": {"long_running_transits": package.get("transit_climate", {}).get("long_running_transits", [])[:30]},
        "orthodox_projection_extract": {
            "theme_metrics": orthodox_metrics_from_package(package),
            "claim_candidates": orthodox_claims_from_package(package)[:20],
            "report_materials": orthodox_report_materials_from_package(package),
        },
    }
    return finalize_view_semantic_boundary(view, package)
