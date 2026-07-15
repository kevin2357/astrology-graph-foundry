# Report Blueprint Specification

**Status:** Pass 2 design document.  
**Scope:** Standard/reference report formats and the future `report_view.json` intermediate representation.

## 1. Summary

A report blueprint is a declarative recipe for assembling SDK package outputs into a report-ready evidence structure.

```text
SDK packages
↓
blueprint compiler
↓
report_view.json
↓
prose writer / publisher / dashboard / game adapter
```

The blueprint is not prose and not layout. It is a report architecture.

## 2. Why blueprints matter

As the SDK adds pipelines, downstream consumers need to know how to combine them. A yearly report, monthly report, synastry report, professional relationship report, and Mythos game mechanic model use different evidence stacks.

## 3. Blueprint fields

```json
{
  "id": "yearly_integrated.v1",
  "name": "Integrated Yearly Report",
  "scope": "individual",
  "timeframe": "year",
  "required_inputs": [],
  "optional_inputs": [],
  "sections": [],
  "evidence_policies": {},
  "fallbacks": {},
  "output_contract": "report_view.v1"
}
```

## 4. Report view fields

```json
{
  "metadata": {},
  "source_packages": [],
  "headline_claims": [],
  "evidence_bundles": [],
  "contradictions": [],
  "sections": [],
  "timeline_highlights": [],
  "projection_hints": [],
  "publisher_hints": []
}
```

## 5. Evidence bundle shape

```json
{
  "id": "bundle.year_theme.9th_house_reframe",
  "claim": "The year emphasizes worldview, abstraction, learning, and meaning reconstruction.",
  "supporting_evidence": [
    {"pipeline": "annual_profections", "ref": "profection.house.9"},
    {"pipeline": "solar_return", "ref": "solar_return.sun.house.9"},
    {"pipeline": "transit", "ref": "transit.pluto_square_mercury"}
  ],
  "confidence": "high",
  "notes": "Example adapted from generated yearly report."
}
```

## 6. Standard report catalog

### 6.1 Natal Baseline Report

Required: natal analysis/full.

Sections: executive summary; chart architecture; big three; planet functions; houses; aspects; strengths; growth edges; practical operating notes.

### 6.2 Daily Transit Report

Required: natal and transit day. Optional: lunation/eclipses and monthly/annual context.

### 6.3 Monthly Integrated Report

Required: natal, lunar return, transit date range. Optional: annual profection, solar return, eclipse/lunation. The July report is the reference example.

### 6.4 Yearly Integrated Report

Required: natal, solar return, annual profection, transit range. Optional: eclipse/lunation and lunar returns. The 2026 yearly report is the reference example.

### 6.5 Full Relationship Analysis

Required: natal A, natal B, synastry, composite, Davison. Kevin/Bre is the reference example.

### 6.6 Professional Relationship Report

Required: natal A/B and synastry. Optional: composite/Davison. Projection context avoids romance language.

### 6.7 Mythos Game Relationship Model

Required: player natal packages and pairwise synastry. Optional: composite/Davison/transits. Output: trait vectors, affinity bonuses, conflict pressures, AI behavior weights, story hooks.

## 7. Narrative units

Narrative units are report-view building blocks: topic, evidence, importance, section fit, visualization hints, projection hints, and quote/pull-quote candidates.

They emerged from the publishing thread because a magazine-style report cannot be just paragraphs poured into pages. Each spread needs a purpose and evidence contract.

## 8. Publisher hints

A report view may include publisher hints without binding to a renderer:

```json
{
  "suggested_visualizations": ["timeline_band", "aspect_network"],
  "spread_archetype": "hero_plus_sidebar",
  "pull_quote_candidates": [],
  "density": "medium"
}
```

## 9. Implementation path

1. Write JSON schemas for `report_blueprint` and `report_view`.
2. Create reference blueprint files for `yearly_integrated`, `monthly_integrated`, and `full_relationship_analysis`.
3. Write toy compilers that read current SDK outputs.
4. Compare generated report views against the hand-written reference reports.
5. Refine evidence bundles and section shapes.
