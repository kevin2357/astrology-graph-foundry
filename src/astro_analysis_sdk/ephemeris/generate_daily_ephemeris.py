from __future__ import annotations

import argparse
import logging

from astro_analysis_sdk.common.io import write_json
from astro_analysis_sdk.common.logging_config import configure_logging
from astro_analysis_sdk.ephemeris.models import BirthData, ProviderConfig
from astro_analysis_sdk.ephemeris.providers import LiveSwissEphemerisProvider

logger = logging.getLogger(__name__)

def build_ephemeris_objects(
    *,
    natal_dataset: str | None = None,
    birth_data: BirthData | None = None,
    start: str | None = None,
    end: str | None = None,
    snapshot_timezone: str = "America/Denver",
    snapshot_time: str = "12:00",
    ephe_path: str = ".",
    house_system: str = "P",
    top_n_candidates: int = 25,
):
    logger.info("Building live ephemeris provider natal_dataset=%s birth_data_present=%s start=%s end=%s", natal_dataset, birth_data is not None, start, end)
    return LiveSwissEphemerisProvider(
        natal_dataset,
        ProviderConfig(
            start=start,
            end=end,
            snapshot_timezone=snapshot_timezone,
            snapshot_time=snapshot_time,
            ephe_path=ephe_path,
            house_system=house_system,
            top_n_candidates=top_n_candidates,
        ),
        birth_data=birth_data,
    )

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate normalized natal/transit ephemeris data.")
    parser.add_argument("--natal-dataset")
    parser.add_argument("--name")
    parser.add_argument("--birth-local")
    parser.add_argument("--birth-timezone")
    parser.add_argument("--birth-lat", type=float)
    parser.add_argument("--birth-lon", type=float)
    parser.add_argument("--birth-location-label", default="")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--snapshot-time", default="12:00")
    parser.add_argument("--timezone", default="America/Denver")
    parser.add_argument("--ephe-path", default=".")
    parser.add_argument("--house-system", default="P")
    parser.add_argument("--top-n-candidates", type=int, default=25)
    parser.add_argument("--persist-jsonl")
    parser.add_argument("--persist-json")
    args = parser.parse_args()

    birth_data = None
    if args.natal_dataset is None:
        required = ["name", "birth_local", "birth_timezone", "birth_lat", "birth_lon"]
        missing = [field for field in required if getattr(args, field) in {None, ""}]
        if missing:
            raise SystemExit(f"Either --natal-dataset or full birth data is required. Missing: {', '.join('--' + m.replace('_','-') for m in missing)}")
        birth_data = BirthData(
            name=args.name,
            birth_local=args.birth_local,
            birth_timezone=args.birth_timezone,
            birth_lat=args.birth_lat,
            birth_lon=args.birth_lon,
            birth_location_label=args.birth_location_label,
        )

    provider = build_ephemeris_objects(
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
        provider.persist_jsonl(args.persist_jsonl)
        print(f"Wrote {args.persist_jsonl}")

    if args.persist_json:
        write_json(args.persist_json, {
            "person_metadata": provider.person_metadata(),
            "natal_chart": provider.natal_chart(),
            "daily": [d.__dict__ for d in provider.iter_days()],
        })
        print(f"Wrote {args.persist_json}")

    if not args.persist_jsonl and not args.persist_json:
        print("Provider initialized. No files written because no --persist-jsonl or --persist-json was supplied.")

if __name__ == "__main__":
    main()
