# Canonical Temporal Activation Graph

## Status

**Implemented in Astrology Graph Foundry 0.4.0**

Contract:

```text
canonical_temporal_activation_graph.v1
```

Schema:

```text
src/astrology_graph_foundry/schemas/canonical_temporal_activation_graph_v1.schema.json
```

The contract is the Foundry-owned, projection-neutral representation of timing facts. It is consumed by Semantic Projection Core's production temporal route, which emits:

```text
projected_temporal_activation_graph.v1
```

Semantic Projection Core 0.10.0 executes temporal projection from the Foundry source bundle. Static projection of Transit packages remains intentionally rejected because it cannot faithfully represent arcs or observation states.

## Architectural boundary

```text
Foundry Transit package
        ↓
canonical temporal normalization
        ↓
canonical_temporal_activation_graph.v1
        ↓
Foundry temporal projection source bundle
        ↓
Semantic Projection Core temporal_projection_request.v1 adapter
↓
projected_temporal_activation_graph.v1
↓
full / standard / summary / forensic materialization + route receipt
```

The Foundry owns:

- transit calculation;
- target-chart identity;
- activator and target directionality;
- temporal arcs and sampled states;
- date, orb, motion, and provenance facts;
- normalization from package-specific Transit structures.

Semantic Projection Core owns:

- projected temporal contracts;
- target-domain activator and target mappings;
- projected relationship vocabulary;
- temporal profile audit and diagnostics;
- projected timing materializations.

## Primary unit: activation arc

One underlying activation process is represented once as an arc:

```text
starts
→ approaches closest sampled state
→ recedes
→ ends
```

Daily observations are nested states of the arc rather than independent semantic relationships.

This avoids projecting the same Transit separately as:

- many daily snapshots;
- an arc summary;
- an exact-event row;
- a streaming-index row;
- a monthly summary.

## Accepted source materializations

The exporter accepts:

```text
full Transit package
streaming_index Transit materialization
```

It rejects:

```text
analysis Transit materialization
```

because an analysis view may contain only a ranked subset of arcs and cannot truthfully serve as a complete temporal source graph.

## Repeated-pass segmentation

Current Transit packages aggregate observations by:

```text
transiting body
+ aspect
+ target object
```

The canonical exporter conservatively segments those observations into passes when the gap between observations exceeds:

```text
max_observation_gap_days
```

Default:

```text
2 days
```

Every pass shares one `sequence_id` and receives a deterministic `pass_index`.

This is a provisional, source-faithful policy. A future Foundry enhancement may replace gap-based segmentation with solved exact-event and retrograde-loop grouping.

## Exactness policy

Current daily Transit packages contain sampled observations rather than solved exact event times.

The canonical contract therefore distinguishes:

```text
sampled_exact
closest_observed_only
```

A sampled observation at or below the configured orb threshold may populate `exact_at`, but carries an explicit note that the value was sampled rather than numerically solved.

The exporter must never manufacture an exact timestamp from a daily observation.

## Directionality

Every activation preserves:

```text
activator_ref
→ target_ref
```

For example:

```text
canonical:transiting_object:mars
→ natal:Venus
```

The relationship is a temporary:

```text
TRANSIT_ACTIVATION
```

not a permanent static relationship in the target chart.

The target may be:

- Natal;
- Composite;
- Davison.

## Observation phases

Observation states use conservative source-level phase labels:

```text
applying_observed
closest_observed
sampled_exact
separating_observed
```

These are geometry/timing states, not interpretive lifecycle claims.

Terms such as:

```text
introduction
review
integration
closure
```

remain outside this Foundry contract.

## Motion

Where the full package supplies transiting position information, the contract preserves:

```text
direct
retrograde
motion change within activation
longitude
latitude
speed
sign
house
```

Streaming indexes may omit some position details; the contract keeps the motion summary empty rather than guessing.

## Projection source bundle

Foundry also exports:

```text
temporal_projection_source_bundle.v1
```

This bundle packages:

- static canonical target graph;
- structural evidence;
- canonical temporal activation graph;
- target identity;
- source identity;
- activated-target relationship registry.

It is explicitly marked:

```text
reserved_for_semantic_projection_core_temporal_support
```

It is projection-neutral source material rather than an executable Core request. SPC validates and adapts it into `temporal_projection_request.v1` before projection.

The historical `reserved_for_semantic_projection_core_temporal_support` value is
a frozen version-1.0.0 compatibility token. SPC 0.10.0 still validates that
exact value; it does not mean temporal execution remains unavailable.

## Python API

```python
from astrology_graph_foundry import (
    TemporalExportOptions,
    extract_canonical_temporal_activation_graph,
    build_temporal_projection_source_bundle,
)

graph = extract_canonical_temporal_activation_graph(
    transit_package,
    options=TemporalExportOptions(
        max_observation_gap_days=2,
        sampled_exact_orb=0.01,
    ),
)

bundle = build_temporal_projection_source_bundle(transit_package)
```

## CLI

Export the canonical temporal graph:

```bat
astro-package export-temporal-graph ^
  --source-dataset transit.full.json ^
  --out transit.canonical_temporal.json
```

Export the Core handoff:

```bat
astro-package export-temporal-projection-source ^
  --source-dataset transit.full.json ^
  --out transit.temporal_projection_source.json
```

Useful options:

```text
--max-observation-gap-days
--sampled-exact-orb
--omit-observation-states
```

## Acceptance properties

The implementation must preserve:

- deterministic IDs and ordering;
- immutable source package;
- one directional activation per normalized pass;
- separate sequence and pass identity;
- no target-domain projected meaning;
- no false exact-event claims;
- complete source references;
- explicit limitations and diagnostics;
- schema validation.

## Deferred Foundry work

Future enhancements include:

- solved exact-event timestamps;
- exact retrograde/pass grouping;
- station-aware activation segmentation;
- cross-package temporal graph indexes;
- source contracts for ingresses, stations, returns, lunations, and eclipses;
- canonical multi-activation pattern primitives.

These are source-contract improvements and remain separate from target-domain semantic projection.

## 0.4.1 observation-join correction

Full Transit daily rows do not normally materialize `candidate_id`. Exporters must reproduce the Transit pipeline's candidate identity algorithm or join by the normalized `(transiting body, aspect, target)` signature. A healthy arc-first export should ordinarily contain at least some multi-observation activations and should not emit `activation_arc_without_observations` for every arc.


## 0.4.2 observation strength labels and contract freeze

Transit source rows expose aspect tightness as categorical labels such as:

```text
tight
very tight
partile / extremely tight
exact / ultra-partile
```

Canonical temporal observation states preserve this value as:

```json
{
  "strength_label": "very tight"
}
```

The field is intentionally named `strength_label`, not `strength`, because it is a categorical descriptor rather than a numeric measurement. Numeric temporal geometry remains represented through fields such as `orb`, `distance`, and `relevance_score`.

The temporal inspector reports the distribution of observed strength labels as a corpus-level sanity check.

With the 0.4.1 real-observation join correction and this 0.4.2 schema correction, Foundry stages A and B are considered stable for the initial Semantic Projection Core Stage C implementation:

```text
A. canonical_temporal_activation_graph.v1     stable
B. temporal_projection_source_bundle.v1       stable
C. projected_temporal_activation_graph.v1     implemented in Semantic Projection Core 0.10.0
```

“Stable” means the cross-repository contract is implemented and suitable for integration. It does not preclude later versioned improvements such as solved exact-event timestamps, station-aware grouping, or richer source indexes.

## Downstream integration correction

See `Downstream Integration Regression Fixes.md` for the complete static-graph authority, standard-index rematerialization, gameplay target-policy, and legacy daily-sky rules.
