from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from astrology_graph_foundry.common.aspects import find_aspect, relevance_score
from astrology_graph_foundry.common.chart_graph import (
    REL_TRANSIT_ACTIVATION,
    build_chart_graph,
    normalize_relationship_types,
    relationship_summaries_for_object,
    transit_targets_from_graph,
)
from astrology_graph_foundry.common.geometry import house_for_lon
from astrology_graph_foundry.common.themes import operator_hints, theme_tags

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransitTarget:
    """A compact, immutable transit target compiled from a chart semantic graph."""

    id: str
    name: str
    source_key: str
    object_type: str
    longitude: float
    house: Any = None
    pretty: str | None = None
    activated_relationships: tuple[dict[str, Any], ...] = ()


class GraphCompiler:
    """Precompiled semantic-graph view optimized for transit consumers.

    The raw semantic graph is deliberately rich. That is good for research and
    report generation, but it is wasteful for period transits if every day has
    to re-normalize relationships, rediscover target objects, and re-summarize
    the natal relationship context for each target. GraphCompiler performs that
    work once and exposes compact helpers for daily transit calculations.
    """

    compiler_version = "graph_compiler_v1.0.0"

    def __init__(self, chart: dict[str, Any], *, relationship_limit: int = 12) -> None:
        self.chart = chart
        self.relationship_limit = relationship_limit
        graph = chart.get("semantic_graph") or build_chart_graph(chart)
        self.graph = normalize_relationship_types(graph)
        self.chart["semantic_graph"] = self.graph
        self.cusps = self._compile_cusps(chart)
        self.targets = self._compile_targets()
        self.targets_by_id = {target.id: target for target in self.targets}
        logger.info(
            "GraphCompiler ready: objects=%d relationships=%d targets=%d relationship_limit=%d",
            len(self.graph.get("objects", [])),
            len(self.graph.get("relationships", [])),
            len(self.targets),
            relationship_limit,
        )

    @classmethod
    def from_provider(cls, provider: Any, *, relationship_limit: int = 12) -> "GraphCompiler":
        reusable = getattr(provider, "graph_compiler", None)
        if callable(reusable):
            compiler = reusable(relationship_limit=relationship_limit)
            if compiler is not None:
                logger.info("Reusing provider-compiled GraphCompiler")
                return compiler
        return cls(provider.target_chart(), relationship_limit=relationship_limit)

    @staticmethod
    def _compile_cusps(chart: dict[str, Any]) -> list[float]:
        houses = chart.get("houses") or {}
        return [float(houses[str(i)]["lon"]) for i in range(1, 13) if str(i) in houses]

    def _compile_targets(self) -> tuple[TransitTarget, ...]:
        raw_targets = transit_targets_from_graph(self.chart)
        compiled: list[TransitTarget] = []
        for target in raw_targets:
            lon = target.get("longitude")
            if lon is None:
                continue
            compiled.append(
                TransitTarget(
                    id=str(target["id"]),
                    name=str(target["name"]),
                    source_key=str(target["source_key"]),
                    object_type=str(target["object_type"]),
                    longitude=float(lon),
                    house=target.get("house"),
                    pretty=target.get("pretty"),
                    activated_relationships=tuple(
                        relationship_summaries_for_object(
                            self.graph,
                            str(target["id"]),
                            limit=self.relationship_limit,
                        )
                    ),
                )
            )
        compiled.sort(key=lambda target: (target.id, target.source_key, target.name))
        return tuple(compiled)

    def target_count_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for target in self.targets:
            counts[target.object_type] = counts.get(target.object_type, 0) + 1
        return dict(sorted(counts.items()))

    def transit_candidate_from_target(
        self,
        transit_body: str,
        transit_pos: dict[str, Any],
        target: TransitTarget,
        aspect: dict[str, Any],
    ) -> dict[str, Any]:
        target_name = target.source_key if target.source_key.startswith("n") else f"n{target.name}"
        score = relevance_score(transit_body, target_name, aspect)
        return {
            "orb": aspect["orb"],
            "relevance_score": score,
            "transit_body": transit_body,
            "target": target_name,
            "target_id": target.id,
            "target_name": target.name,
            "target_type": target.object_type,
            "aspect": aspect["aspect"],
            "distance": aspect["distance"],
            "exact_angle": aspect["exact_angle"],
            "major": aspect["major"],
            "strength": aspect["strength"],
            "transit_house_in_target_chart": house_for_lon(transit_pos["lon"], self.cusps) if len(self.cusps) == 12 else None,
            "target_house": target.house,
            "target_pretty": target.pretty,
            "relationship_type": REL_TRANSIT_ACTIVATION,
            "theme_tags": theme_tags(transit_body, target.name, target.house, aspect=aspect["aspect"]),
            "semantic_operator_hints": operator_hints(transit_body, target.name, aspect=aspect["aspect"]),
            "activated_target_relationships": list(target.activated_relationships),
        }

    def transit_to_target_candidates(
        self,
        positions: dict[str, dict[str, Any]],
        *,
        include_minor: bool = True,
        top_n: int | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        rows: list[dict[str, Any]] = []
        for transit_name, transit_pos in positions.items():
            lon = transit_pos.get("lon")
            if lon is None:
                continue
            for target in self.targets:
                aspect = find_aspect(transit_name, float(lon), target.name, target.longitude, include_minor=include_minor)
                if not aspect:
                    continue
                rows.append(self.transit_candidate_from_target(transit_name, transit_pos, target, aspect))
        rows.sort(key=lambda row: (
            float(row["orb"]),
            -float(row["relevance_score"]),
            str(row.get("transit_body")),
            str(row.get("aspect")),
            str(row.get("target_id")),
        ))
        ranked_source = sorted(rows, key=lambda row: (
            -float(row["relevance_score"]),
            float(row["orb"]),
            str(row.get("transit_body")),
            str(row.get("aspect")),
            str(row.get("target_id")),
        ))
        if top_n is not None:
            ranked_source = ranked_source[:top_n]
        ranked = [{**row, "rank": i} for i, row in enumerate(ranked_source, 1)]
        return rows, ranked

    def metadata(self) -> dict[str, Any]:
        return {
            "compiler_version": self.compiler_version,
            "relationship_limit": self.relationship_limit,
            "target_count": len(self.targets),
            "target_type_counts": self.target_count_by_type(),
        }
