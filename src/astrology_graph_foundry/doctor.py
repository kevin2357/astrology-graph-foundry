from __future__ import annotations

import importlib.util
import importlib
import json
import platform
import sys
from importlib import metadata

from astrology_graph_foundry import __version__ as PACKAGE_VERSION
from pathlib import Path
from typing import Any


def _distribution_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def _module_status(module_name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(module_name)
    return {
        "available": spec is not None,
        "origin": str(spec.origin) if spec and spec.origin else None,
    }


def _module_attribute(module_name: str, attribute: str) -> str | None:
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None
    value = getattr(module, attribute, None)
    return str(value) if value is not None else None


def build_doctor_report() -> dict[str, Any]:
    package_status = _module_status("astrology_graph_foundry")
    projection_status = _module_status("semantic_projection")
    swiss_status = _module_status("swisseph")
    projection_distribution_version = _distribution_version("semantic-projection-core")
    projection_engine_version = _module_attribute("semantic_projection", "ENGINE_VERSION")
    projection_version_mismatch = bool(
        projection_distribution_version
        and projection_engine_version
        and projection_distribution_version != projection_engine_version
    )
    return {
        "report_type": "astrology_graph_foundry_doctor",
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
            "platform": platform.platform(),
        },
        "foundry": {
            **package_status,
            "package_version": PACKAGE_VERSION,
            "installed_distribution_version": _distribution_version("astrology-graph-foundry"),
        },
        "semantic_projection_core": {
            **projection_status,
            "distribution_version": projection_distribution_version,
            "engine_version": projection_engine_version,
            "version_metadata_matches_engine": not projection_version_mismatch,
            "required_for_projection": True,
        },
        "swiss_ephemeris": {
            **swiss_status,
            "distribution_version": _distribution_version("pyswisseph"),
            "required_for_live_calculation": True,
            "cached_package_workflows_available_without_it": True,
        },
        "capabilities": {
            "read_and_transform_saved_packages": bool(package_status["available"]),
            "project_saved_packages": bool(package_status["available"] and projection_status["available"]),
            "live_ephemeris_calculation": bool(package_status["available"] and swiss_status["available"]),
        },
        "recommendations": [
            *([] if projection_status["available"] else [
                "Install Semantic Projection Core for projection workflows."
            ]),
            *([] if not projection_version_mismatch else [
                "Semantic Projection Core distribution metadata does not match its imported engine version. "
                "Reinstall the editable Semantic Projection Core package to refresh installation metadata."
            ]),
            *([] if swiss_status["available"] else [
                "Install the Foundry live extra in an environment with a compatible pyswisseph wheel: "
                "python -m pip install -e .[live]. Graph-only and saved-package workflows remain available."
            ]),
        ],
    }


def render_doctor_report(report: dict[str, Any]) -> str:
    lines = [
        "Astrology Graph Foundry doctor",
        "==============================",
        f"Python: {report['python']['version']} ({report['python']['executable']})",
        f"Foundry: {'OK' if report['foundry']['available'] else 'MISSING'}"
        + (f" {report['foundry']['package_version']}" if report['foundry']['package_version'] else ""),
        f"Semantic Projection Core: {'OK' if report['semantic_projection_core']['available'] else 'MISSING'}"
        + (f" {report['semantic_projection_core']['distribution_version']}" if report['semantic_projection_core']['distribution_version'] else "")
        + (
            f" (engine {report['semantic_projection_core']['engine_version']})"
            if report['semantic_projection_core']['engine_version']
            and report['semantic_projection_core']['engine_version'] != report['semantic_projection_core']['distribution_version']
            else ""
        ),
        f"Swiss Ephemeris / live calculations: {'OK' if report['swiss_ephemeris']['available'] else 'UNAVAILABLE'}",
        "",
        "Capabilities:",
        f"  Saved-package workflows: {'yes' if report['capabilities']['read_and_transform_saved_packages'] else 'no'}",
        f"  Projection workflows: {'yes' if report['capabilities']['project_saved_packages'] else 'no'}",
        f"  Live calculation workflows: {'yes' if report['capabilities']['live_ephemeris_calculation'] else 'no'}",
    ]
    if report["recommendations"]:
        lines.extend(["", "Recommendations:"])
        lines.extend(f"  - {item}" for item in report["recommendations"])
    return "\n".join(lines)
