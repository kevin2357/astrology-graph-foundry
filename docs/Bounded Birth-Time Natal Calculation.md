# Bounded Birth-Time Natal Calculation

**Status:** Implemented on `main` for the Astrology Graph Foundry 0.7.0 release
candidate; not yet published

**Owner:** Astrology Graph Foundry for calculation, canonical source facts,
uncertainty evidence, provenance, schemas, and source capabilities

**Consumers requiring compatibility review:** Semantic Projection Core, Semantic
Basis Extractor, AstroWoof API, and other Natal-package consumers

## Purpose

AGF supports its established exact Natal package and a separate bounded Natal
package for subjects whose date or approximate time range is known but whose exact
instant is not defensible. This is common for animals and may also apply to
historical or poorly documented human subjects.

The bounded mode accepts a bounded birth-time basis and produces only natal
facts proven valid throughout the complete interval. It must preserve uncertainty
explicitly rather than hiding a representative noon calculation behind exact-looking
longitudes, houses, angles, aspects, and derived structures.

The 0.7.0 candidate implements the Python/CLI input, interval evaluation, schemas,
canonical graph, uncertainty evidence, provenance, capabilities, and exact-only
consumer rejections described here. SPC and SBE support remains a separate follow-on
sprint; the published 0.6.0 wheel does not implement bounded Natal.

## Core invariant

> A fact may enter the bounded Natal canonical graph only when AGF has proven that
> the fact remains true throughout the normalized birth-time interval under the
> pinned calculation and uncertainty-assessment profile.

Failure to prove invariance is not proof that a fact is false. Such a feature is
reported as conditional, variable, or unavailable. Provider/runtime failure remains
a separate failure class.

## Input contract

Use a tagged birth-time basis rather than optional combinations of unrelated fields:

```json
{
  "mode": "bounded",
  "earliest_local": "2024-05-12T08:00:00",
  "latest_local": "2024-05-12T14:00:00",
  "timezone": "America/Denver"
}
```

Modes:

- `exact`: one validated local civil datetime;
- `bounded`: earliest and latest complete local datetimes; and
- `unknown_time`: a known local calendar date with no known time, normalized to its
  complete local day.

For CLI exposure, prefer `--birth-local-earliest` and
`--birth-local-latest`. “Earlier than” and “later than” are easier to reverse and do
not naturally communicate complete datetime or boundary semantics.

Caller-supplied endpoints are inclusive. `unknown_time` spans local midnight
inclusive to the next local midnight exclusive. The v1 maximum is 48 elapsed UTC
hours. Empty/inverted bounds are rejected, and a zero-width range must use exact
mode. Ambiguous or nonexistent boundary wall times fail closed. A whole local day is
not assumed to be 24 UTC hours because timezone transitions may produce 23- or
25-hour days.

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

## Implemented calculation scope

The 0.7.0 candidate conservatively assesses:

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

## Artifact layers

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

The post-0.7.0 working source formalizes
`agf.bounded_uncertainty_evidence.v1.0.0` as an additive evidence envelope. Existing
`longitude_range`, `motion`, `possible_sign_indexes`, `possible_aspects`, and
`orb_range` fields remain available while new nested evidence adds:

- circular ranges represented as one or more ordered closed segments;
- scalar proof ranges with optional observed subranges;
- deterministic categorical possibility sets;
- prerequisite evidence references;
- adjacent sampled transition witnesses;
- compact counterexamples explaining withheld invariance; and
- an explicit complete-normalized-birth-interval proof scope.

This is deliberate dual-write compatibility. Saved 0.7-shaped artifacts remain
readable and valid under their original contract; consumers should feature-detect
the new `evidence_contract_version` rather than assuming every bounded artifact has
the generalized envelope.

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

Proof profile `agf.interval_proof.v1.0.0` evaluates every valid minute throughout the
interval, unwraps circular longitude, and adds speed-derived safety envelopes to
longitude and aspect ranges. Provider failure, non-finite/missing point data, and
evaluation-budget exhaustion are inconclusive. Inconclusive evidence is never
promoted merely because sampled endpoints agree. Controlled Linux/Python 3.11
Moshier evidence measured approximately 0.70 seconds for 24 hours and 1.27 seconds
for the maximum 48 hours.

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

## Versioning

This is additive at the product capability level but materially changes input,
package, graph, and consumer semantics. The package candidate is AGF 0.7.0. Exact
Birth Data v1, Natal Dataset 1.1.0, and canonical graph 1.3.0 remain unchanged.
Bounded contracts begin at Birth Data v1, Bounded Natal Dataset 1.0.0, bounded
canonical graph 1.0.0, bounded calculation provenance 1.0.0, and interval proof
profile 1.0.0.

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

## Deferred follow-on decisions

- SPC and SBE compatibility and release versions;
- aspect strength/application semantics;
- whether estimated representative positions have any non-canonical consumer role;
- whether timing pipelines can target bounded placements and with what semantics;
- migration timing for consumers currently using warned noon; and
- later adaptive proof profiles if production cost justifies their complexity.
