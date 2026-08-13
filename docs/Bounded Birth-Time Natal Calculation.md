# Bounded Birth-Time Natal Calculation

**Status:** Published in Astrology Graph Foundry 0.7.0

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

The 0.7.0 release implements the Python/CLI input, interval evaluation, schemas,
canonical graph, uncertainty evidence, provenance, capabilities, and exact-only
consumer rejections described here. SPC and SBE support remains a separate follow-on
sprint. The published 0.7.0 wheel is the first immutable bounded-Natal release.

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

The 0.7.0 release conservatively assesses:

- bounded longitude ranges for ordinary configured bodies;
- bounded ecliptic-latitude, right-ascension, and declination ranges;
- bounded ranges for the longitude, latitude, right-ascension, and declination
  speeds returned by Swiss Ephemeris;
- antiscia, contra-antiscia, and configured harmonic longitude ranges, with
  invariant transformed signs promoted as explicitly bounded derived objects;
- invariant versus possible zodiac signs;
- invariant versus variable motion state;
- sign-dependent dignity only when its inputs are invariant; and
- ordinary body-to-body aspects as invariant, conditional, or absent throughout the
  interval, with bounded orb evidence where supportable.

Current unreleased source additionally assesses cusp and angle ranges, invariant
house membership, cusp signs/rulers, angle signs/relationships, sect/triplicity,
Vertex house membership, and branched Fortune/Spirit ranges and relationships. The
published 0.7.0 artifact does not contain those post-release additions.

Still unavailable are unqualified external-data objects, applying/separating
semantics, bounded structural scores and patterns, canonical claims, and downstream
operations requiring one exact natal longitude unless a separately reviewed bounded
operation exists. This preserves the conservative certainty rule while expanding
the set of predicates AGF can actually prove.

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

AGF 0.8.0 formalizes
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

Coordinate evidence records whether the provider field was available, missing,
non-finite, or failed calculation. A failed equatorial calculation therefore makes
right ascension and declination inconclusive without erasing an otherwise valid
ecliptic placement. Numeric ranges remain evidence and are not promoted as exact
canonical coordinates.

Evidence has three separate descriptive axes:

- `classification` is the epistemic result across the complete interval:
  invariant, conditional, variable, unavailable, or inconclusive;
- `availability` describes the calculation path or prerequisite state and never
  overrides classification; and
- `status_reason` is open explanatory text that consumers preserve verbatim.

Canonical availability values are `available`, `disabled`,
`missing_provider_field`, `nonfinite_provider_value`,
`prerequisite_unavailable`, `prerequisite_variable_or_unavailable`,
`provider_failure`, and `unsupported_profile`. The earlier schema-only spellings
`disabled_by_configuration` and `unsupported_provider_field` remain accepted as
compatibility aliases but are not emitted by current AGF producers. Unknown tokens
are rejected at the common evidence-construction boundary so implementation and
packaged schema cannot drift silently.

The bounded package schema composes the standalone evidence schema at homogeneous
evidence-bearing paths. The evidence registry itself remains heterogeneous, so it
is not correct to validate every registry value as a common evidence envelope.
`iter_bounded_evidence_records()` discovers common envelopes by their contract
marker or complete structural signature and reports each artifact path for focused
validation and diagnostics.

Antiscia and harmonic transforms operate on the conservative source-longitude proof
envelope, not a midpoint. Circular origin crossings become ordered segment sets;
when harmonic multiplication covers 360 degrees or more, evidence records
full-circle coverage and no sign is promoted. Derived graph objects retain their
source-body owner reference and contain a sign index but no exact target longitude.

Bounded canonical graph 1.3.0 can also promote invariant aspects whose endpoints
are retained body or transformed objects, plus invariant declination parallels and
contraparallels between retained bodies. Relationship orb ranges remain evidence;
the canonical relationship carries only the invariant type and resolvable endpoints.
Pairs with no relationship throughout the interval are counted compactly rather
than expanded into thousands of negative evidence rows.

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

Applying/separating is not currently promoted in bounded mode. The exact artifact's
`applying_delta` is instantaneous signed geometry, not by itself proof that one
application state persists throughout an uncertain birth interval.

### Structural material

Bounded canonical graph 1.3.0 labels all summaries as
`bounded_invariant_subgraph`. Deterministic indexes, counts by object/relationship
type, evidence tiers, derivation families, and root-owner evidence-family groups are
available. Raw record counts are not independence weights.

AGF emits no bounded structural-strength score or canonical claim. The shared exact
score heuristic depends partly on exact orb and complete-chart interpretation; its
fallback for missing orb is not meaningful evidence for a bounded relationship.
Consumers should use evidence-family grouping to prevent repeated harmonics and
owner-derived structures from being counted as independent source facts.

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
Moshier evidence for the original longitude-only evaluator measured approximately
0.70 seconds for 24 hours and 1.27 seconds for the maximum 48 hours. A Slice 3
four-hour run including ecliptic and equatorial coordinates and speeds completed in
1.77 seconds. Final installed-wheel qualification completed four-hour, 24-hour, and
maximum 48-hour Moshier artifacts in approximately 8, 36, and 65 wall-clock seconds
respectively after coordinate-derived transforms, relationships, evidence, and
structural material were enabled. Runtime depends on profile and hardware; these
figures are qualification observations, not an API service-level guarantee.

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

### Optional external-data features

The bounded no-file profile evaluates only the twelve core bodies. Chiron,
asteroids, and fixed stars are not silently attempted or fallback-calculated.
Whether requested or disabled, each family receives an explicit evidence record:
`unsupported_profile` when requested without a qualified external-data profile and
`disabled` when excluded by configuration. Request flags, asteroid IDs, and fixed-
star names participate in the configuration hash; the machine-local ephemeris path
does not.

No external-data-backed bounded profile is currently qualified. A future profile
must pin the Swiss Ephemeris wrapper and every `.se1` or catalog resource by content
hash, define supported date coverage, prove requested-versus-observed provider
behavior, and version the calculation profile. The existing Moshier/no-file profile
remains valid and does not acquire an external-file dependency.

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
profile 1.0.0. The published 0.7.0 release emits bounded graph 1.3.0,
`agf.bounded_uncertainty_evidence.v1.0.0`, and bounded calculation profile 1.5.0;
earlier graph/profile versions remain accepted where their schemas declare them.

The current unreleased parity-complete source emits bounded graph 1.7.0 and bounded
calculation profile 1.12.0. The recommended package release is 0.8.0; published
0.7.0 remains the immutable baseline until separately authorized publication.

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
