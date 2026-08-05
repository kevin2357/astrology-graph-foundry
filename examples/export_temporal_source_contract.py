from __future__ import annotations

import json
from pathlib import Path

from astrology_graph_foundry import (
    build_temporal_projection_source_bundle,
    extract_canonical_temporal_activation_graph,
)


def fixture() -> dict:
    candidates = [
        ("2026-01-01", 1.1, False),
        ("2026-01-02", 0.3, False),
        ("2026-01-03", 0.005, False),
        ("2026-01-04", 0.4, False),
        ("2026-01-10", 0.5, True),
        ("2026-01-11", 0.2, True),
        ("2026-01-12", 0.7, True),
    ]
    days = []
    for day, orb, retrograde in candidates:
        days.append(
            {
                "date": day,
                "transit_datetime": f"{day}T12:00:00-07:00",
                "positions": {
                    "Mars": {
                        "longitude": 120.0,
                        "speed": -0.1 if retrograde else 0.4,
                        "retrograde": retrograde,
                        "sign": "Leo",
                    }
                },
                "candidates": [
                    {
                        "candidate_id": "tc:Mars:square:natal_Venus",
                        "transit_body": "Mars",
                        "aspect": "square",
                        "target": "Venus",
                        "target_id": "natal:Venus",
                        "target_type": "planet_or_point",
                        "target_house": 8,
                        "transit_house_in_target_chart": 6,
                        "rank": 1,
                        "orb": orb,
                        "relevance_score": 0.88,
                        "strength": (
                            "exact / ultra-partile"
                            if orb <= 0.01
                            else "partile / extremely tight"
                            if orb <= 0.5
                            else "very tight"
                        ),
                    }
                ],
            }
        )
    return {
        "metadata": {
            "analysis_type": "transit_range_dataset",
            "target_label": "Example",
            "target_chart_id": "natal:example",
            "target_chart_type": "natal",
            "target_subject_scope": "individual",
            "semantic_scope": "individual_climate",
            "start_date": "2026-01-01",
            "end_date": "2026-01-12",
        },
        "period": {
            "start_date": "2026-01-01",
            "end_date": "2026-01-12",
            "day_count": 12,
        },
        "daily_windows": days,
        "transit_arcs": [
            {
                "arc_id": "arc:tc:Mars:square:natal_Venus",
                "candidate_id": "tc:Mars:square:natal_Venus",
                "transit_body": "Mars",
                "aspect": "square",
                "target": "Venus",
                "target_id": "natal:Venus",
                "target_type": "planet_or_point",
                "target_house": 8,
                "transit_house_in_target_chart": 6,
                "start_date": "2026-01-01",
                "end_date": "2026-01-12",
                "closest_orb": 0.005,
            }
        ],
        "canonical_astrology_graph": {
            "graph_type": "canonical_astrology_graph",
            "graph_version": "1.3.0",
            "source_chart_id": "natal:example",
            "metadata": {
                "graph_id": "canonical:natal:example",
                "source_chart_id": "natal:example",
            },
            "objects": [
                {
                    "id": "natal:Venus",
                    "name": "Venus",
                    "object_type": "planet_or_point",
                    "sign": "Scorpio",
                    "house": 8,
                }
            ],
            "relationships": [],
        },
        "structural_evidence_graph": {
            "graph_type": "structural_evidence_graph",
            "graph_version": "1.3.0",
        },
    }


def main() -> None:
    output = Path(__file__).parent / "outputs"
    output.mkdir(parents=True, exist_ok=True)
    package = fixture()
    graph = extract_canonical_temporal_activation_graph(package)
    bundle = build_temporal_projection_source_bundle(package)
    (output / "canonical_temporal_activation_demo.json").write_text(
        json.dumps(graph, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "temporal_projection_source_bundle_demo.json").write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "graph_summary": graph["summary"],
        "bundle_id": bundle["metadata"]["bundle_id"],
    }, indent=2))


if __name__ == "__main__":
    main()
