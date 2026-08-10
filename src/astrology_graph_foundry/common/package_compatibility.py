from __future__ import annotations

from typing import Any

BOUNDED_NATAL_ANALYSIS_TYPE = "bounded_natal_dataset"


class BoundedNatalCompatibilityError(ValueError):
    """Raised when an exact-only consumer receives a bounded Natal package."""


def is_bounded_natal_package(package: dict[str, Any]) -> bool:
    metadata = package.get("metadata") if isinstance(package.get("metadata"), dict) else {}
    graph = package.get("canonical_astrology_graph") if isinstance(package.get("canonical_astrology_graph"), dict) else {}
    return metadata.get("analysis_type") == BOUNDED_NATAL_ANALYSIS_TYPE or graph.get("graph_type") == "bounded_canonical_astrology_graph"


def require_exact_chart_package(package: dict[str, Any], *, consumer: str) -> None:
    if is_bounded_natal_package(package):
        raise BoundedNatalCompatibilityError(
            f"{consumer} does not support bounded_natal_dataset or "
            "bounded_canonical_astrology_graph.v1. This artifact intentionally has "
            "no exact longitudes, houses, angles, or exact TransitableChart "
            "capabilities. Use an exact Natal package or a future explicitly "
            "bounded-compatible consumer."
        )
