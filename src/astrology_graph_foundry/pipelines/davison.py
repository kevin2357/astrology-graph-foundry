from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from astrology_graph_foundry.common.io import read_json
from astrology_graph_foundry.pipelines.natal import build as build_natal
from astrology_graph_foundry.common.transitable_chart import descriptor_for_package
from astrology_graph_foundry.common.semantic_layers import finalize_package_semantic_boundary
from astrology_graph_foundry.common.identity import (
    RELATIONSHIP_CHART_IDENTITY_VERSION,
    derive_relationship_source_chart_id,
    source_chart_id_from_natal_package,
)

SCHEMA_VERSION = "1.0.0"
PIPELINE_VERSION = "davison_pipeline_v1.0.0"


def _load(data: str | dict[str, Any]) -> dict[str, Any]:
    return read_json(data) if isinstance(data, str) else data


def _natal(dataset: dict[str, Any]) -> dict[str, Any]:
    return dataset.get("natal", dataset)


def _utc(natal: dict[str, Any]) -> datetime:
    if natal.get("birth_utc"):
        return datetime.fromisoformat(str(natal["birth_utc"]).replace("Z", "+00:00")).astimezone(timezone.utc)
    local = datetime.fromisoformat(str(natal["birth_local"])).replace(tzinfo=ZoneInfo(str(natal["birth_timezone"])))
    return local.astimezone(timezone.utc)


def build(*, person_a_natal_dataset: str | dict[str, Any], person_b_natal_dataset: str | dict[str, Any], ephe_path: str = ".", house_system: str = "P") -> dict[str, Any]:
    a_ds = _load(person_a_natal_dataset); b_ds = _load(person_b_natal_dataset)
    a = _natal(a_ds); b = _natal(b_ds)
    a_utc = _utc(a); b_utc = _utc(b)
    mid_ts = (a_utc.timestamp() + b_utc.timestamp()) / 2.0
    mid_utc = datetime.fromtimestamp(mid_ts, tz=timezone.utc)
    lat = (float(a["birth_lat"]) + float(b["birth_lat"])) / 2.0
    lon = (float(a["birth_lon"]) + float(b["birth_lon"])) / 2.0
    name_a = a_ds.get("metadata", {}).get("person") or a.get("person") or "A"
    name_b = b_ds.get("metadata", {}).get("person") or b.get("person") or "B"
    participant_source_chart_ids = [
        source_chart_id_from_natal_package(a_ds, fallback_name=name_a),
        source_chart_id_from_natal_package(b_ds, fallback_name=name_b),
    ]
    source_chart_id = derive_relationship_source_chart_id("davison", participant_source_chart_ids)
    chart = build_natal(provider="live", name=f"Davison: {name_a} + {name_b}", birth_local=mid_utc.replace(tzinfo=None).isoformat(timespec="seconds"), birth_timezone="UTC", birth_lat=lat, birth_lon=lon, birth_location_label="Davison midpoint", source_chart_id=source_chart_id, ephe_path=ephe_path, house_system=house_system)
    package = {
        "metadata": {"schema_version": SCHEMA_VERSION, "pipeline_version": PIPELINE_VERSION, "analysis_type": "davison_relationship_dataset", "created_at": datetime.now().isoformat(timespec="seconds"), "person_a": name_a, "person_b": name_b, "source_chart_id": source_chart_id, "participant_source_chart_ids": participant_source_chart_ids, "relationship_chart_identity_version": RELATIONSHIP_CHART_IDENTITY_VERSION},
        "davison_event": {"midpoint_utc": mid_utc.isoformat(), "midpoint_lat": lat, "midpoint_lon": lon, "method": "midpoint in time and space between births; chart cast as a real event"},
        "davison_chart": chart.get("natal", chart),
        "semantic_graph": chart.get("natal", {}).get("semantic_graph"),
        "report_materials": {"recommended_sections": ["Davison Relationship Entity", "Angles and Houses", "Planetary Psychology", "Davison vs Composite Comparison Notes", "Davison Transit Climate"]},
    }
    package["transitable_chart"] = descriptor_for_package(package)
    return finalize_package_semantic_boundary(package)
