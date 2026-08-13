"""Assert that installed AGF operates without importing Semantic Projection Core."""

from __future__ import annotations

import argparse
import importlib.abc
import importlib.util
import sys


class _BlockSemanticProjection(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "semantic_projection" or fullname.startswith("semantic_projection."):
            raise ImportError(f"SPC import forbidden during AGF qualification: {fullname}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("base", "live"), required=True)
    args = parser.parse_args()

    if importlib.util.find_spec("semantic_projection") is not None and args.mode == "base":
        raise SystemExit("semantic_projection unexpectedly exists in the clean AGF base environment")
    sys.meta_path.insert(0, _BlockSemanticProjection())

    import astrology_graph_foundry
    from astrology_graph_foundry.doctor import build_doctor_report

    if astrology_graph_foundry.__version__ != "0.8.1":
        raise SystemExit(f"unexpected AGF version: {astrology_graph_foundry.__version__}")
    readiness_mode = "saved" if args.mode == "base" else "live"
    if not build_doctor_report()["startup_readiness"][readiness_mode]:
        raise SystemExit(f"AGF {args.mode} capability is not ready")
    print(f"AGF {args.mode} qualification passed with SPC imports forbidden")


if __name__ == "__main__":
    main()
