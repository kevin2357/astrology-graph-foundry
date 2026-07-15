from __future__ import annotations
import logging
from datetime import datetime
from astrology_graph_foundry.ephemeris.models import ProviderConfig
from astrology_graph_foundry.ephemeris.providers import create_provider
from astrology_graph_foundry.pipelines.transit_period import build_from_provider

logger = logging.getLogger(__name__)
def build(*, person_a_provider: str="cached", person_a_jsonl: str | None=None, person_a_natal_dataset: str | None=None, person_b_provider: str | None=None, person_b_jsonl: str | None=None, person_b_natal_dataset: str | None=None, start: str, end: str, snapshot_timezone: str="America/Denver", snapshot_time: str="12:00", ephe_path: str="."):
    logger.info("Building timeline package start=%s end=%s person_b_present=%s", start, end, bool(person_b_provider))
    cfg=ProviderConfig(start=start,end=end,snapshot_timezone=snapshot_timezone,snapshot_time=snapshot_time,ephe_path=ephe_path)
    a=create_provider(person_a_provider,person_jsonl=person_a_jsonl,target_dataset=person_a_natal_dataset,config=cfg)
    out={"metadata":{"schema_version":"1.0.0","analysis_type":"timeline_dataset","created_at":datetime.now().isoformat(timespec="seconds"),"start":start,"end":end},"person_a_period":build_from_provider(a,start,end),"person_b_period":None}
    if person_b_provider:
        b=create_provider(person_b_provider,person_jsonl=person_b_jsonl,target_dataset=person_b_natal_dataset,config=cfg); out["person_b_period"]=build_from_provider(b,start,end)
    logger.info("Timeline package complete start=%s end=%s", start, end)
    return out
