"""Installed-safe access to packaged Foundry contracts and their identities."""

from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from typing import Any

from ._version import __version__

RUNTIME_PACKAGE_MANIFEST_TYPE = "astrology_graph_foundry_runtime_package_manifest.v1"
SCHEMA_PACKAGE = "astrology_graph_foundry.schemas"
VERSION_PROPERTY_NAMES = {
    "contract_version",
    "graph_version",
    "interface_version",
    "pipeline_version",
    "schema_version",
}


def schema_names() -> tuple[str, ...]:
    """Return packaged JSON Schema names in deterministic order."""

    return tuple(
        sorted(
            resource.name
            for resource in files(SCHEMA_PACKAGE).iterdir()
            if resource.is_file() and resource.name.endswith(".json")
        )
    )


def read_schema_bytes(name: str) -> bytes:
    """Read one packaged schema without relying on a source-tree path."""

    if name not in schema_names():
        raise FileNotFoundError(f"Unknown packaged schema: {name}")
    return files(SCHEMA_PACKAGE).joinpath(name).read_bytes()


def read_schema(name: str) -> dict[str, Any]:
    """Decode one packaged JSON Schema."""

    return json.loads(read_schema_bytes(name))


def _declared_versions(schema: dict[str, Any]) -> dict[str, list[str]]:
    versions: dict[str, set[str]] = {}

    def visit(value: Any, property_name: str | None = None) -> None:
        if isinstance(value, dict):
            if property_name in VERSION_PROPERTY_NAMES:
                declared = value.get("const")
                if isinstance(declared, str):
                    versions.setdefault(property_name, set()).add(declared)
                enum = value.get("enum")
                if isinstance(enum, list):
                    versions.setdefault(property_name, set()).update(
                        item for item in enum if isinstance(item, str)
                    )
            for key, child in value.items():
                visit(child, key)
        elif isinstance(value, list):
            for child in value:
                visit(child, property_name)

    visit(schema)
    return {name: sorted(values) for name, values in sorted(versions.items())}


def build_runtime_package_manifest() -> dict[str, Any]:
    """Describe installed schema resources with content-addressed identities."""

    resources = []
    for name in schema_names():
        content = read_schema_bytes(name)
        schema = json.loads(content)
        resources.append(
            {
                "path": f"astrology_graph_foundry/schemas/{name}",
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "schema_id": schema.get("$id"),
                "title": schema.get("title"),
                "declared_versions": _declared_versions(schema),
            }
        )
    return {
        "manifest_type": RUNTIME_PACKAGE_MANIFEST_TYPE,
        "distribution": "astrology-graph-foundry",
        "package": "astrology_graph_foundry",
        "package_version": __version__,
        "resource_count": len(resources),
        "resources": resources,
    }
