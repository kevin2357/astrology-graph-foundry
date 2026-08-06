"""Qualify the installed Linux/Moshier AGF release candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import semantic_projection
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

import astrology_graph_foundry
from astrology_graph_foundry.common.io import write_json
from astrology_graph_foundry.ephemeris.providers import _ephemeris_data_inventory
from astrology_graph_foundry.pipelines.natal import build
from astrology_graph_foundry.projection_adapter import project_dataset
from astrology_graph_foundry.resources import read_schema, schema_names

EXPECTED_PYSWISSEPH_VERSION = "2.10.3.2"
EXPECTED_PYSWISSEPH_WHEEL_SHA256 = "e00d7e08aeafe00938603bc118874b6ca7871c5aaa55aafca8fa2c6d76aff812"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def natal_validator() -> Draft202012Validator:
    registry = Registry()
    for name in schema_names():
        registry = registry.with_resource(name, Resource.from_contents(read_schema(name)))
    return Draft202012Validator(read_schema("natal_dataset_v1.schema.json"), registry=registry)


def semantic_payload(package: dict) -> dict:
    payload = deepcopy(package)
    payload.get("metadata", {}).pop("created_at", None)
    return payload


def assert_live_package(package: dict, source_chart_id: str, validator: Draft202012Validator) -> None:
    validator.validate(package)
    provenance = package["metadata"]["calculation_provenance"]
    runtime = provenance["calculation_profile"]["provider"]
    assert package["canonical_astrology_graph"]["source_chart_id"] == source_chart_id
    assert runtime["calculation_flags"]["requested_ephemeris_mode"] == "moshier"
    assert runtime["calculation_flags"]["observed_ephemeris_modes"] == ["moshier"]
    assert runtime["calculation_flags"]["returned_flags_recorded"] is True
    assert runtime["ephemeris_data"]["resource_count"] == 0
    assert package["natal"]["calculation_options"]["include_optional_points"] is False
    assert "nChiron" not in package["natal"]["bodies"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--agf-wheel", type=Path, required=True)
    parser.add_argument("--spc-wheel", type=Path, required=True)
    parser.add_argument("--pyswisseph-wheel", type=Path, required=True)
    parser.add_argument("--require-installed", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.require_installed and "site-packages" not in str(Path(astrology_graph_foundry.__file__)).lower():
        raise SystemExit("AGF import is not from an installed environment")
    if platform.system() != "Linux" or platform.machine().lower() not in {"x86_64", "amd64"}:
        raise SystemExit("Live release qualification requires Linux x86-64")
    if sys.version_info[:2] != (3, 11):
        raise SystemExit("Live release qualification requires CPython 3.11")
    pyswisseph_hash = sha256_file(args.pyswisseph_wheel)
    if pyswisseph_hash != EXPECTED_PYSWISSEPH_WHEEL_SHA256:
        raise SystemExit(f"Unexpected pyswisseph wheel SHA-256: {pyswisseph_hash}")
    if importlib.metadata.version("pyswisseph") != EXPECTED_PYSWISSEPH_VERSION:
        raise SystemExit("Installed pyswisseph version does not match the qualified artifact")

    fixtures = [
        ("baseline", "2020-05-17T14:30:00", "America/Denver", 39.7392, -104.9903),
        ("standard-time", "2020-01-15T08:30:00", "America/Denver", 39.7392, -104.9903),
        ("daylight-time", "2020-07-15T08:30:00", "America/Denver", 39.7392, -104.9903),
        ("coordinate-edge", "2020-05-17T14:30:00", "UTC", 66.0, 179.9),
    ]
    validator = natal_validator()
    fixture_summaries = []
    with TemporaryDirectory(prefix="agf-live-empty-ephe-") as empty_ephe:
        inventory = _ephemeris_data_inventory(empty_ephe)
        assert inventory["resource_count"] == 0
        packages = {}
        for label, local_time, timezone, latitude, longitude in fixtures:
            source_chart_id = f"agf:qualification:{label}"
            package = build(
                provider="live",
                name=f"Qualification {label}",
                birth_local=local_time,
                birth_timezone=timezone,
                birth_lat=latitude,
                birth_lon=longitude,
                source_chart_id=source_chart_id,
                ephe_path=empty_ephe,
                ephemeris_mode="moshier",
                include_optional_points=False,
            )
            assert_live_package(package, source_chart_id, validator)
            packages[label] = package
            fixture_summaries.append(
                {
                    "label": label,
                    "source_chart_id": source_chart_id,
                    "canonical_graph_sha256": sha256_json(package["canonical_astrology_graph"]),
                    "semantic_package_sha256": sha256_json(semantic_payload(package)),
                    "configuration_sha256": package["metadata"]["calculation_provenance"]["configuration_sha256"],
                    "source_input_sha256": package["metadata"]["calculation_provenance"]["source_input"]["sha256"],
                }
            )
        repeated = build(
            provider="live",
            name="Qualification baseline",
            birth_local="2020-05-17T14:30:00",
            birth_timezone="America/Denver",
            birth_lat=39.7392,
            birth_lon=-104.9903,
            source_chart_id="agf:qualification:baseline",
            ephe_path=empty_ephe,
            ephemeris_mode="moshier",
            include_optional_points=False,
        )
        assert semantic_payload(repeated) == semantic_payload(packages["baseline"])
        projected = project_dataset(
            packages["baseline"],
            profile_id="orthodox_astrology.v1",
            profile_version="1.0.0",
        )
        assert projected["source_identity"]["source_chart_id"] == "agf:qualification:baseline"

    result = {
        "evidence_type": "agf.controlled_live_summary.v1",
        "runtime": {
            "python": platform.python_version(),
            "system": platform.system(),
            "machine": platform.machine(),
            "agf_version": importlib.metadata.version("astrology-graph-foundry"),
            "spc_distribution_version": importlib.metadata.version("semantic-projection-core"),
            "spc_engine_version": semantic_projection.ENGINE_VERSION,
            "pyswisseph_version": importlib.metadata.version("pyswisseph"),
        },
        "artifacts": {
            "agf_wheel_sha256": sha256_file(args.agf_wheel),
            "spc_wheel_sha256": sha256_file(args.spc_wheel),
            "pyswisseph_wheel_sha256": pyswisseph_hash,
        },
        "provider": {
            "requested_mode": "moshier",
            "observed_modes": ["moshier"],
            "external_ephemeris_files": 0,
            "optional_points": False,
        },
        "fixtures": fixture_summaries,
        "repeat_semantic_equal": True,
        "projection": {
            "passed": True,
            "source_chart_id": projected["source_identity"]["source_chart_id"],
            "object_count": len(projected["objects"]),
            "relationship_count": len(projected["relationships"]),
        },
    }
    write_json(args.out, result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
