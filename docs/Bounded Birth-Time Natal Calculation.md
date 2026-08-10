# Bounded Birth-Time Natal Calculation

**Status:** Accepted design direction; not implemented in Astrology Graph Foundry
0.6.0

**Owner:** Astrology Graph Foundry for calculation, canonical source facts,
uncertainty evidence, provenance, schemas, and source capabilities

**Consumers requiring compatibility review:** Semantic Projection Core, Semantic
Basis Extractor, AstroWoof API, and other Natal-package consumers

## Purpose

AGF currently requires one exact local birth datetime and emits an exact Natal
package. Some subjects, including many animals and historical or poorly documented
human subjects, have a known date or approximate time range but no defensible exact
instant.

The intended new mode accepts a bounded birth-time basis and produces only natal
facts proven valid throughout the complete interval. It must preserve uncertainty
explicitly rather than hiding a representative noon calculation behind exact-looking
longitudes, houses, angles, aspects, and derived structures.

This document describes the current design intention. Code, schemas, CLI flags, and
released package guarantees do not yet implement it.

## Core invariant

> A fact may enter the bounded Natal canonical graph only when AGF has proven that
> the fact remains true throughout the normalized birth-time interval under the
> pinned calculation and uncertainty-assessment profile.

Failure to prove invariance is not proof that a fact is false. Such a feature is
reported as conditional, variable, or unavailable. Provider/runtime failure remains
a separate failure class.

## Proposed input contract

Use a tagged birth-time basis rather than optional combinations of unrelated fields:

```json
{
  "mode": "bounded",
  "earliest_local": "2024-05-12T08:00:00",
  "latest_local": "2024-05-12T14:00:00",
  "timezone": "America/Denver"
}
```

Proposed modes:

- `exact`: one validated local civil datetime;
- `bounded`: earliest and latest complete local datetimes; and
- `unknown_day`: a known local calendar date normalized to its complete local day.

For CLI exposure, prefer `--birth-local-earliest` and
`--birth-local-latest`. “Earlier than” and “later than” are easier to reverse and do
not naturally communicate complete datetime or boundary semantics.

The reviewed contract must decide endpoint inclusivity, maximum interval duration,
ambiguous/nonexistent local-time behavior, and whether a zero-width bounded range is
accepted or normalized to `exact`. A whole local day is not assumed to be 24 UTC
hours because timezone transitions may produce 23- or 25-hour days.

## Why sign-change filtering is insufficient

All moving bodies have uncertain exact longitude across a nonzero interval even
when their zodiac sign is invariant. Other categorical or derived facts can change
inside the interval:

- direct/retrograde state near a station;
- an aspect entering or leaving its allowed orb;
- aspect strength or applying/separating state;
- sign-dependent dignity when a body crosses a sign;
- sect when the interval crosses sunrise or sunset;
- house and angle geometry; and
- lots and calculated points whose inputs or formula branch are time-dependent.

Endpoint equality does not establish invariance. Retrograde loops, 360-degree
wraparound, interior aspect extrema, and multiple crossings can return the same
endpoint category after changing inside the interval.

## Initial calculation scope

The first implementation should conservatively assess:

- bounded longitude ranges for ordinary configured bodies;
- invariant versus possible zodiac signs;
- invariant versus variable motion state;
- sign-dependent dignity only when its inputs are invariant; and
- ordinary body-to-body aspects as invariant, conditional, or absent throughout the
  interval, with bounded orb evidence where supportable.

Initially treat these as unavailable in bounded mode:

- house cusps and house placements;
- ASC, DSC, MC, IC, and Vertex;
- sect;
- Part of Fortune, Spirit, and other angle/sect-dependent lots;
- angle and house aspects; and
- downstream operations requiring one exact natal longitude unless a reviewed
  bounded operation exists.

This deliberately conservative first scope can expand later without laundering
uncertainty into the canonical graph.

## Proposed artifact layers

### Birth-time basis

Record supplied and normalized local bounds, resolved UTC bounds, IANA timezone,
boundary policy, normalization-policy version, uncertainty-assessment profile, and
whether the basis was exact, genuinely bounded, or derived from an unknown date-only
input.

### Bounded calculation evidence

Retain enough compact evidence to audit the classification: evaluated range,
transition/refinement findings, tolerances, requested and observed ephemeris mode,
and feature extrema or possible categorical values. Do not retain bulky sampling
traces unless they are required for qualification or dispute analysis.

### Uncertainty assessment

Use explicit statuses:

- `invariant`: proven true throughout the interval;
- `conditional`: true for only a documented subset;
- `variable`: categorical value changes across the interval;
- `unavailable`: intentionally not derivable under this mode/profile; and
- `calculation_failed`: expected calculation could not be completed.

Each excluded feature records its reason and, where useful, possible values,
longitude/orb range, or transition windows.

### Canonical graph

Emit invariant facts only. Do not put a representative midpoint/noon longitude into
the current exact-placement object shape. The design sprint must choose either new
bounded object/relationship types or a bounded graph materialization that can state
stable categorical facts without asserting an exact degree.

### Capabilities

The artifact must advertise reduced capabilities. At minimum, consumers must be able
to distinguish exact longitude aspects, bounded aspects, house transits, angle
transits, and semantic graph activation. An exact-only consumer must reject or
deliberately adapt a bounded artifact rather than assuming full Natal equivalence.

## Calculation strategy

Swiss Ephemeris can calculate positions and speeds at arbitrary UT Julian dates, so
the provider supports interval evaluation. Correctness requires a versioned AGF
algorithm above those point calculations.

A reasonable initial strategy is conservative adaptive sampling with transition
detection and numerical refinement. The profile must define step selection,
tolerances, wraparound handling, station detection, aspect-boundary refinement, and
the condition under which AGF declares proof inconclusive. Inconclusive evidence is
never promoted merely because sampled endpoints agree.

## Identity, hashing, and provenance

`source_chart_id` remains the stable caller-owned chart lineage. Correcting or
narrowing birth-time bounds creates a new calculation/input identity and artifact;
it does not inherently require a new chart lineage.

The normalized source-input hash must include normalized bounds, timezone, boundary
policy, and normalization-policy version. The configuration hash must include the
uncertainty algorithm/profile, tolerances, evaluated feature policy, and ordinary
calculation settings. The persistence owner still hashes the exact retained package
bytes.

Legacy warned-noon and bounded artifacts occupy different calculation-policy
namespaces. A historical noon artifact must never be relabeled as bounded evidence.

## Downstream boundary

- SPC may project canonical invariant facts and preserve their evidence. It must not
  reconstruct omitted exact placements or introduce a noon chart.
- SBE and authoring systems must apply eligibility before selection, synthesis, and
  summaries. Hiding unsupported cards after authorship is insufficient.
- An API owns collection, civil-time acceptance, immutable birth versions, policy
  selection, orchestration, storage, and reader-facing qualification.
- AGF remains reusable and does not learn dog, user, breed, handler, or product
  database semantics.

## Versioning expectation

This is additive at the product capability level but materially changes input,
package, graph, and consumer semantics. The sprint must choose versions from actual
schema impact; it should not force the mode into the current Birth Data v1 or exact
Natal contract merely to obtain a patch-level release.

## Acceptance examples

Required fixtures should include:

- a narrow interval with stable Moon sign;
- a Moon sign ingress inside the interval;
- a body station inside the interval;
- an aspect entering or leaving orb;
- zodiac longitude wraparound;
- a short and long DST local calendar day;
- an interval crossing local midnight;
- deterministic repeated evaluation;
- calculation/provider failure distinct from uncertainty; and
- exact input compared with its accepted zero-width equivalent, if supported.

No uncertain feature may appear as an exact canonical fact, no omitted feature may
vanish without classified evidence, and no downstream exact-only path may accept a
bounded artifact silently.

## Open design decisions

- bounded graph vocabulary and object/relationship IDs;
- proof algorithm, tolerances, and evidence compactness;
- aspect semantics when type remains invariant but orb/strength/application varies;
- whether estimated representative positions have any non-canonical consumer role;
- duration limits and performance budgets;
- package/schema/profile version increments;
- exact SPC compatibility contract;
- whether timing pipelines can target bounded placements and with what semantics;
- migration timing for consumers currently using warned noon; and
- qualification and release matrix.
