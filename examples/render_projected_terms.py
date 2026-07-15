"""Render deterministic canonical sentences and local paragraphs.

Example:
    python examples/render_projected_terms.py \
      --cognitive path/to/cognitive_projection.json \
      --woofmapped path/to/woofmapped_projection.json \
      --out-json examples/outputs/deterministic_renderer_showcase.json \
      --out-md examples/outputs/deterministic_renderer_showcase.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from semantic_projection.rendering import (
    object_index,
    render_local_narrative,
    render_object_sentence,
)

JsonDict = dict[str, Any]

SELECTIONS = {
    "cognitive": [
        "identity_organization",
        "emotional_regulation",
        "action_selection",
        "change_adaptation",
        "resource_ease_convergence",
    ],
    "woofmapped": [
        "pack_role_identity",
        "scent_signal_interpretation",
        "comfort_safety_regulation",
        "chase_play_defense_drive",
        "training_development_vector",
    ],
}


def load(path: Path) -> JsonDict:
    return json.loads(path.read_text(encoding="utf-8"))


def by_name(graph: JsonDict) -> dict[str, JsonDict]:
    return {str(row["name"]): row for row in graph.get("objects") or []}


def render_profile(graph: JsonDict, *, profile: str, subject: str) -> JsonDict:
    rows = by_name(graph)
    registry = graph["projected_term_registry"]
    rendered = []
    for index, name in enumerate(SELECTIONS[profile]):
        row = rows[name]
        strict = render_object_sentence(row, registry, subject=subject, style="technical")
        natural = render_object_sentence(
            row, registry, subject=subject, style="natural", variant=index
        )
        narrative = render_local_narrative(
            graph, str(row["id"]), subject=subject, relationship_limit=4
        )
        rendered.append({
            "projected_object_id": row["id"],
            "projected_term": name,
            "raw_composition": (row.get("attributes") or {}).get("projection_composition"),
            "registry_entry": registry["terms"][name],
            "strict_sentence": strict.to_dict(),
            "natural_sentence": natural.to_dict(),
            "local_narrative": narrative.to_dict(),
        })
    return {
        "profile": profile,
        "target_ontology": graph["target_ontology"],
        "subject": subject,
        "selection_policy": "fixed_reference_set.v1",
        "items": rendered,
    }


def to_markdown(result: JsonDict) -> str:
    lines = [
        "# Deterministic Projected-Term Renderer Showcase",
        "",
        "This artifact compares raw projected composition, registry context, strict rendering, natural rendering, and bounded local-neighborhood prose. Content selection is fixed in advance; the renderer does not discover clusters or claims.",
        "",
    ]
    for profile in result["profiles"]:
        lines.extend([f"## {profile['profile'].title()}", ""])
        for item in profile["items"]:
            entry = item["registry_entry"]
            lines.extend([
                f"### {entry['canonical_label']}",
                "",
                "**Raw composition**",
                "",
                "```json",
                json.dumps(item["raw_composition"], indent=2),
                "```",
                "",
                f"**Registry description:** {entry['short_description']}",
                "",
                f"**Strict:** {item['strict_sentence']['text']}",
                "",
                f"**Natural:** {item['natural_sentence']['text']}",
                "",
                "**Local paragraph**",
                "",
                item["local_narrative"]["paragraph"],
                "",
                f"*Templates: {', '.join(item['local_narrative']['template_ids'])}*",
                "",
            ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cognitive", type=Path, required=True)
    parser.add_argument("--woofmapped", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    result = {
        "renderer_contract": "deterministic_projected_term_renderer.v0",
        "profiles": [
            render_profile(load(args.cognitive), profile="cognitive", subject="Kevin"),
            render_profile(load(args.woofmapped), profile="woofmapped", subject="Nivek"),
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(to_markdown(result), encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
