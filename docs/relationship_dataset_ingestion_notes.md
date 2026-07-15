# Relationship Dataset v1 — Ingestion Notes

## Purpose

`relationship_dataset_builder.py` is a second-stage compiler for the existing `Name_2026.jsonl` and `global_transits_2026.jsonl` files produced by `reverse_read_multi_person_generator.py`.

It does **not** replace your current Swiss Ephemeris pipeline. It consumes the exact natal and transit data that pipeline already computes, then builds a reusable relationship-analysis package for synastry reports, forecast reports, manga/story adaptations, infographics, and OMTA/operator-style research.

The resulting package is intended to make large report generation much easier because the expensive astrology facts and relationship evidence are precomputed and ranked.

## Files included

This handoff includes:

1. `relationship_dataset_builder.py`
   - Python compiler for relationship packages.
2. `relationship_dataset_v1.schema.json`
   - JSON Schema describing the output package.
3. `relationship_dataset_ingestion_notes.md`
   - This usage and report-writing guide.

## Recommended workflow

Run your existing generator first:

```bash
python reverse_read_multi_person_generator.py
```

That should produce files similar to:

```text
reverse_read_ephems/
  global_transits_2026.jsonl
  brandi_2026.jsonl
  andrew_2026.jsonl
  kevin_2026.jsonl
```

Then run the relationship builder:

```bash
python relationship_dataset_builder.py \
  --person-a reverse_read_ephems/brandi_2026.jsonl \
  --person-b reverse_read_ephems/andrew_2026.jsonl \
  --global-transits reverse_read_ephems/global_transits_2026.jsonl \
  --out brandi_andrew_relationship_dataset_v1.json
```

The script also writes a Markdown audit summary by default:

```text
brandi_andrew_relationship_dataset_v1.audit.md
```

You can override that path:

```bash
python relationship_dataset_builder.py \
  --person-a reverse_read_ephems/brandi_2026.jsonl \
  --person-b reverse_read_ephems/andrew_2026.jsonl \
  --global-transits reverse_read_ephems/global_transits_2026.jsonl \
  --out brandi_andrew_relationship_dataset_v1.json \
  --audit-md brandi_andrew_relationship_dataset_v1.audit.md
```

## Output structure

The root object looks like this:

```json
{
  "metadata": {},
  "person_a": {},
  "person_b": {},
  "global_transits": {},
  "natal_synastry": {},
  "composite": {},
  "relationship_metrics": {},
  "evidence_graph": [],
  "transit_weather": {},
  "story_materials": {},
  "report_materials": {}
}
```

## Most important sections for report generation

### 1. `person_a` and `person_b`

These embed each person's exact natal chart from the original person JSONL file.

Use them for:

- individual context sections;
- Big Three refresher;
- natal planet tables;
- house and angle references;
- appendices.

### 2. `natal_synastry.interchart_aspects`

This is the main synastry matrix.

Each row contains:

- person A body;
- person B body;
- aspect;
- orb;
- weight;
- theme tags;
- semantic operator hints.

Use this for:

- planet-to-planet synastry;
- high-impact contact sections;
- relationship strengths;
- relationship growth edges;
- exact technical appendix.

Recommended report use:

- Top 10–20 by `weight` for executive summary.
- Top exact contacts by `orb` for technical precision.
- Challenging contacts where `aspect` is `square`, `opposition`, or `quincunx`.
- Supportive contacts where `aspect` is `trine`, `sextile`, or constructive `conjunction`.

### 3. `natal_synastry.house_overlays`

This describes where each person's planets fall in the other's houses.

Use it for:

- “how Brandi experiences Andrew”;
- “how Andrew experiences Brandi”;
- first impressions vs reality;
- partnership field;
- attraction and attachment;
- career/home/intimacy overlays.

The summary subfield ranks house concentrations.

### 4. `relationship_metrics`

This gives heuristic scored themes:

- communication;
- emotional safety;
- romance/affection;
- conflict/drive;
- trust/depth;
- growth/meaning;
- stability/commitment;
- freedom/change.

Each theme includes:

- `score_0_to_10`;
- raw score;
- confidence;
- top supporting evidence.

Use these scores to decide which report sections should be longest.

Example:

If `communication` is 9/10 and `romance_affection` is 5/10, write the relationship as primarily conversational/intellectual rather than primarily romantic/chemistry-driven.

### 5. `evidence_graph`

This is an auditable claim layer.

Each claim includes:

- claim text;
- theme;
- confidence;
- supporting observations;
- supporting evidence IDs.

Use this section to write synthesis paragraphs without drifting into generic astrology. Each major interpretive claim can point back to specific computed evidence.

Recommended workflow:

- Read the highest-confidence claims first.
- Use them to build the executive summary.
- Use supporting observations to write detailed paragraphs.
- Use low-confidence or mixed-polarity claims for nuance.

### 6. `transit_weather`

This is the synastry equivalent of the “long-running 2026 transit climate” section in the natal reports.

It includes:

- monthly relationship-weather scores;
- major weather windows;
- each person's long-running individual transits.

Use this for:

- 2026 relationship climate;
- month-by-month timing;
- periods when both charts are activated;
- stress windows;
- growth windows;
- relationship forecast sections.

Important note:

This is not a formal “transit to composite chart” calculation yet. It is a relationship-weather layer built from both people’s daily reverse-read transit candidates. It asks:

> What relationship-relevant natal functions are activated in both people across 2026?

That is extremely useful for report writing, even without a full transit-to-composite module.

### 7. `story_materials`

This supports the playful section:

> If This Relationship Were a Story...

It includes:

- candidate genres;
- recurring motifs;
- central conflict candidates;
- central gift candidates.

Use it to build a structured story section:

1. Genre
2. Protagonist roles
3. Central conflict
4. Hidden harmony
5. Season finale / developmental lesson

### 8. `report_materials`

This is the pre-chewed writing layer.

It includes:

- executive summary inputs;
- recommended report sections;
- writer guidance.

This is the best place to start if generating a large report with ChatGPT or another LLM.

## Suggested structure for the full Brandi + Andrew synastry report

Recommended production report outline:

```text
# Brandi + Andrew — Full Synastry and 2026 Relationship Weather Report

0. Source and Extraction Summary
1. Executive Summary
2. Individual Context
3. First Impressions vs. Reality
4. What Each Person Brings to the Partnership
5. Planet-to-Planet Synastry
6. House Overlays
7. Communication Dynamics
8. Emotional Safety and Attachment
9. Romance, Affection, and Attraction
10. Conflict and Repair Loops
11. Trust, Depth, and Psychological Activation
12. Stability, Commitment, and Long-Term Potential
13. Freedom, Change, and Autonomy
14. Growth, Meaning, and Shared Direction
15. Hidden Harmony
16. Relationship Operating Manual
17. 2026 Relationship Weather
18. Month-by-Month Relationship Timing
19. If This Relationship Were a Story
20. Practical Guidance
21. Final Synthesis
22. Technical Appendix
```

## How to use the package with ChatGPT

Upload:

- `brandi_andrew_relationship_dataset_v1.json`
- optionally the `.audit.md`

Then prompt:

```text
Please read the attached relationship dataset. Use the package as the source of truth.
Generate a full-length production synastry report using:
- report_materials for section ordering,
- evidence_graph for auditable synthesis,
- relationship_metrics for section emphasis,
- natal_synastry.interchart_aspects for exact synastry,
- house_overlays for mutual experience,
- transit_weather for 2026 relationship climate,
- story_materials for the final story section.

Do not recompute astrology. Do not guess placements. Use exact values from the package.
```

## Schema validation

If you have `jsonschema` installed:

```bash
python -m pip install jsonschema
```

Validate:

```bash
python - <<'PY'
import json
from jsonschema import validate
schema = json.load(open("relationship_dataset_v1.schema.json", encoding="utf-8"))
data = json.load(open("brandi_andrew_relationship_dataset_v1.json", encoding="utf-8"))
validate(data, schema)
print("valid")
PY
```

## Design notes

### Why a second-stage compiler?

The existing generator already does the Swiss Ephemeris work well. The relationship builder should not duplicate that. It should compile already-computed natal and transit facts into relationship-specific structures.

### Why hierarchical JSON instead of JSONL?

The relationship dataset is a graph. It contains nested evidence, metrics, overlays, composite structures, and report materials. A single JSON file is easier to ingest than a line-oriented stream.

### Why include heuristic metrics?

The scores are not meant to be “truth.” They are prioritization aids. They help downstream report generators decide which themes deserve the most attention.

### Why include semantic operator hints?

This makes the package compatible with OMTA-style research. Instead of mapping directly from astrology to prose every time, the package exposes intermediate symbolic verbs such as:

- connect;
- interpret;
- stabilize;
- intensify;
- differentiate;
- contextualize;
- transform.

These operator hints can later support projected chart generation, A1/B1 reverse reads, story adaptation, and infographic generation.

## Current limitations and future upgrades

This version includes:

- interchart aspects;
- house overlays;
- midpoint composite chart;
- relationship metrics;
- evidence graph;
- monthly relationship weather;
- story materials.

Future versions could add:

- formal Davison chart;
- transit-to-composite aspects;
- progressed synastry;
- solar arc directions;
- midpoint structures involving one planet to another pair’s midpoint;
- dispositors and dignity scoring;
- formal elemental/modality balance;
- exact applying/separating based on velocities;
- report paragraph templates;
- visual-layout hints for infographic generation;
- manga cast/scene generator data.

## Recommended next step

Run the builder for Brandi + Andrew and upload:

```text
brandi_andrew_relationship_dataset_v1.json
```

Then the full report can be written from the compiled package rather than from raw ephemeris files.
