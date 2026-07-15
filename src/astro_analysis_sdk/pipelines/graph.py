from __future__ import annotations
from datetime import datetime
from astro_analysis_sdk.common.chart_graph import build_chart_graph
from astro_analysis_sdk.common.io import read_json


def build(*, natal_dataset: str | None = None, natal: dict | None = None, **kwargs):
    if natal_dataset:
        data = read_json(natal_dataset)
        natal = data.get("natal", data)
    graph = build_chart_graph(natal or {})
    return {
        "metadata": {
            "schema_version": "1.0.0",
            "analysis_type": "graph_dataset",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
        **graph,
    }
