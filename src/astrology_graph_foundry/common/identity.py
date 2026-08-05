from __future__ import annotations

import re
from typing import Any

SOURCE_CHART_ID_MAX_LENGTH = 200
SOURCE_CHART_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$"
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
