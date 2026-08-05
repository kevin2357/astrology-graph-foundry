#!/usr/bin/env python3
"""Build a standard Natal package from live birth data or cached JSONL."""

from __future__ import annotations

import argparse

from _foundry_cli import (
    add_common_execution_arguments, append_live_birth_arguments, choose, cli_command, configure_execution,
    existing_file, option, output_dir, print_outputs, run_commands, run_main,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("live", "cached"))
    parser.add_argument("--person-jsonl")
    parser.add_argument("--global-jsonl")
    parser.add_argument("--name")
    parser.add_argument("--birth-local")
    parser.add_argument("--birth-timezone")
    parser.add_argument("--birth-lat", type=float)
    parser.add_argument("--birth-lon", type=float)
    parser.add_argument("--birth-location-label", default="")
    parser.add_argument("--ephe-path", default=".")
    parser.add_argument("--house-system", default="P")
    parser.add_argument("--out-dir")
    parser.add_argument("--stem", default="natal", help="Output filename stem inside --out-dir.")
    parser.add_argument("--analysis", action="store_true", help="Also write the compact Natal analysis view.")
    add_common_execution_arguments(parser)
    args = parser.parse_args(argv)
    configure_execution(args)

    provider = choose("Provider", (("live", "Live Swiss Ephemeris"), ("cached", "Cached person JSONL")), args.provider)
    directory = output_dir(args.out_dir)
    full_path = directory / f"{args.stem}.full.json"
    analysis_path = directory / f"{args.stem}.analysis.json"
    command = cli_command("natal")
    option(command, "--provider", provider)
    if provider == "live":
        append_live_birth_arguments(command, args)
        option(command, "--ephe-path", args.ephe_path)
        option(command, "--house-system", args.house_system)
    else:
        option(command, "--person-jsonl", existing_file("Person JSONL", args.person_jsonl))
    if args.global_jsonl:
        option(command, "--global-jsonl", existing_file("Global JSONL", args.global_jsonl))
    option(command, "--out", full_path)
    if args.analysis:
        option(command, "--out-analysis", analysis_path)
    run_commands([command], dry_run=args.dry_run)
    print_outputs([full_path, *([analysis_path] if args.analysis else [])], dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_main(main))
