from __future__ import annotations

import re
from collections.abc import Iterable
from hashlib import sha256
from typing import Any

SOURCE_CHART_ID_MAX_LENGTH = 200
SOURCE_CHART_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$"
RELATIONSHIP_CHART_IDENTITY_VERSION = "relationship_chart_identity_v1.0.0"
_SOURCE_CHART_ID_RE = re.compile(SOURCE_CHART_ID_PATTERN, re.ASCII)


def validate_source_chart_id(value: Any, *, field_name: str = "source_chart_id") -> str | None:
    """Validate and preserve an optional caller-owned canonical chart ID."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string when supplied")
    if not _SOURCE_CHART_ID_RE.fullmatch(value):
        raise ValueError(
            f"{field_name} must be 1-{SOURCE_CHART_ID_MAX_LENGTH} ASCII characters, "
            "begin with a letter or digit, and contain only letters, digits, '.', '_', ':', '/', or '-'"
        )
    return value


def resolve_explicit_source_chart_id(
    carriers: Iterable[tuple[str, Any]],
) -> str | None:
    """Resolve equal explicit identity carriers and reject disagreement."""
    supplied: list[tuple[str, str]] = []
    for field_name, value in carriers:
        if value is None:
            continue
        supplied.append(
            (field_name, validate_source_chart_id(value, field_name=field_name) or "")
        )
    distinct = {value for _, value in supplied}
    if len(distinct) > 1:
        details = ", ".join(f"{name}={value!r}" for name, value in supplied)
        raise ValueError(f"Conflicting explicit source chart identities: {details}")
    return supplied[0][1] if supplied else None


def derive_relationship_source_chart_id(
    chart_type: str,
    participant_source_chart_ids: Iterable[str],
) -> str:
    """Derive an order-independent relationship chart ID from participant charts."""
    normalized_type = str(chart_type).lower()
    if normalized_type not in {"composite", "davison"}:
        raise ValueError("Relationship chart identity supports composite or davison charts")
    participants = sorted(
        validate_source_chart_id(value, field_name="participant_source_chart_id") or ""
        for value in participant_source_chart_ids
    )
    if len(participants) != 2:
        raise ValueError("Relationship chart identity requires exactly two participant chart IDs")
    payload = "|".join((RELATIONSHIP_CHART_IDENTITY_VERSION, normalized_type, *participants))
    return f"{normalized_type}:{sha256(payload.encode('utf-8')).hexdigest()[:32]}"


def source_chart_id_from_natal_package(
    package: dict[str, Any],
    *,
    fallback_name: str,
) -> str:
    """Resolve a Natal package's canonical identity with legacy-name fallback."""
    metadata = package.get("metadata") if isinstance(package.get("metadata"), dict) else {}
    transitable = package.get("transitable_chart") if isinstance(package.get("transitable_chart"), dict) else {}
    canonical = package.get("canonical_astrology_graph") if isinstance(package.get("canonical_astrology_graph"), dict) else {}
    natal = package.get("natal") if isinstance(package.get("natal"), dict) else {}
    person = package.get("person") if isinstance(package.get("person"), dict) else {}
    explicit = resolve_explicit_source_chart_id(
        (
            ("transitable_chart.chart_identity.chart_id", (transitable.get("chart_identity") or {}).get("chart_id")),
            ("metadata.source_chart_id", metadata.get("source_chart_id")),
            ("canonical_astrology_graph.source_chart_id", canonical.get("source_chart_id")),
            ("natal.source_chart_id", natal.get("source_chart_id")),
            ("person.source_chart_id", person.get("source_chart_id")),
        )
    )
    if explicit:
        return explicit
    fallback = "".join(ch if ch.isalnum() else "_" for ch in fallback_name.strip().lower())
    return f"natal:{fallback.strip('_') or 'unknown'}"
