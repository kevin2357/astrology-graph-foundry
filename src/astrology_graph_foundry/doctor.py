from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import platform
import sys
from importlib import metadata
from typing import Any

from astrology_graph_foundry import __version__ as PACKAGE_VERSION
from astrology_graph_foundry.calculation_provenance import (
    CALCULATION_PROFILE_VERSION,
    CALCULATION_PROVENANCE_CONTRACT_VERSION,
    NORMALIZATION_POLICY_VERSION,
)
from astrology_graph_foundry.resources import build_runtime_package_manifest

SUPPORTED_SPC_RELEASE_LINE = "0.10.x"
REQUIRED_MODES = ("saved", "projection", "live")


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
    foundry_distribution_version = _distribution_version("astrology-graph-foundry")
    foundry_version_matches = bool(
        foundry_distribution_version and foundry_distribution_version == PACKAGE_VERSION
    )
    projection_compatible = bool(
        projection_distribution_version
        and projection_distribution_version.split(".")[:2] == ["0", "10"]
    )
    runtime_manifest = build_runtime_package_manifest()
    resources_ready = bool(runtime_manifest["resources"])
    runtime_manifest_sha256 = hashlib.sha256(
        json.dumps(runtime_manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    saved_ready = bool(package_status["available"] and foundry_version_matches and resources_ready)
    projection_ready = bool(
        saved_ready
        and projection_status["available"]
        and not projection_version_mismatch
        and projection_compatible
    )
    live_ready = bool(saved_ready and swiss_status["available"])
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
            "installed_distribution_version": foundry_distribution_version,
            "version_metadata_matches_runtime": foundry_version_matches,
        },
        "semantic_projection_core": {
            **projection_status,
            "distribution_version": projection_distribution_version,
            "engine_version": projection_engine_version,
            "version_metadata_matches_engine": not projection_version_mismatch,
            "supported_release_line": SUPPORTED_SPC_RELEASE_LINE,
            "compatible_with_foundry": projection_compatible,
            "required_for_projection": True,
        },
        "swiss_ephemeris": {
            **swiss_status,
            "distribution_version": _distribution_version("pyswisseph"),
            "required_for_live_calculation": True,
            "cached_package_workflows_available_without_it": True,
        },
        "capabilities": {
            "read_and_transform_saved_packages": saved_ready,
            "project_saved_packages": projection_ready,
            "live_ephemeris_calculation": live_ready,
        },
        "startup_readiness": {
            "saved": saved_ready,
            "projection": projection_ready,
            "live": live_ready,
            "live_scope": "dependency availability only; provider and ephemeris-data qualification is invocation/release evidence",
        },
        "runtime_resources": {
            "manifest_type": runtime_manifest["manifest_type"],
            "resource_count": runtime_manifest["resource_count"],
            "manifest_sha256": runtime_manifest_sha256,
        },
        "calculation_contracts": {
            "provenance": CALCULATION_PROVENANCE_CONTRACT_VERSION,
            "profile": CALCULATION_PROFILE_VERSION,
            "normalization": NORMALIZATION_POLICY_VERSION,
        },
        "recommendations": [
            *([] if projection_status["available"] else [
                "Install Semantic Projection Core for projection workflows."
            ]),
            *([] if foundry_version_matches else [
                "Foundry distribution metadata does not match its imported runtime version. Reinstall the exact Foundry artifact."
            ]),
            *([] if projection_compatible or not projection_status["available"] else [
                f"Install a Semantic Projection Core release in the supported {SUPPORTED_SPC_RELEASE_LINE} line."
            ]),
            *([] if not projection_version_mismatch else [
                (
                    "Semantic Projection Core distribution metadata does not match its imported engine version. "
                    "Reinstall the editable Semantic Projection Core package to refresh installation metadata."
                )
            ]),
            *([] if swiss_status["available"] else [
                (
                    "Install the Foundry live extra in an environment with a compatible pyswisseph wheel: "
                    "python -m pip install -e .[live]. Graph-only and saved-package workflows remain available."
                )
            ]),
        ],
    }


def required_mode_failures(report: dict[str, Any], mode: str) -> list[str]:
    """Return stable startup failure codes for a required runtime mode."""

    if mode not in REQUIRED_MODES:
        raise ValueError(f"Unknown required mode: {mode}")
    failures: list[str] = []
    if not report["foundry"]["version_metadata_matches_runtime"]:
        failures.append("foundry_version_mismatch")
    if not report["runtime_resources"]["resource_count"]:
        failures.append("packaged_resources_missing")
    if mode == "projection":
        spc = report["semantic_projection_core"]
        if not spc["available"]:
            failures.append("spc_missing")
        elif not spc["version_metadata_matches_engine"]:
            failures.append("spc_version_mismatch")
        elif not spc["compatible_with_foundry"]:
            failures.append("spc_incompatible")
    if mode == "live" and not report["swiss_ephemeris"]["available"]:
        failures.append("pyswisseph_missing")
    return failures


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
        "",
        "Startup readiness:",
        f"  Saved: {'ready' if report['startup_readiness']['saved'] else 'not ready'}",
        f"  Projection: {'ready' if report['startup_readiness']['projection'] else 'not ready'}",
        f"  Live dependency availability: {'ready' if report['startup_readiness']['live'] else 'not ready'}",
    ]
    if report["recommendations"]:
        lines.extend(["", "Recommendations:"])
        lines.extend(f"  - {item}" for item in report["recommendations"])
    return "\n".join(lines)
