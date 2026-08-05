from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from semantic_projection.engine import ProjectionExecutionError
from semantic_projection.registry import ProjectionProfileRegistryError
from semantic_projection.validation import ProjectionValidationError

from astrology_graph_foundry import __version__
from astrology_graph_foundry.common.io import read_json, write_json
from astrology_graph_foundry.common.logging_config import configure_logging
from astrology_graph_foundry.common.temporal_activation import (
    TemporalExportOptions,
    TemporalSourceContractError,
    extract_canonical_temporal_activation_graph,
)
from astrology_graph_foundry.doctor import build_doctor_report, render_doctor_report
from astrology_graph_foundry.ephemeris.generate_daily_ephemeris import build_ephemeris_objects
from astrology_graph_foundry.ephemeris.models import BirthData
from astrology_graph_foundry.pipelines import (
    annual_profections,
    composite,
    davison,
    eclipse_lunation,
    lunar_return,
    natal,
    progressed,
    solar_arc,
    solar_return,
    synastry,
    timeline,
    transit,
)
from astrology_graph_foundry.projection_adapter import (
    enforce_unmapped_threshold,
    project_dataset,
    projection_materialization_view,
)
from astrology_graph_foundry.resources import build_runtime_package_manifest
from astrology_graph_foundry.temporal_projection_adapter import build_temporal_projection_source_bundle

logger = logging.getLogger(__name__)

DEFAULT_PACKAGE_ROOT = Path(r"C:\dev\astro-packages")


def safe_name(value: str | None) -> str:
    raw = (value or "unknown").strip() or "unknown"
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in raw)


def infer_person_name(args, data=None) -> str:
    if getattr(args, "name", None):
        return args.name
    if data:
        return data.get("metadata", {}).get("target_label") or data.get("metadata", {}).get("person") or data.get("person", {}).get("person") or "unknown"
    return "unknown"


def resolve_output_path(args, default_filename: str, data=None) -> Path:
    if getattr(args, "out", None):
        return Path(args.out)
    out_dir = getattr(args, "output_dir", None)
    if out_dir:
        base = Path(out_dir)
    else:
        base = DEFAULT_PACKAGE_ROOT / safe_name(infer_person_name(args, data))
    base.mkdir(parents=True, exist_ok=True)
    return base / default_filename


def add_provider_args(p: argparse.ArgumentParser, *, include_natal_dataset: bool = True) -> None:
    p.add_argument("--provider", choices=["cached", "live"], default="cached")
    p.add_argument("--person-jsonl")
    if include_natal_dataset:
        p.add_argument("--natal-dataset")
    p.add_argument("--global-jsonl")
    p.add_argument("--name")
    p.add_argument("--birth-local")
    p.add_argument("--birth-timezone")
    p.add_argument("--birth-lat", type=float)
    p.add_argument("--birth-lon", type=float)
    p.add_argument("--birth-location-label", default="")
    p.add_argument("--source-chart-id")
    p.add_argument("--snapshot-time", default="12:00")
    p.add_argument("--timezone", default="America/Denver")
    p.add_argument("--ephe-path", default=".")
    p.add_argument("--house-system", default="P")
    p.add_argument("--output-dir")


def add_pair_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--person-a-provider", choices=["cached", "live"], default="live")
    p.add_argument("--person-a-jsonl")
    p.add_argument("--person-a-natal-dataset")
    p.add_argument("--person-a-name")
    p.add_argument("--person-a-birth-local")
    p.add_argument("--person-a-birth-timezone")
    p.add_argument("--person-a-birth-lat", type=float)
    p.add_argument("--person-a-birth-lon", type=float)
    p.add_argument("--person-a-birth-location-label", default="")
    p.add_argument("--person-a-source-chart-id")
    p.add_argument("--person-b-provider", choices=["cached", "live"], default="live")
    p.add_argument("--person-b-jsonl")
    p.add_argument("--person-b-natal-dataset")
    p.add_argument("--person-b-name")
    p.add_argument("--person-b-birth-local")
    p.add_argument("--person-b-birth-timezone")
    p.add_argument("--person-b-birth-lat", type=float)
    p.add_argument("--person-b-birth-lon", type=float)
    p.add_argument("--person-b-birth-location-label", default="")
    p.add_argument("--person-b-source-chart-id")
    p.add_argument("--snapshot-time", default="12:00")
    p.add_argument("--timezone", default="America/Denver")
    p.add_argument("--ephe-path", default=".")
    p.add_argument("--house-system", default="P")
    p.add_argument("--output-dir")
    p.add_argument("--out")


def main() -> None:
    configure_logging()
    logger.info("astro-package CLI starting")
    parser = argparse.ArgumentParser(prog="astro-package")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser(
        "doctor",
        help="Inspect installation health and report graph/projection/live-calculation capabilities.",
    )
    p.add_argument("--json", action="store_true", help="Emit the doctor report as JSON.")

    p = sub.add_parser(
        "runtime-manifest",
        help="Report installed schema resources, contract declarations, and SHA-256 identities.",
    )
    p.add_argument("--out", help="Write the JSON manifest to this path instead of stdout.")

    p = sub.add_parser("generate-ephemeris")
    add_provider_args(p)
    p.add_argument("--start")
    p.add_argument("--end")
    p.add_argument("--top-n-candidates", type=int, default=25)
    p.add_argument("--persist-jsonl")
    p.add_argument("--out-json")

    p = sub.add_parser("natal")
    add_provider_args(p)
    p.add_argument("--start")
    p.add_argument("--end")
    p.add_argument("--out")
    p.add_argument("--out-analysis", help="Optionally write compact natal analysis view in addition to the full natal package.")

    p = sub.add_parser("transit")
    add_provider_args(p, include_natal_dataset=False)
    p.add_argument("--target-dataset", help="Natal, composite, or Davison package exposing the TransitableChart interface.")
    one = p.add_mutually_exclusive_group(required=True)
    one.add_argument("--date", help="Single-day transit snapshot. Equivalent to --start DATE --end DATE.")
    one.add_argument("--start", help="Start date for a multi-day transit range.")
    p.add_argument("--end", help="End date for a multi-day transit range. Required when --start is used.")
    p.add_argument("--top-n-per-day", type=int, default=20)
    p.add_argument("--min-arc-days", type=int, default=1)
    p.add_argument("--out", help="Default compact output stem/path. Writes .analysis.json and .streaming_index.json unless explicit view paths are provided.")
    p.add_argument("--out-analysis")
    p.add_argument("--out-streaming-index")
    p.add_argument(
        "--streaming-profile",
        choices=["standard", "compact", "game"],
        default="standard",
        help="Retention/materialization profile for the Transit streaming index.",
    )
    p.add_argument(
        "--transit-target-set",
        choices=["core", "expanded", "all", "gameplay"],
        help="Target selection policy for compact/game streaming views. Defaults to gameplay for game and all otherwise.",
    )
    p.add_argument(
        "--streaming-compression",
        choices=["none", "gzip"],
        default="none",
        help="Optionally write the streaming artifact as deterministic gzip-compressed JSON.",
    )
    p.add_argument("--out-full", help="Explicitly write the full-detail transit package. Full output is opt-in because it can be very large.")

    p = sub.add_parser(
        "transit-streaming-view",
        help="Materialize standard, compact, or game streaming views from an existing full Transit package.",
    )
    p.add_argument("--source-dataset", required=True)
    p.add_argument(
        "--full-transit-dataset",
        help=(
            "Optional full Transit package used to restore daily sky positions when "
            "materializing from a legacy standard streaming index that did not embed them."
        ),
    )
    p.add_argument("--streaming-profile", choices=["standard", "compact", "game"], default="standard")
    p.add_argument("--transit-target-set", choices=["core", "expanded", "all", "gameplay"])
    p.add_argument("--compression", choices=["none", "gzip"], default="none")
    p.add_argument("--out", required=True)

    p = sub.add_parser("synastry")
    add_pair_args(p)
    p.add_argument("--out-analysis")
    p.add_argument("--out-streaming-index")
    p.add_argument("--out-full", help="Explicitly write the full-detail synastry relationship package. Full output is opt-in because it can be large.")

    p = sub.add_parser("composite")
    add_pair_args(p)

    p = sub.add_parser("annual-profections")
    p.add_argument("--target-dataset", required=True, help="Natal, composite, or Davison package exposing TransitableChart.")
    p.add_argument("--target-date", required=True)
    p.add_argument("--reference-date", help="Optional override for the TransitableChart reference date.")
    p.add_argument("--output-dir")
    p.add_argument("--out")

    p = sub.add_parser("solar-return")
    p.add_argument("--target-dataset", required=True, help="Natal, composite, or Davison package exposing TransitableChart.")
    p.add_argument("--return-year", type=int, required=True)
    p.add_argument(
        "--return-location-policy",
        required=True,
        choices=["target_reference", "explicit"],
        help=(
            "Required. Choose target_reference for simple testing or when the "
            "TransitableChart reference event is the intended return location; "
            "choose explicit and provide all --location-* fields for a lived/event location."
        ),
    )
    p.add_argument("--location-timezone")
    p.add_argument("--location-lat", type=float)
    p.add_argument("--location-lon", type=float)
    p.add_argument("--location-label")
    p.add_argument("--ephe-path", default=".")
    p.add_argument("--house-system", default="P")
    p.add_argument("--output-dir")
    p.add_argument("--out")
    p.add_argument("--out-analysis", help="Optionally write compact Solar Return analysis view.")

    p = sub.add_parser(
        "solar-return-analysis",
        help="Materialize a compact factual analysis view from an existing full Solar Return package.",
    )
    p.add_argument("--source-dataset", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("lunar-return")
    p.add_argument("--target-dataset", required=True, help="Natal, composite, or Davison package exposing TransitableChart.")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument(
        "--return-location-policy",
        required=True,
        choices=["target_reference", "explicit"],
        help=(
            "Required. Choose target_reference for simple testing or when the "
            "TransitableChart reference event is the intended return location; "
            "choose explicit and provide all --location-* fields for a lived/event location."
        ),
    )
    p.add_argument("--location-timezone")
    p.add_argument("--location-lat", type=float)
    p.add_argument("--location-lon", type=float)
    p.add_argument("--location-label")
    p.add_argument("--ephe-path", default=".")
    p.add_argument("--house-system", default="P")
    p.add_argument("--output-dir")
    p.add_argument("--out")

    p = sub.add_parser("davison")
    p.add_argument("--person-a-natal-dataset", required=True)
    p.add_argument("--person-b-natal-dataset", required=True)
    p.add_argument("--ephe-path", default=".")
    p.add_argument("--house-system", default="P")
    p.add_argument("--output-dir")
    p.add_argument("--out")

    p = sub.add_parser("eclipse-lunation")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--target-dataset", help="Optional natal, composite, or Davison package exposing TransitableChart.")
    p.add_argument("--ephe-path", default=".")
    p.add_argument("--output-dir")
    p.add_argument("--out")


    p = sub.add_parser(
        "export-temporal-graph",
        help=(
            "Export a full or streaming Transit package as the projection-neutral "
            "canonical_temporal_activation_graph.v1 contract."
        ),
    )
    p.add_argument("--source-dataset", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--max-observation-gap-days", type=int, default=2)
    p.add_argument("--sampled-exact-orb", type=float, default=0.01)
    p.add_argument(
        "--omit-observation-states",
        action="store_true",
        help="Emit arc summaries without embedded dated observation states.",
    )

    p = sub.add_parser(
        "export-temporal-projection-source",
        help=(
            "Build the Foundry-owned projection-neutral timing handoff consumed "
            "by Semantic Projection Core's production temporal route."
        ),
    )
    p.add_argument("--source-dataset", required=True)
    p.add_argument(
        "--target-dataset",
        help=(
            "Full natal, composite, or Davison package supplying the authoritative "
            "canonical target graph when the Transit artifact is a compact/streaming view."
        ),
    )
    p.add_argument(
        "--transit-target-set",
        choices=["core", "expanded", "all", "gameplay"],
        default="all",
        help="Explicit source-selection policy for temporal activations.",
    )
    p.add_argument("--out", required=True)
    p.add_argument("--max-observation-gap-days", type=int, default=2)
    p.add_argument("--sampled-exact-orb", type=float, default=0.01)
    p.add_argument("--omit-observation-states", action="store_true")

    p = sub.add_parser(
        "project",
        help="Project an existing full Foundry dataset without recalculating astrology.",
    )
    p.add_argument("--source-dataset", required=True)
    p.add_argument(
        "--projection-profile",
        default="orthodox_astrology.v1",
    )
    p.add_argument("--projection-profile-version", default="1.0.0")
    p.add_argument("--projection-context", help="JSON file containing ProjectionContext.")
    p.add_argument("--context-id")
    p.add_argument("--context-version", default="1.0.0")
    p.add_argument("--subject-scope")
    p.add_argument("--relationship-type")
    p.add_argument("--application-context")
    p.add_argument("--audience")
    p.add_argument("--target-domain")
    p.add_argument("--output-intent", default="structured_semantic_model")
    p.add_argument(
        "--unmapped-policy",
        choices=["diagnostic", "passthrough", "ignore", "fail"],
        default="diagnostic",
    )
    p.add_argument("--no-audit", action="store_true")
    p.add_argument("--no-diagnostics", action="store_true")
    p.add_argument(
        "--fail-on-unmapped-threshold",
        type=float,
        help="Fail when unmapped source fraction exceeds this 0..1 value.",
    )
    p.add_argument(
        "--unmapped-threshold-scope",
        choices=["eligible", "canonical"],
        default="eligible",
        help="Threshold denominator: profile-eligible rows or all canonical rows.",
    )
    p.add_argument(
        "--output-mode",
        choices=["full", "standard", "summary", "forensic"],
        default="full",
    )
    p.add_argument("--out", required=True)

    p = sub.add_parser("progressed")
    p.add_argument("--output-dir")
    p.add_argument("--out")

    p = sub.add_parser("solar-arc")
    p.add_argument("--output-dir")
    p.add_argument("--out")

    p = sub.add_parser("timeline")
    p.add_argument("--person-a-provider", choices=["cached", "live"], default="cached")
    p.add_argument("--person-a-jsonl")
    p.add_argument("--person-a-natal-dataset")
    p.add_argument("--person-b-provider", choices=["cached", "live"])
    p.add_argument("--person-b-jsonl")
    p.add_argument("--person-b-natal-dataset")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--snapshot-time", default="12:00")
    p.add_argument("--timezone", default="America/Denver")
    p.add_argument("--ephe-path", default=".")
    p.add_argument("--output-dir")
    p.add_argument("--out")

    args = parser.parse_args()
    logger.info("CLI command parsed: %s", args.cmd)
    logger.debug("CLI args: %s", vars(args))

    if args.cmd == "doctor":
        report = build_doctor_report()
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(render_doctor_report(report))
        return

    if args.cmd == "runtime-manifest":
        manifest = build_runtime_package_manifest()
        if args.out:
            write_json(args.out, manifest)
            print(f"Wrote {args.out}")
        else:
            print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    if args.cmd == "solar-return-analysis":
        package = read_json(args.source_dataset)
        if package.get("metadata", {}).get("analysis_type") != "solar_return_dataset":
            raise SystemExit("solar-return-analysis requires a full solar_return_dataset package.")
        write_json(args.out, solar_return.analysis_view(package))
        print(f"Wrote {args.out}")
        return

    if args.cmd == "export-temporal-graph":
        logger.info(
            "Exporting canonical temporal graph source=%s out=%s",
            args.source_dataset,
            args.out,
        )
        source_package = read_json(args.source_dataset)
        try:
            temporal_graph = extract_canonical_temporal_activation_graph(
                source_package,
                options=TemporalExportOptions(
                    max_observation_gap_days=args.max_observation_gap_days,
                    sampled_exact_orb=args.sampled_exact_orb,
                    include_observation_states=not args.omit_observation_states,
                ),
            )
        except TemporalSourceContractError as exc:
            raise SystemExit(f"Temporal graph export failed: {exc}") from exc
        write_json(args.out, temporal_graph)
        logger.info("Command complete: wrote %s", args.out)
        print(f"Wrote {args.out}")
        return

    if args.cmd == "export-temporal-projection-source":
        logger.info(
            "Exporting temporal projection source bundle source=%s out=%s",
            args.source_dataset,
            args.out,
        )
        source_package = read_json(args.source_dataset)
        target_package = read_json(args.target_dataset) if args.target_dataset else None
        try:
            bundle = build_temporal_projection_source_bundle(
                source_package,
                target_package=target_package,
                target_set=args.transit_target_set,
                options=TemporalExportOptions(
                    max_observation_gap_days=args.max_observation_gap_days,
                    sampled_exact_orb=args.sampled_exact_orb,
                    include_observation_states=not args.omit_observation_states,
                ),
            )
        except (TemporalSourceContractError, ValueError) as exc:
            raise SystemExit(f"Temporal projection source export failed: {exc}") from exc
        write_json(args.out, bundle)
        logger.info("Command complete: wrote %s", args.out)
        print(f"Wrote {args.out}")
        return

    if args.cmd == "project":
        logger.info(
            "Projecting saved dataset source=%s profile=%s version=%s",
            args.source_dataset,
            args.projection_profile,
            args.projection_profile_version,
        )
        source_package = read_json(args.source_dataset)
        context = read_json(args.projection_context) if args.projection_context else None
        if context is None and any(
            value is not None
            for value in (
                args.context_id,
                args.subject_scope,
                args.relationship_type,
                args.application_context,
                args.audience,
                args.target_domain,
            )
        ):
            context = {
                "context_id": args.context_id or "orthodox.general.v1",
                "context_version": args.context_version,
                "subject_scope": args.subject_scope or "individual",
                "relationship_type": args.relationship_type,
                "age_band": None,
                "target_domain": (
                    args.target_domain or args.projection_profile
                ),
                "application_context": (
                    args.application_context or "general_interpretation"
                ),
                "audience": args.audience,
                "output_intent": args.output_intent,
                "constraints": {},
                "parameters": {},
                "extensions": {},
            }
        options = {
            "retain_unmapped_sources": True,
            "include_audit": not args.no_audit,
            "include_diagnostics": not args.no_diagnostics,
            "unmapped_policy": args.unmapped_policy,
            "compact_audit": False,
            "extensions": {},
        }
        try:
            projected = project_dataset(
                source_package,
                profile_id=args.projection_profile,
                profile_version=args.projection_profile_version,
                context=context,
                options=options,
            )
            enforce_unmapped_threshold(
                projected,
                args.fail_on_unmapped_threshold,
                scope=args.unmapped_threshold_scope,
            )
        except (
            ValueError,
            LookupError,
            ProjectionExecutionError,
            ProjectionProfileRegistryError,
            ProjectionValidationError,
        ) as exc:
            raise SystemExit(f"Projection failed: {exc}") from exc

        output = projection_materialization_view(
            projected, args.output_mode
        )
        write_json(args.out, output)
        logger.info("Command complete: wrote %s", args.out)
        print(f"Wrote {args.out}")
        return

    if args.cmd == "generate-ephemeris":
        birth_data = None
        if args.natal_dataset is None:
            birth_data = BirthData(
                name=args.name,
                birth_local=args.birth_local,
                birth_timezone=args.birth_timezone,
                birth_lat=args.birth_lat,
                birth_lon=args.birth_lon,
                birth_location_label=args.birth_location_label,
                source_chart_id=args.source_chart_id,
            )
        logger.info("Generating ephemeris objects provider=%s natal_dataset=%s start=%s end=%s", args.provider, args.natal_dataset, args.start, args.end)
        ep = build_ephemeris_objects(
            natal_dataset=args.natal_dataset,
            birth_data=birth_data,
            start=args.start,
            end=args.end,
            snapshot_timezone=args.timezone,
            snapshot_time=args.snapshot_time,
            ephe_path=args.ephe_path,
            house_system=args.house_system,
            top_n_candidates=args.top_n_candidates,
        )
        if args.persist_jsonl:
            ep.persist_jsonl(args.persist_jsonl)
        if args.out_json:
            write_json(args.out_json, {
                "person_metadata": ep.person_metadata(),
                "natal_chart": ep.natal_chart(),
                "daily": [d.__dict__ for d in ep.iter_days()],
            })
        if not args.persist_jsonl and not args.out_json:
            print("Provider computed in-memory; no output requested.")
        return

    if args.cmd == "natal":
        logger.info("Building natal package provider=%s out=%s", args.provider, args.out)
        data = natal.build(
            provider=args.provider,
            person_jsonl=args.person_jsonl,
            natal_dataset=args.natal_dataset,
            global_jsonl=args.global_jsonl,
            name=args.name,
            birth_local=args.birth_local,
            birth_timezone=args.birth_timezone,
            birth_lat=args.birth_lat,
            birth_lon=args.birth_lon,
            birth_location_label=args.birth_location_label,
            source_chart_id=args.source_chart_id,
            start=args.start,
            end=args.end,
            snapshot_timezone=args.timezone,
            snapshot_time=args.snapshot_time,
            ephe_path=args.ephe_path,
            house_system=args.house_system,
        )
        out = resolve_output_path(args, f"{safe_name(data['metadata'].get('person'))}_natal_dataset.json", data)
        if args.out_analysis:
            logger.info("Writing optional natal analysis view to %s", args.out_analysis)
            write_json(args.out_analysis, natal.analysis_view(data))
            print(f"Wrote {args.out_analysis}")
    elif args.cmd == "transit":
        if args.provider == "live" and not args.target_dataset:
            raise SystemExit("transit --provider live requires --target-dataset with a natal, composite, or Davison package.")
        if args.provider == "cached" and not args.person_jsonl:
            raise SystemExit("transit --provider cached requires --person-jsonl.")
        if args.start and not args.end:
            raise SystemExit("transit --start requires --end. For a single day, use --date YYYY-MM-DD.")
        start_date = args.date or args.start
        end_date = args.date or args.end
        logger.info("Building unified transit package provider=%s start=%s end=%s top_n=%s out=%s", args.provider, start_date, end_date, args.top_n_per_day, args.out)
        data = transit.build(
            date=args.date,
            start=args.start,
            end=args.end,
            provider=args.provider,
            person_jsonl=args.person_jsonl,
            target_dataset=args.target_dataset,
            global_jsonl=args.global_jsonl,
            snapshot_timezone=args.timezone,
            snapshot_time=args.snapshot_time,
            ephe_path=args.ephe_path,
            top_n_per_day=args.top_n_per_day,
            min_arc_days=args.min_arc_days,
        )

        def derived_transit_view_paths() -> tuple[Path, Path]:
            suffix = f"{start_date}" if start_date == end_date else f"{start_date}_to_{end_date}"
            base = resolve_output_path(args, f"{safe_name(data['metadata'].get('target_label'))}_{suffix}_transit.json", data)
            if base.suffix:
                return base.with_name(f"{base.stem}.analysis.json"), base.with_name(f"{base.stem}.streaming_index.json")
            base.mkdir(parents=True, exist_ok=True)
            stem = f"{safe_name(data['metadata'].get('target_label'))}_{suffix}_transit"
            return base / f"{stem}.analysis.json", base / f"{stem}.streaming_index.json"

        def streaming_output_path(path: Path) -> Path:
            if args.streaming_compression == "gzip" and path.suffix != ".gz":
                return path.with_name(path.name + ".gz")
            return path

        def streaming_payload() -> dict:
            return transit.streaming_index(
                data,
                profile=args.streaming_profile,
                target_set=args.transit_target_set,
            )

        wrote: list[Path] = []
        explicit_view_paths = bool(args.out_analysis or args.out_streaming_index or args.out_full)
        if explicit_view_paths:
            if args.out_analysis:
                path = Path(args.out_analysis); write_json(path, transit.analysis_view(data)); wrote.append(path)
            if args.out_streaming_index:
                path = streaming_output_path(Path(args.out_streaming_index))
                write_json(path, streaming_payload())
                wrote.append(path)
            if args.out_full:
                path = Path(args.out_full); write_json(path, data); wrote.append(path)
        else:
            analysis_path, streaming_path = derived_transit_view_paths()
            write_json(analysis_path, transit.analysis_view(data))
            streaming_path = streaming_output_path(streaming_path)
            write_json(streaming_path, streaming_payload())
            wrote.extend([analysis_path, streaming_path])
        for path in wrote:
            print(f"Wrote {path}")
        logger.info("Command complete: wrote %d transit output files", len(wrote))
        return
    elif args.cmd == "transit-streaming-view":
        source = read_json(args.source_dataset)
        output_path = Path(args.out)
        if args.compression == "gzip" and output_path.suffix != ".gz":
            output_path = output_path.with_name(output_path.name + ".gz")
        full_source = read_json(args.full_transit_dataset) if args.full_transit_dataset else None
        view = transit.streaming_index(
            source,
            profile=args.streaming_profile,
            target_set=args.transit_target_set,
            daily_sky_source=full_source,
        )
        write_json(output_path, view)
        print(f"Wrote {output_path}")
        return
    elif args.cmd == "synastry":
        logger.info("Building synastry package out=%s", args.out)
        data = synastry.build(
            person_a_provider=args.person_a_provider,
            person_a_jsonl=args.person_a_jsonl,
            person_a_natal_dataset=args.person_a_natal_dataset,
            person_a_name=args.person_a_name,
            person_a_birth_local=args.person_a_birth_local,
            person_a_birth_timezone=args.person_a_birth_timezone,
            person_a_birth_lat=args.person_a_birth_lat,
            person_a_birth_lon=args.person_a_birth_lon,
            person_a_birth_location_label=args.person_a_birth_location_label,
            person_a_source_chart_id=args.person_a_source_chart_id,
            person_b_provider=args.person_b_provider,
            person_b_jsonl=args.person_b_jsonl,
            person_b_natal_dataset=args.person_b_natal_dataset,
            person_b_name=args.person_b_name,
            person_b_birth_local=args.person_b_birth_local,
            person_b_birth_timezone=args.person_b_birth_timezone,
            person_b_birth_lat=args.person_b_birth_lat,
            person_b_birth_lon=args.person_b_birth_lon,
            person_b_birth_location_label=args.person_b_birth_location_label,
            person_b_source_chart_id=args.person_b_source_chart_id,
            snapshot_timezone=args.timezone,
            snapshot_time=args.snapshot_time,
            ephe_path=args.ephe_path,
            house_system=args.house_system,
        )

        def derived_synastry_view_paths() -> tuple[Path, Path]:
            a = safe_name(data["metadata"].get("person_a"))
            b = safe_name(data["metadata"].get("person_b"))
            base = resolve_output_path(args, f"{a}_{b}_synastry_relationship_dataset.json", data)
            if base.suffix:
                analysis = base.with_name(f"{base.stem}.analysis.json")
                streaming = base.with_name(f"{base.stem}.streaming_index.json")
            else:
                base.mkdir(parents=True, exist_ok=True)
                stem = f"{a}_{b}_synastry_relationship_dataset"
                analysis = base / f"{stem}.analysis.json"
                streaming = base / f"{stem}.streaming_index.json"
            return analysis, streaming

        wrote: list[Path] = []
        explicit_view_paths = bool(args.out_analysis or args.out_streaming_index or args.out_full)
        if explicit_view_paths:
            if args.out_analysis:
                path = Path(args.out_analysis)
                logger.info("Writing synastry analysis view to %s", path)
                write_json(path, synastry.analysis_view(data))
                wrote.append(path)
            if args.out_streaming_index:
                path = Path(args.out_streaming_index)
                logger.info("Writing synastry streaming index view to %s", path)
                write_json(path, synastry.streaming_index(data))
                wrote.append(path)
            if args.out_full:
                path = Path(args.out_full)
                logger.info("Writing explicit full-detail synastry package to %s", path)
                write_json(path, data)
                wrote.append(path)
        else:
            analysis_path, streaming_path = derived_synastry_view_paths()
            logger.info("Writing default compact synastry analysis view to %s", analysis_path)
            write_json(analysis_path, synastry.analysis_view(data))
            logger.info("Writing default compact synastry streaming index view to %s", streaming_path)
            write_json(streaming_path, synastry.streaming_index(data))
            wrote.extend([analysis_path, streaming_path])

        for path in wrote:
            print(f"Wrote {path}")
        logger.info("Command complete: wrote %d synastry output files", len(wrote))
        return
    elif args.cmd == "composite":
        logger.info("Building composite package out=%s", args.out)
        data = composite.build(
            person_a_provider=args.person_a_provider,
            person_a_jsonl=args.person_a_jsonl,
            person_a_natal_dataset=args.person_a_natal_dataset,
            person_a_name=args.person_a_name,
            person_a_birth_local=args.person_a_birth_local,
            person_a_birth_timezone=args.person_a_birth_timezone,
            person_a_birth_lat=args.person_a_birth_lat,
            person_a_birth_lon=args.person_a_birth_lon,
            person_a_birth_location_label=args.person_a_birth_location_label,
            person_a_source_chart_id=args.person_a_source_chart_id,
            person_b_provider=args.person_b_provider,
            person_b_jsonl=args.person_b_jsonl,
            person_b_natal_dataset=args.person_b_natal_dataset,
            person_b_name=args.person_b_name,
            person_b_birth_local=args.person_b_birth_local,
            person_b_birth_timezone=args.person_b_birth_timezone,
            person_b_birth_lat=args.person_b_birth_lat,
            person_b_birth_lon=args.person_b_birth_lon,
            person_b_birth_location_label=args.person_b_birth_location_label,
            person_b_source_chart_id=args.person_b_source_chart_id,
            snapshot_timezone=args.timezone,
            snapshot_time=args.snapshot_time,
            ephe_path=args.ephe_path,
            house_system=args.house_system,
        )
        a = safe_name(data["metadata"].get("person_a"))
        b = safe_name(data["metadata"].get("person_b"))
        out = resolve_output_path(args, f"{a}_{b}_composite_dataset.json", data)
    elif args.cmd == "annual-profections":
        data = annual_profections.build(target_dataset=args.target_dataset, target_date=args.target_date, reference_date=args.reference_date)
        target_label = safe_name(data.get("metadata", {}).get("target_label"))
        out = resolve_output_path(args, f"{target_label}_annual_profections_{args.target_date}.json", data)
    elif args.cmd == "solar-return":
        data = solar_return.build(target_dataset=args.target_dataset, return_year=args.return_year, return_location_policy=args.return_location_policy, location_timezone=args.location_timezone, location_lat=args.location_lat, location_lon=args.location_lon, location_label=args.location_label, ephe_path=args.ephe_path, house_system=args.house_system)
        target_label = safe_name(data.get("metadata", {}).get("target_label"))
        out = resolve_output_path(args, f"{target_label}_solar_return_{args.return_year}.json", data)
        if args.out_analysis:
            write_json(args.out_analysis, solar_return.analysis_view(data))
            print(f"Wrote {args.out_analysis}")
    elif args.cmd == "lunar-return":
        data = lunar_return.build(target_dataset=args.target_dataset, start=args.start, end=args.end, return_location_policy=args.return_location_policy, location_timezone=args.location_timezone, location_lat=args.location_lat, location_lon=args.location_lon, location_label=args.location_label, ephe_path=args.ephe_path, house_system=args.house_system)
        target_label = safe_name(data.get("metadata", {}).get("target_label"))
        out = resolve_output_path(args, f"{target_label}_lunar_returns_{args.start}_to_{args.end}.json", data)
    elif args.cmd == "davison":
        data = davison.build(person_a_natal_dataset=args.person_a_natal_dataset, person_b_natal_dataset=args.person_b_natal_dataset, ephe_path=args.ephe_path, house_system=args.house_system)
        out = resolve_output_path(args, "davison_relationship_dataset.json", data)
    elif args.cmd == "eclipse-lunation":
        data = eclipse_lunation.build(start=args.start, end=args.end, target_dataset=args.target_dataset, ephe_path=args.ephe_path)
        target_label = safe_name((data.get("target") or {}).get("label")) if data.get("target") else "global"
        out = resolve_output_path(args, f"{target_label}_eclipse_lunation_{args.start}_to_{args.end}.json", data)
    elif args.cmd == "progressed":
        data = progressed.build()
        out = resolve_output_path(args, "progressed_dataset_scaffold.json", data)
    elif args.cmd == "solar-arc":
        data = solar_arc.build()
        out = resolve_output_path(args, "solar_arc_dataset_scaffold.json", data)
    elif args.cmd == "timeline":
        logger.info("Building timeline package start=%s end=%s out=%s", args.start, args.end, args.out)
        data = timeline.build(
            person_a_provider=args.person_a_provider,
            person_a_jsonl=args.person_a_jsonl,
            person_a_natal_dataset=args.person_a_natal_dataset,
            person_b_provider=args.person_b_provider,
            person_b_jsonl=args.person_b_jsonl,
            person_b_natal_dataset=args.person_b_natal_dataset,
            start=args.start,
            end=args.end,
            snapshot_timezone=args.timezone,
            snapshot_time=args.snapshot_time,
            ephe_path=args.ephe_path,
        )
        out = resolve_output_path(args, f"timeline_{args.start}_to_{args.end}.json", data)
    else:
        raise SystemExit(f"Unknown command {args.cmd}")

    logger.info("Writing command output to %s", out)
    write_json(out, data)
    logger.info("Command complete: wrote %s", out)
    print(f"Wrote {out}")


def cli_entry() -> None:
    """Console entry point with concise optional-dependency failures."""

    try:
        main()
    except ImportError as exc:
        raise SystemExit(f"ERROR: {exc}") from None


if __name__ == "__main__":
    cli_entry()
