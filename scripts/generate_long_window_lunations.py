from __future__ import annotations

import argparse
from pathlib import Path

from astrology_graph_foundry.common.io import write_json
from astrology_graph_foundry.pipelines import eclipse_lunation


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an eclipse/lunation package over the same explicit window used by a long Transit package."
    )
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--target-dataset")
    parser.add_argument("--ephe-path", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    package = eclipse_lunation.build(
        start=args.start,
        end=args.end,
        target_dataset=args.target_dataset,
        ephe_path=args.ephe_path,
    )
    out = Path(args.out)
    write_json(out, package)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
