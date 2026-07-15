from __future__ import annotations

"""Projection-neutral temporal activation export.

This module converts Foundry transit packages into a canonical, arc-first
temporal source graph.  It does not assign target-domain meaning.  Semantic
Projection Core may later consume this contract to create
``projected_temporal_activation_graph.v1`` artifacts.

The current exporter accepts full Transit packages and streaming-index Transit
materializations.  Compact analysis views are intentionally rejected because
they may contain only a ranked subset of arcs and are therefore not a complete
temporal source contract.
"""

from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha256
from typing import Any, Iterable

CANONICAL_TEMPORAL_GRAPH_VERSION = "1.0.0"
CANONICAL_TEMPORAL_GRAPH_TYPE = "canonical_temporal_activation_graph"
SUPPORTED_ANALYSIS_TYPES = {
    "transit_dataset",
    "transit_range_dataset",
    "transit_period_dataset",
}


class TemporalSourceContractError(ValueError):
    """Raised when a package cannot produce a truthful temporal source graph."""


@dataclass(frozen=True)
class TemporalExportOptions:
    max_observation_gap_days: int = 2
    sampled_exact_orb: float = 0.01
    include_observation_states: bool = True

    def validate(self) -> None:
        if self.max_observation_gap_days < 1:
            raise ValueError("max_observation_gap_days must be at least 1")
        if self.sampled_exact_orb < 0:
            raise ValueError("sampled_exact_orb must be non-negative")


def _stable_token(*parts: Any, length: int = 20) -> str:
    payload = "|".join(str(part if part is not None else "") for part in parts)
    return sha256(payload.encode("utf-8")).hexdigest()[:length]


def _slug(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    text = "".join(ch if ch.isalnum() else "_" for ch in text)
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_") or "unknown"


def _date(value: Any) -> date:
    text = str(value or "")
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise TemporalSourceContractError(
            f"Temporal observation date is not ISO-compatible: {value!r}"
        ) from exc


def _analysis_type(package: dict[str, Any]) -> str:
    return str((package.get("metadata") or {}).get("analysis_type") or "")


def _materialization_kind(package: dict[str, Any]) -> str:
    view_type = str(package.get("view_type") or "")
    if view_type == "streaming_index" or (
        "days" in package and "candidate_registry" in package and "arcs" in package
    ):
        return "streaming_index"
    if "daily_windows" in package and "transit_arcs" in package:
        return "full"
    if view_type == "analysis":
        return "analysis"
    return "unknown"


def _target_identity(package: dict[str, Any]) -> dict[str, Any]:
    metadata = package.get("metadata") or {}
    target = package.get("target") or {}
    target_metadata = target.get("metadata") or {}
    chart_identity = (
        target.get("chart_identity")
        or target_metadata.get("chart_identity")
        or (package.get("transitable_chart") or {}).get("chart_identity")
        or {}
    )
    chart_id = (
        chart_identity.get("chart_id")
        or metadata.get("target_chart_id")
        or target_metadata.get("target_chart_id")
        or f"{metadata.get('target_chart_type', 'chart')}:{_slug(metadata.get('target_label'))}"
    )
    return {
        "chart_id": str(chart_id),
        "chart_type": (
            chart_identity.get("chart_type")
            or metadata.get("target_chart_type")
            or target_metadata.get("chart_type")
        ),
        "subject_scope": (
            chart_identity.get("subject_scope")
            or metadata.get("target_subject_scope")
            or target_metadata.get("subject_scope")
        ),
        "semantic_scope": (
            chart_identity.get("semantic_scope")
            or metadata.get("semantic_scope")
            or target_metadata.get("semantic_scope")
        ),
        "label": (
            chart_identity.get("label")
            or metadata.get("target_label")
            or target_metadata.get("target_label")
        ),
    }


def _period(package: dict[str, Any]) -> dict[str, Any]:
    period = dict(package.get("period") or {})
    metadata = package.get("metadata") or {}
    start = (
        period.get("start_at")
        or period.get("start")
        or period.get("start_date")
        or metadata.get("start_date")
    )
    end = (
        period.get("end_at")
        or period.get("end")
        or period.get("end_date")
        or metadata.get("end_date")
    )
    return {
        "start_at": start,
        "end_at": end,
        "day_count": period.get("day_count"),
    }


def _full_day_rows(package: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for day in package.get("daily_windows", []) or []:
        for candidate in day.get("candidates", []) or []:
            row = dict(candidate)
            row["date"] = day.get("date")
            row["transit_datetime"] = day.get("transit_datetime")
            row["positions"] = day.get("positions") or {}
            rows.append(row)
    return rows


def _streaming_day_rows(package: dict[str, Any]) -> list[dict[str, Any]]:
    registry = package.get("candidate_registry") or {}
    rows: list[dict[str, Any]] = []
    for day in package.get("days", []) or []:
        for mutable in day.get("candidate_refs", []) or []:
            candidate_id = str(mutable.get("candidate_id") or "")
            static = dict(registry.get(candidate_id) or {})
            row = {**static, **mutable}
            row["date"] = day.get("date")
            row["transit_datetime"] = day.get("transit_datetime")
            rows.append(row)
    return rows


def _arc_rows(package: dict[str, Any], materialization: str) -> list[dict[str, Any]]:
    key = "transit_arcs" if materialization == "full" else "arcs"
    return [dict(row) for row in package.get(key, []) or []]


def _candidate_id(row: dict[str, Any]) -> str:
    """Return the canonical Transit candidate identifier.

    Full Transit daily candidates do not materialize ``candidate_id``.  Their
    parent pipeline uses case-preserving body/aspect tokens and only normalizes
    spaces/colons in the target token.  Temporal export must reproduce that
    algorithm exactly so daily observations join the summarized arc rows.
    """

    explicit = row.get("candidate_id")
    if explicit:
        return str(explicit)
    transit_body = str(row.get("transit_body") or "unknown").replace(" ", "_")
    aspect = str(row.get("aspect") or "unknown").replace(" ", "_")
    target = (
        str(row.get("target_id") or row.get("target") or "unknown")
        .replace(" ", "_")
        .replace(":", "_")
    )
    return f"tc:{transit_body}:{aspect}:{target}"


def _candidate_signature(row: dict[str, Any]) -> tuple[str, str, str]:
    """Return a tolerant semantic join key for older/materialized packages."""

    return (
        _slug(row.get("transit_body")),
        _slug(row.get("aspect")),
        _slug(row.get("target_id") or row.get("target")),
    )


def _split_contiguous(
    rows: list[dict[str, Any]], *, max_gap_days: int
) -> list[list[dict[str, Any]]]:
    ordered = sorted(rows, key=lambda row: (str(row.get("date") or ""), float(row.get("orb") or 999)))
    if not ordered:
        return []
    segments: list[list[dict[str, Any]]] = [[ordered[0]]]
    for row in ordered[1:]:
        previous = segments[-1][-1]
        gap = (_date(row.get("date")) - _date(previous.get("date"))).days
        if gap > max_gap_days:
            segments.append([row])
        else:
            segments[-1].append(row)
    return segments


def _phase_states(rows: list[dict[str, Any]], exact_threshold: float) -> list[dict[str, Any]]:
    if not rows:
        return []
    ordered = sorted(rows, key=lambda row: str(row.get("date") or ""))
    closest_index = min(
        range(len(ordered)),
        key=lambda index: float(ordered[index].get("orb") if ordered[index].get("orb") is not None else 999),
    )
    states: list[dict[str, Any]] = []
    for index, row in enumerate(ordered):
        orb = row.get("orb")
        if orb is not None and float(orb) <= exact_threshold:
            phase = "sampled_exact"
        elif index < closest_index:
            phase = "applying_observed"
        elif index > closest_index:
            phase = "separating_observed"
        else:
            phase = "closest_observed"
        state = {
            "state_id": f"temporal_state:{_stable_token(_candidate_id(row), row.get('date'), row.get('transit_datetime'))}",
            "observed_at": row.get("transit_datetime") or row.get("date"),
            "date": row.get("date"),
            "phase": phase,
            "orb": row.get("orb"),
            "distance": row.get("distance"),
            "rank": row.get("rank"),
            "relevance_score": row.get("relevance_score"),
            "strength_label": row.get("strength"),
        }
        positions = row.get("positions") or {}
        body = str(row.get("transit_body") or "")
        position = (
            positions.get(body)
            or positions.get(f"n{body}")
            or positions.get(body[1:] if body.startswith("n") else "")
            or {}
        )
        if isinstance(position, dict) and position:
            state["activator_state"] = {
                "longitude": position.get("longitude"),
                "latitude": position.get("latitude"),
                "speed": position.get("speed"),
                "retrograde": position.get("retrograde"),
                "sign": position.get("sign"),
                "house": position.get("house"),
            }
        states.append(state)
    return states


def _motion_summary(states: list[dict[str, Any]]) -> dict[str, Any]:
    values: list[str] = []
    for state in states:
        activator = state.get("activator_state") or {}
        retrograde = activator.get("retrograde")
        speed = activator.get("speed")
        if retrograde is True or (isinstance(speed, (int, float)) and speed < 0):
            values.append("retrograde")
        elif retrograde is False or isinstance(speed, (int, float)):
            values.append("direct")
    distinct = sorted(set(values))
    return {
        "states": distinct,
        "changes_motion_within_activation": len(distinct) > 1,
    }


def _source_graph_ref(package: dict[str, Any]) -> dict[str, Any]:
    graph = package.get("canonical_astrology_graph") or {}
    metadata = graph.get("metadata") or {}
    return {
        "graph_type": graph.get("graph_type") or CANONICAL_TEMPORAL_GRAPH_TYPE,
        "graph_version": graph.get("graph_version"),
        "graph_id": metadata.get("graph_id") or graph.get("id"),
    }


def extract_canonical_temporal_activation_graph(
    package: dict[str, Any],
    *,
    options: TemporalExportOptions | None = None,
) -> dict[str, Any]:
    """Normalize a Foundry transit package into an arc-first temporal graph.

    The exporter preserves temporal facts and provenance but adds no projected
    interpretation.  Existing Transit arcs identify candidate processes; daily
    observations provide phase, orb, motion, and repeated-pass segmentation.
    """

    options = options or TemporalExportOptions()
    options.validate()

    analysis_type = _analysis_type(package)
    if analysis_type not in SUPPORTED_ANALYSIS_TYPES:
        raise TemporalSourceContractError(
            "Canonical temporal export currently supports Transit packages only; "
            f"received analysis_type={analysis_type!r}."
        )

    materialization = _materialization_kind(package)
    if materialization == "analysis":
        raise TemporalSourceContractError(
            "Transit analysis views may contain only a ranked subset of activation "
            "arcs and cannot be exported as a complete canonical temporal graph. "
            "Use the full or streaming_index Transit materialization."
        )
    if materialization not in {"full", "streaming_index"}:
        raise TemporalSourceContractError(
            "Transit package is missing the full/streaming temporal structures "
            "required for canonical temporal export."
        )

    day_rows = (
        _full_day_rows(package)
        if materialization == "full"
        else _streaming_day_rows(package)
    )
    rows_by_candidate: dict[str, list[dict[str, Any]]] = {}
    rows_by_signature: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in day_rows:
        rows_by_candidate.setdefault(_candidate_id(row), []).append(row)
        rows_by_signature.setdefault(_candidate_signature(row), []).append(row)

    target_identity = _target_identity(package)
    source_period = _period(package)
    activators: dict[str, dict[str, Any]] = {}
    activations: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for arc in sorted(
        _arc_rows(package, materialization),
        key=lambda row: (
            str(row.get("candidate_id") or ""),
            str(row.get("start_date") or ""),
            str(row.get("arc_id") or ""),
        ),
    ):
        candidate_id = _candidate_id(arc)
        observations = rows_by_candidate.get(candidate_id, [])
        observation_join_policy = "candidate_id_exact"
        if not observations:
            observations = rows_by_signature.get(_candidate_signature(arc), [])
            if observations:
                observation_join_policy = "semantic_signature_fallback"
        if not observations:
            observation_join_policy = "arc_summary_fallback"
            warnings.append(
                {
                    "code": "activation_arc_without_observations",
                    "arc_id": arc.get("arc_id"),
                    "candidate_id": candidate_id,
                }
            )
            # Retain an arc summary rather than silently dropping it.
            observations = [
                {
                    **arc,
                    "date": arc.get("start_date"),
                    "transit_datetime": arc.get("start_date"),
                    "orb": arc.get("closest_orb"),
                }
            ]

        segments = _split_contiguous(
            observations,
            max_gap_days=options.max_observation_gap_days,
        )
        sequence_id = f"temporal_sequence:{_stable_token(target_identity.get('chart_id'), candidate_id)}"
        for pass_index, segment in enumerate(segments, 1):
            states = _phase_states(segment, options.sampled_exact_orb)
            closest = min(
                states,
                key=lambda state: float(state.get("orb") if state.get("orb") is not None else 999),
            )
            transit_body = arc.get("transit_body") or segment[0].get("transit_body")
            aspect = arc.get("aspect") or segment[0].get("aspect")
            target_id = arc.get("target_id") or segment[0].get("target_id") or arc.get("target")
            activator_ref = f"canonical:transiting_object:{_slug(transit_body)}"
            activators.setdefault(
                activator_ref,
                {
                    "id": activator_ref,
                    "object_type": "transiting_object",
                    "name": transit_body,
                    "source_body": transit_body,
                },
            )

            start_at = states[0].get("observed_at")
            end_at = states[-1].get("observed_at")
            sampled_exact = closest.get("phase") == "sampled_exact"
            activation_id = (
                f"temporal_activation:{_stable_token(sequence_id, pass_index, start_at, end_at)}"
            )
            source_refs = [
                f"transit_arc:{arc.get('arc_id') or candidate_id}",
                f"transit_candidate:{candidate_id}",
                *[
                    f"transit_observation:{state.get('date')}:{candidate_id}"
                    for state in states
                ],
            ]
            activation = {
                "id": activation_id,
                "sequence_id": sequence_id,
                "pass_index": pass_index,
                "activation_type": "transit_aspect_arc",
                "activator_ref": activator_ref,
                "target_ref": str(target_id),
                "target_chart_ref": target_identity.get("chart_id"),
                "relationship_type": "TRANSIT_ACTIVATION",
                "aspect": aspect,
                "start_at": start_at,
                "closest_observed_at": closest.get("observed_at"),
                "exact_at": closest.get("observed_at") if sampled_exact else None,
                "end_at": end_at,
                "exactness": {
                    "status": "sampled_exact" if sampled_exact else "closest_observed_only",
                    "closest_orb": closest.get("orb"),
                    "sampled_exact_orb_threshold": options.sampled_exact_orb,
                    "note": (
                        "Exact time is a sampled observation, not a solved exact event."
                        if sampled_exact
                        else "No solved exact event is asserted by this source package."
                    ),
                },
                "motion": _motion_summary(states),
                "target_type": arc.get("target_type") or segment[0].get("target_type"),
                "target_house": arc.get("target_house") or segment[0].get("target_house"),
                "transit_house_in_target_chart": (
                    arc.get("transit_house_in_target_chart")
                    or segment[0].get("transit_house_in_target_chart")
                ),
                "observation_count": len(states),
                "observation_states": states if options.include_observation_states else [],
                "source_refs": source_refs,
                "provenance": {
                    "source_analysis_type": analysis_type,
                    "source_materialization": materialization,
                    "source_arc_id": arc.get("arc_id"),
                    "source_candidate_id": candidate_id,
                    "normalization_policy": "arc_first_with_observation_segmentation.v1",
                    "observation_join_policy": observation_join_policy,
                    "max_observation_gap_days": options.max_observation_gap_days,
                },
            }
            activations.append(activation)

    activations.sort(
        key=lambda row: (
            str(row.get("start_at") or ""),
            str(row.get("activator_ref") or ""),
            str(row.get("target_ref") or ""),
            str(row.get("aspect") or ""),
            int(row.get("pass_index") or 0),
            str(row.get("id") or ""),
        )
    )
    graph_id = f"canonical_temporal_graph:{_stable_token(target_identity.get('chart_id'), source_period, [(row['id'], row['start_at'], row['end_at']) for row in activations])}"

    by_activator: dict[str, list[str]] = {}
    by_target: dict[str, list[str]] = {}
    by_month: dict[str, list[str]] = {}
    for row in activations:
        by_activator.setdefault(str(row["activator_ref"]), []).append(row["id"])
        by_target.setdefault(str(row["target_ref"]), []).append(row["id"])
        month = str(row.get("start_at") or "")[:7]
        by_month.setdefault(month, []).append(row["id"])

    return {
        "metadata": {
            "package_type": CANONICAL_TEMPORAL_GRAPH_TYPE,
            "contract_version": CANONICAL_TEMPORAL_GRAPH_VERSION,
            "graph_id": graph_id,
            "source_analysis_type": analysis_type,
            "source_materialization": materialization,
            "projection_neutral": True,
            "authoritative_unit": "activation_arc",
            "normalization_policy": "arc_first_with_observation_segmentation.v1",
        },
        "target_identity": target_identity,
        "period": source_period,
        "source_graph_ref": _source_graph_ref(package),
        "activators": [activators[key] for key in sorted(activators)],
        "activations": activations,
        "indexes": {
            "activation_ids_by_activator": {
                key: sorted(value) for key, value in sorted(by_activator.items())
            },
            "activation_ids_by_target": {
                key: sorted(value) for key, value in sorted(by_target.items())
            },
            "activation_ids_by_start_month": {
                key: sorted(value) for key, value in sorted(by_month.items())
            },
        },
        "summary": {
            "activator_count": len(activators),
            "activation_count": len(activations),
            "sequence_count": len({row["sequence_id"] for row in activations}),
            "sampled_exact_count": sum(
                1
                for row in activations
                if row.get("exactness", {}).get("status") == "sampled_exact"
            ),
            "observation_state_count": sum(
                int(row.get("observation_count") or 0) for row in activations
            ),
            "warning_count": len(warnings),
        },
        "diagnostics": {
            "warnings": warnings,
            "limitations": [
                "Current Transit packages provide sampled observations rather than solved exact-event timestamps.",
                "Repeated passes are segmented by observation gaps and remain conservative until exact-event grouping is available.",
                "Only full and streaming_index Transit materializations are accepted to avoid incomplete analysis-view export.",
            ],
        },
    }
