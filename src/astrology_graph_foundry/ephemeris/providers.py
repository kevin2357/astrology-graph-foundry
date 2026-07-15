from __future__ import annotations
from datetime import datetime, timedelta
import logging
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo
from astrology_graph_foundry.common.aspects import all_aspects
from astrology_graph_foundry.common.chart_graph import build_chart_graph
from astrology_graph_foundry.common.graph_compiler import GraphCompiler
from astrology_graph_foundry.common.io import load_global, load_person, write_jsonl
from astrology_graph_foundry.common.transitable_chart import TransitableChart, from_package as transitable_chart_from_package
from .live_natal import active_body_map, build_live_natal_chart, datetime_to_jd_ut, safe_planet_position
from .models import BirthData, DailySnapshot, ProviderConfig

logger = logging.getLogger(__name__)

class EphemerisProvider:
    def target_metadata(self) -> dict[str, Any]: raise NotImplementedError
    def target_chart(self) -> dict[str, Any]: raise NotImplementedError
    # Natal aliases remain internal conveniences for natal-generation code.
    def person_metadata(self) -> dict[str, Any]: return self.target_metadata()
    def natal_chart(self) -> dict[str, Any]: return self.target_chart()
    def iter_days(self) -> Iterable[DailySnapshot]: raise NotImplementedError
    def graph_compiler(self, *, relationship_limit: int = 12):
        return None
    def to_jsonl_rows(self) -> list[dict[str, Any]]:
        person = self.person_metadata().get("person")
        rows = [{**self.person_metadata(), "type": "person_metadata"}, {**self.natal_chart(), "type": "natal_chart"}]
        rows.extend(day.as_person_daily_snapshot(person=person) for day in self.iter_days())
        return rows
    def persist_jsonl(self, output_path: str | Path) -> None:
        logger.info("Persisting provider JSONL to %s", output_path)
        write_jsonl(output_path, self.to_jsonl_rows())

class CachedJsonlEphemerisProvider(EphemerisProvider):
    def __init__(self, person_jsonl: str | Path, start: str | None = None, end: str | None = None, global_jsonl: str | Path | None = None):
        self.person_jsonl = Path(person_jsonl); self.start = start; self.end = end
        logger.info("Initializing CachedJsonlEphemerisProvider person_jsonl=%s start=%s end=%s global_jsonl=%s", person_jsonl, start, end, global_jsonl)
        self.person = load_person(self.person_jsonl); self.global_data = load_global(global_jsonl)
        self.person["natal"].setdefault("semantic_graph", build_chart_graph(self.person["natal"]))
    def _in_range(self, date: str) -> bool:
        return (self.start is None or date >= self.start) and (self.end is None or date <= self.end)
    def target_metadata(self) -> dict[str, Any]:
        return {**self.person["metadata"], "provider": "cached_jsonl", "chart_type": "natal", "subject_scope": "individual", "semantic_scope": "individual_climate"}
    def target_chart(self) -> dict[str, Any]:
        return self.person["natal"]
    def iter_days(self) -> Iterable[DailySnapshot]:
        global_by_date = {d.get("date_local"): d for d in self.global_data["daily"]} if self.global_data else {}
        for row in self.person["daily"]:
            date = str(row.get("date_local"))
            if not self._in_range(date): continue
            g = global_by_date.get(date, {})
            yield DailySnapshot(date, g.get("local_datetime") or row.get("local_datetime"), g.get("utc_datetime") or row.get("utc_datetime"), g.get("jd_ut") or row.get("jd_ut"), g.get("positions", row.get("positions", {})), g.get("transit_to_transit_aspects", []), row.get("transit_to_natal_aspects", []), row.get("reverse_read_candidates", []))

class LiveSwissEphemerisProvider(EphemerisProvider):
    def __init__(self, target_dataset: str | Path | dict[str, Any] | None, config: ProviderConfig, birth_data: BirthData | None = None):
        logger.info("Initializing LiveSwissEphemerisProvider target_dataset=%s birth_data_present=%s start=%s end=%s", target_dataset, birth_data is not None, config.start, config.end)
        try:
            import swisseph as swe
        except ImportError as exc:
            raise ImportError("LiveSwissEphemerisProvider requires pyswisseph (`pip install pyswisseph`).") from exc
        self.swe = swe; self.config = config; self.swe.set_ephe_path(config.ephe_path)
        if birth_data is not None:
            logger.info("Computing live natal chart for %s", birth_data.name)
            self.dataset = {"metadata": {"analysis_type": "natal_dataset", "person": birth_data.name}, "person": {"person": birth_data.name, "birth_local": birth_data.birth_local, "birth_timezone": birth_data.birth_timezone, "birth_lat": birth_data.birth_lat, "birth_lon": birth_data.birth_lon, "birth_location_label": birth_data.birth_location_label}, "natal": build_live_natal_chart(birth_data, config)}
        elif target_dataset is not None:
            from astrology_graph_foundry.common.io import read_json
            logger.info("Loading existing TransitableChart target package: %s", target_dataset if not isinstance(target_dataset, dict) else "<dict>")
            self.dataset = read_json(target_dataset) if not isinstance(target_dataset, dict) else target_dataset
        else:
            raise ValueError("LiveSwissEphemerisProvider requires either target_dataset or birth_data")
        self._target: TransitableChart = transitable_chart_from_package(self.dataset)
        self._chart = self._target.chart
        logger.info("Building/normalizing target semantic graph for %s", self._target.label)
        self._chart["semantic_graph"] = self._target.semantic_graph or build_chart_graph(self._chart)
        self._active_bodies = None; self._skipped_transit_bodies = []
        self._graph_compiler = GraphCompiler(self._chart)
    def graph_compiler(self, *, relationship_limit: int = 12):
        if self._graph_compiler.relationship_limit == relationship_limit:
            return self._graph_compiler
        return GraphCompiler(self._chart, relationship_limit=relationship_limit)
    def target_metadata(self) -> dict[str, Any]:
        return {
            "person": self._target.label,
            "target_label": self._target.label,
            "target_chart_id": self._target.chart_id,
            "chart_type": self._target.chart_type,
            "subject_scope": self._target.subject_scope,
            "semantic_scope": self._target.semantic_scope,
            "construction": self._target.construction,
            "provider": "live_swiss_ephemeris",
            "start_date": self.config.start,
            "end_date": self.config.end,
            "snapshot_timezone": self.config.snapshot_timezone,
            "snapshot_time": self.config.snapshot_time,
            "skipped_transit_bodies": self._skipped_transit_bodies,
        }
    def target_chart(self) -> dict[str, Any]:
        return self._chart
    def _ensure_active_bodies(self, jd_ut: float) -> dict[str, int]:
        if self._active_bodies is None:
            self._active_bodies, self._skipped_transit_bodies = active_body_map(self.swe, jd_ut, self.config)
            logger.info("Active transit body map initialized: %d bodies, %d skipped", len(self._active_bodies), len(self._skipped_transit_bodies))
        return self._active_bodies
    def _daily_positions(self, jd_ut: float) -> dict[str, dict[str, Any]]:
        positions = {}
        for name, swe_id in self._ensure_active_bodies(jd_ut).items():
            pos, error = safe_planet_position(self.swe, jd_ut, swe_id)
            if error or pos is None:
                logger.warning("Skipping transit body %s: %s", name, error or "unknown calculation failure")
                self._skipped_transit_bodies.append({"name": name, "swe_id": swe_id, "reason": error or "unknown calculation failure"})
            else:
                positions[name] = pos
        return positions
    def _transit_to_target(self, positions):
        rows, ranked = self._graph_compiler.transit_to_target_candidates(
            positions,
            include_minor=self.config.include_minor,
            top_n=self.config.top_n_candidates,
        )
        logger.debug("Computed %d transit-to-natal candidate rows before ranking", len(rows))
        return rows, ranked
    def iter_days(self) -> Iterable[DailySnapshot]:
        if not self.config.start or not self.config.end: return
        start_dt = datetime.fromisoformat(self.config.start); end_dt = datetime.fromisoformat(self.config.end)
        hour, minute = [int(x) for x in self.config.snapshot_time.split(":", 1)]; tz = ZoneInfo(self.config.snapshot_timezone)
        total_days = (end_dt.date() - start_dt.date()).days + 1
        logger.info("Beginning daily ephemeris iteration: %s to %s (%d days)", start_dt.date(), end_dt.date(), total_days)
        count = 0
        cur = start_dt
        while cur <= end_dt:
            local_dt = cur.replace(hour=hour, minute=minute, second=0, tzinfo=tz)
            jd_ut, utc_dt = datetime_to_jd_ut(self.swe, local_dt)
            positions = self._daily_positions(jd_ut)
            t2t = all_aspects(positions, positions, "transit", "transit", include_minor=self.config.include_minor)
            t2n, candidates = self._transit_to_target(positions)
            count += 1
            if count == 1 or count % 10 == 0 or count == total_days:
                logger.info("Generated daily snapshot %d/%d for %s: positions=%d t2n=%d candidates=%d", count, total_days, cur.date(), len(positions), len(t2n), len(candidates))
            yield DailySnapshot(str(cur.date()), local_dt.isoformat(), utc_dt.isoformat(), jd_ut, positions, t2t, t2n, candidates)
            cur += timedelta(days=1)
        logger.info("Completed daily ephemeris iteration: %d days", count)

def create_provider(provider: str, *, person_jsonl: str | Path | None = None, target_dataset: str | Path | dict[str, Any] | None = None, birth_data: BirthData | None = None, global_jsonl: str | Path | None = None, config: ProviderConfig | None = None) -> EphemerisProvider:
    config = config or ProviderConfig()
    logger.info("Creating ephemeris provider: %s", provider)
    if provider == "cached":
        if person_jsonl is None: raise ValueError("provider='cached' requires person_jsonl")
        return CachedJsonlEphemerisProvider(person_jsonl, start=config.start, end=config.end, global_jsonl=global_jsonl)
    if provider == "live":
        return LiveSwissEphemerisProvider(target_dataset, config, birth_data=birth_data)
    raise ValueError(f"Unknown provider: {provider}")
