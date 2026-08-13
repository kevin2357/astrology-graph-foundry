"""Verify installed bounded-evidence schemas agree with the runtime vocabulary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from astrology_graph_foundry.ephemeris.uncertainty_evidence import SUPPORTED_AVAILABILITY_VALUES
from astrology_graph_foundry.resources import read_schema


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    args = parser.parse_args()

    evidence = read_schema("bounded_uncertainty_evidence_v1.schema.json")
    declared = set(evidence["properties"]["availability"]["enum"])
    if declared != SUPPORTED_AVAILABILITY_VALUES:
        raise SystemExit("installed availability vocabulary does not match runtime")
    package = read_schema("bounded_natal_dataset_v1.schema.json")
    if "evidence" not in package.get("$defs", {}):
        raise SystemExit("installed bounded package schema lacks composed evidence definition")
    manifest = json.loads(args.runtime_manifest.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "availability_count": len(declared),
                "package_schema_composes_evidence": True,
                "resource_count": manifest["resource_count"],
                "status": "passed",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
