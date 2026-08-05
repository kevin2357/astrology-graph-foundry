#!/usr/bin/env python3
"""Build standard Synastry outputs from two saved Natal packages or live inputs."""

from __future__ import annotations

import argparse

from _foundry_cli import (
    add_common_execution_arguments, append_live_birth_arguments, choose, cli_command, configure_execution,
    existing_file, option, output_dir, print_outputs, run_commands, run_main,
)


def _add_birth_args(parser: argparse.ArgumentParser, prefix: str) -> None:
    parser.add_argument(f"--{prefix}-name")
    parser.add_argument(f"--{prefix}-birth-local")
    parser.add_argument(f"--{prefix}-birth-timezone")
    parser.add_argument(f"--{prefix}-birth-lat", type=float)
    parser.add_argument(f"--{prefix}-birth-lon", type=float)
    parser.add_argument(f"--{prefix}-birth-location-label", default="")
    parser.add_argument(f"--{prefix}-source-chart-id")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("saved", "live"))
    parser.add_argument("--person-a-natal")
    parser.add_argument("--person-b-natal")
    _add_birth_args(parser, "person-a")
    _add_birth_args(parser, "person-b")
    parser.add_argument("--ephe-path", default=".")
    parser.add_argument("--house-system", default="P")
    parser.add_argument("--out-dir")
    parser.add_argument("--stem", default="synastry")
    parser.add_argument("--full", action="store_true", help="Also write the potentially large full Synastry package.")
    add_common_execution_arguments(parser)
    args = parser.parse_args(argv)
    configure_execution(args)

    mode = choose("Input mode", (("saved", "Two saved Natal packages"), ("live", "Two live birth records")), args.mode)
    directory = output_dir(args.out_dir)
    analysis_path = directory / f"{args.stem}.analysis.json"
    streaming_path = directory / f"{args.stem}.streaming_index.json"
    full_path = directory / f"{args.stem}.full.json"
    command = cli_command("synastry")
    if mode == "saved":
        option(command, "--person-a-provider", "cached")
        option(command, "--person-b-provider", "cached")
        option(command, "--person-a-natal-dataset", existing_file("Person A Natal package", args.person_a_natal))
        option(command, "--person-b-natal-dataset", existing_file("Person B Natal package", args.person_b_natal))
    else:
        option(command, "--person-a-provider", "live")
        option(command, "--person-b-provider", "live")
        append_live_birth_arguments(command, args, "person-a")
        append_live_birth_arguments(command, args, "person-b")
        option(command, "--ephe-path", args.ephe_path)
        option(command, "--house-system", args.house_system)
    option(command, "--out-analysis", analysis_path)
    option(command, "--out-streaming-index", streaming_path)
    if args.full:
        option(command, "--out-full", full_path)
    run_commands([command], dry_run=args.dry_run)
    print_outputs([analysis_path, streaming_path, *([full_path] if args.full else [])], dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_main(main))
