#!/usr/bin/env python3
"""Build standard compact Transit outputs for one date or a date range."""

from __future__ import annotations

import argparse

from _foundry_cli import (
    add_common_execution_arguments, choose, cli_command, configure_execution, existing_file, option,
    output_dir, print_outputs, required, run_commands, run_main,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("live", "cached"), default="live")
    parser.add_argument("--target", help="Natal, Composite, or Davison target package for live calculation.")
    parser.add_argument("--person-jsonl", help="Cached person JSONL when --provider cached.")
    dates = parser.add_mutually_exclusive_group()
    dates.add_argument("--date")
    dates.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--ephe-path", default=".")
    parser.add_argument("--timezone", default="America/Denver")
    parser.add_argument("--snapshot-time", default="12:00")
    parser.add_argument("--top-n-per-day", type=int, default=20)
    parser.add_argument("--min-arc-days", type=int, default=1)
    parser.add_argument("--streaming-profile", choices=("standard", "compact", "game"), default="standard")
    parser.add_argument("--target-set", choices=("core", "expanded", "all", "gameplay"))
    parser.add_argument("--compression", choices=("none", "gzip"), default="none")
    parser.add_argument("--out-dir")
    parser.add_argument("--stem", default="transit")
    parser.add_argument("--full", action="store_true", help="Also write the potentially large full Transit package.")
    add_common_execution_arguments(parser)
    args = parser.parse_args(argv)
    configure_execution(args)

    date = args.date
    start = args.start
    if not date and not start:
        mode = choose("Date mode", (("date", "Single date"), ("range", "Date range")))
        date = required("Date (YYYY-MM-DD)") if mode == "date" else None
        start = required("Start date (YYYY-MM-DD)") if mode == "range" else None
    if start and not args.end:
        args.end = required("End date (YYYY-MM-DD)")

    directory = output_dir(args.out_dir)
    analysis_path = directory / f"{args.stem}.analysis.json"
    stream_suffix = ".streaming_index.json.gz" if args.compression == "gzip" else ".streaming_index.json"
    streaming_path = directory / f"{args.stem}{stream_suffix}"
    full_path = directory / f"{args.stem}.full.json"
    command = cli_command("transit")
    option(command, "--provider", args.provider)
    if args.provider == "live":
        option(command, "--target-dataset", existing_file("Target package", args.target))
        option(command, "--ephe-path", args.ephe_path)
    else:
        option(command, "--person-jsonl", existing_file("Person JSONL", args.person_jsonl))
    option(command, "--date", date)
    option(command, "--start", start)
    option(command, "--end", args.end)
    option(command, "--timezone", args.timezone)
    option(command, "--snapshot-time", args.snapshot_time)
    option(command, "--top-n-per-day", args.top_n_per_day)
    option(command, "--min-arc-days", args.min_arc_days)
    option(command, "--streaming-profile", args.streaming_profile)
    option(command, "--transit-target-set", args.target_set)
    option(command, "--streaming-compression", args.compression)
    option(command, "--out-analysis", analysis_path)
    option(command, "--out-streaming-index", streaming_path)
    if args.full:
        option(command, "--out-full", full_path)
    run_commands([command], dry_run=args.dry_run)
    print_outputs([analysis_path, streaming_path, *([full_path] if args.full else [])], dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_main(main))
