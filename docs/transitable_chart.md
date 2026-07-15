# TransitableChart Interface

`TransitableChart` is the common transit-target interface shared by natal, composite, and Davison packages.

The interface exists so the transit engine can consume chart-like semantic packages without treating every chart as natal and without adding pipeline-specific branches to transit calculation.

```text
Natal package ───────┐
Composite package ───┼─> TransitableChart ─> transit pipeline
Davison package ─────┘
```

## Package contract

A transitable package contains its normal chart field plus a `transitable_chart` descriptor:

```json
{
  "transitable_chart": {
    "interface_version": "transitable_chart_v1.0.0",
    "chart_identity": {
      "chart_id": "davison:davison_kevin_bre",
      "chart_type": "davison",
      "subject_scope": "relationship",
      "semantic_scope": "relationship_lifecycle_climate",
      "label": "Davison: Kevin + Bre"
    },
    "chart_key": "davison_chart",
    "construction": {
      "method": "midpoint in time and space between births; chart cast as a real event"
    },
    "capabilities": {
      "supports_longitude_aspects": true,
      "supports_house_transits": true,
      "supports_angle_transits": true,
      "supports_semantic_graph_activation": true
    }
  }
}
```

The descriptor references the package's existing chart field rather than duplicating the full chart.

## Supported chart types

| Chart type | Subject scope | Semantic scope | Transit question |
|---|---|---|---|
| `natal` | `individual` | `individual_climate` | What weather is the individual experiencing? |
| `composite` | `relationship` | `relationship_pattern_climate` | Which mechanisms in the relationship pattern are activated? |
| `davison` | `relationship` | `relationship_lifecycle_climate` | What chapter or season is the relationship entity living through? |

Composite support is exposed by the interface in this release, while the first validated relationship-target implementation is Davison transit generation. Composite transit validation and target-policy refinement remain the next development pass.

## CLI

The transit command now accepts `--target-dataset`; `--natal-dataset` is no longer part of the transit CLI.

```bat
python -m astrology_graph_foundry.cli transit ^
  --provider live ^
  --target-dataset outputs\kevin_bre_test\kevin_bre_davison.json ^
  --start 2026-01-01 ^
  --end 2027-07-01 ^
  --timezone America/Denver ^
  --snapshot-time 12:00 ^
  --ephe-path C:\dev\swisseph ^
  --out outputs\kevin_bre_test\kevin_bre_davison_transit.json
```

The same command works with a natal package. Composite packages also implement the interface and can be used as targets, but composite-specific target policy and report validation are scheduled for the next pass.

## Transit output metadata

Transit packages identify the target explicitly:

```json
{
  "target_label": "Davison: Kevin + Bre",
  "target_chart_type": "davison",
  "target_subject_scope": "relationship",
  "semantic_scope": "relationship_lifecycle_climate"
}
```

Candidate and arc fields are now generic:

- `target`
- `target_id`
- `target_name`
- `target_type`
- `target_house`
- `transit_house_in_target_chart`
- `activated_target_relationship_refs`

This replaces natal-only field naming in transit outputs.


## Timing capabilities

`TransitableChart` now exposes a `reference_event` and capability flags for:

- transit aspects;
- eclipse/lunation activation;
- solar returns where a reference event exists.

Natal charts use the birth event. Davison charts use the real midpoint event. Composite charts use a clearly labeled **synthetic midpoint reference event** only as the annual-return search anchor. This does not change the midpoint-longitude construction of the composite chart.

Solar-return and eclipse/lunation pipelines accept `--target-dataset`; they no longer require a natal-specific package.


## Lunar-return and profection capabilities

The interface now supports:

- `solar-return`: exact Sun return, anchored by the target reference event;
- `lunar-return`: every exact Moon return in a requested date range;
- `annual-profections`: completed-year activation from the target reference event;
- `eclipse-lunation`: lunation contacts and eclipse-season windows;
- `transit`: daily/range transit climate.

Natal interpretations are the traditional/default case. Composite and Davison timing outputs preserve relationship-specific semantic scopes. Relationship-entity annual profections are marked experimental in package metadata and prose.


## Return location is not part of the target identity

The `reference_event` supplies a possible return location, but Solar and Lunar Return pipelines do not silently assume it. Callers must select `target_reference` or provide an explicit lived/event location. The target chart still determines the exact Sun/Moon return moment; the return location determines houses and angles.
