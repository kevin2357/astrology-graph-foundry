# Astrology Graph Foundry 0.4.1
## Chunk 3.alpha.1 — Temporal Observation Join and Namespace Completion

This pass completes two focused corrections before Semantic Projection Core implements temporal projection.

## Temporal observation join correction

Full Transit daily candidate rows intentionally omit `candidate_id`; the Transit pipeline reconstructs that identifier using case-preserving body and aspect tokens plus target-token normalization. The initial temporal exporter used a lowercasing slug algorithm for daily rows while arc summaries carried the pipeline-native identifier. Consequently, schema-valid arc summaries could fail to join their dated observation series and degrade into one-state fallback events.

The exporter now:

- reproduces the Transit pipeline's canonical candidate-ID algorithm exactly;
- indexes observations by both canonical candidate ID and a tolerant semantic signature;
- records the observation join policy in activation provenance;
- retains arc-summary fallback only when no real dated observations can be found;
- adds a regression test using realistic full-package daily rows without materialized candidate IDs.

The temporal inspector now emits high-severity diagnostics when:

- every activation contains exactly one observation state; or
- every activation required arc-summary fallback.

These checks prevent a schema-valid but semantically impoverished event list from being mistaken for a healthy arc-first export.

## Namespace and project rename completion

The repository and distribution were already named `astrology-graph-foundry`. This pass completes the Python namespace rename:

```python
astro_analysis_sdk
→ astrology_graph_foundry
```

Current source, tests, examples, scripts, package metadata, console entry points, and active documentation now use the Foundry namespace. The old embedded import namespace is not retained as a compatibility shim because there are no downstream compatibility requirements.

Two active documentation filenames were also renamed:

- `how_to_use_sdk.md` → `How to Use Astrology Graph Foundry.md`
- `SDK Developer Manual.md` → `Astrology Graph Foundry Developer Manual.md`

Historical chat logs and patch artifacts may retain historical names because they document the project's earlier identity rather than defining its current API.

The default log and configuration environment variable were also renamed:

```text
astrology_analysis_sdk.log → astrology_graph_foundry.log
ASTRO_SDK_LOG_CONFIG       → ASTROLOGY_FOUNDRY_LOG_CONFIG
```
