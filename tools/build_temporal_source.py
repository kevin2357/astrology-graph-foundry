#!/usr/bin/env python3
"""Export a Transit artifact as canonical temporal graph and SPC source bundle."""

from __future__ import annotations

import argparse

from _foundry_cli import (
    add_common_execution_arguments, cli_command, configure_execution, existing_file, flag, option,
    output_dir, print_outputs, run_commands, run_main,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Full or streaming Transit artifact.")
    parser.add_argument("--target", help="Authoritative full target package when the Transit artifact does not embed it.")
    parser.add_argument("--target-set", choices=("core", "expanded", "all", "gameplay"), default="all")
    parser.add_argument("--max-observation-gap-days", type=int, default=2)
    parser.add_argument("--sampled-exact-orb", type=float, default=0.01)
    parser.add_argument("--omit-observation-states", action="store_true")
    parser.add_argument("--out-dir")
    parser.add_argument("--stem", default="transit")
    add_common_execution_arguments(parser)
    args = parser.parse_args(argv)
    configure_execution(args)

    source = existing_file("Transit artifact", args.source)
    target = existing_file("Target package", args.target) if args.target else None
    directory = output_dir(args.out_dir)
    graph_path = directory / f"{args.stem}.canonical_temporal.json"
    bundle_path = directory / f"{args.stem}.temporal_projection_source.json"

    graph_command = cli_command("export-temporal-graph")
    option(graph_command, "--source-dataset", source)
    option(graph_command, "--out", graph_path)
    option(graph_command, "--max-observation-gap-days", args.max_observation_gap_days)
    option(graph_command, "--sampled-exact-orb", args.sampled_exact_orb)
    flag(graph_command, "--omit-observation-states", args.omit_observation_states)

    bundle_command = cli_command("export-temporal-projection-source")
    option(bundle_command, "--source-dataset", source)
    option(bundle_command, "--target-dataset", target)
    option(bundle_command, "--transit-target-set", args.target_set)
    option(bundle_command, "--out", bundle_path)
    option(bundle_command, "--max-observation-gap-days", args.max_observation_gap_days)
    option(bundle_command, "--sampled-exact-orb", args.sampled_exact_orb)
    flag(bundle_command, "--omit-observation-states", args.omit_observation_states)

    run_commands([graph_command, bundle_command], dry_run=args.dry_run)
    print_outputs([graph_path, bundle_path], dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_main(main))
