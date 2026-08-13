# Bounded Natal Consumer Handoff

**Status:** Published AGF 0.7.0 baseline plus unreleased post-0.7 bounded expansion;
downstream enablement pending

## What the API supplies

The caller supplies ordinary descriptive/location fields plus exactly one time
basis: exact `birth_local`; bounded `birth_local_earliest` and
`birth_local_latest`; or `birth_time_unknown=true` with `birth_date`.

All modes require an IANA timezone and calculation coordinates. Production callers
should provide opaque stable `source_chart_id`; changing display name must not change
chart lineage. Bounds are local wall datetimes without offsets. AGF validates zone
resolution, rejects DST gaps/ambiguous folds, normalizes UTC bounds, and enforces the
48-elapsed-hour maximum.

The API owns product eligibility, acknowledgement, immutable birth-data versions,
orchestration, persistence, and reader-facing warnings. It must not turn missing
time into noon before calling bounded mode.

## Artifact and cache identity

Persist bounded packages immutably. Cache/idempotency identity must include the
normalized source-input hash, bounded configuration hash, AGF artifact identity,
all bounded contract/profile versions, and qualified provider/runtime identity.

Display name and location label do not determine geometry. Correcting bounds changes
source-input/calculation identity and creates a new immutable artifact; it does not
automatically change caller-owned `source_chart_id`. The persistence owner hashes the
exact serialized bytes because operational `created_at` belongs to that envelope.

## Downstream consumption

The canonical graph contains only invariant categorical body and aspect facts.
Longitude, ecliptic latitude, right ascension, declination, available coordinate
speeds, and orb ranges live in `uncertainty_assessment.evidence_registry` and are
referenced by canonical rows. Consumers may filter canonical rows while retaining
evidence references and provenance. They must not convert a range endpoint or
midpoint into an exact placement. Coordinate evidence also distinguishes missing or
non-finite provider fields from provider calculation failure.

Bounded canonical graph 1.1.0 adds bounded antiscia, contra-antiscia, and harmonic
derived objects plus explicit owner-lineage relationships. These rows assert only
an invariant transformed sign. Consumers must not interpret their familiar
astrological transform names as evidence that an exact transformed longitude is
present. Graph 1.0.0 remains valid and contains only the original bounded body and
aspect vocabulary.

Graph 1.2.0 adds invariant relationships involving bounded transform objects and
invariant declination parallels/contraparallels. These relationships intentionally
omit orb, strength, distance, and applying/separating scalars. Their evidence
registry rows retain bounded orb ranges, transitions, alternatives, and coordinate
prerequisites. A counted invariant absence is not a canonical negative claim.

Graph 1.3.0 and its structural evidence explicitly describe the retained invariant
subgraph. It supplies deterministic indexes and topology/family counts, but no
structural-strength scores or canonical claims. Downstream systems must not rank or
claim by raw row count: use root-owner `evidence_family_group` lineage when applying
anti-double-counting policy.

The current unreleased source extends that family through graph 1.7.0. Versions
1.4–1.7 add invariant body/point house membership, cusp and angle semantics,
angle relationships, sect and triplicity, Vertex house evidence, and branched
Fortune/Spirit evidence and invariant relationships. Calculation profile 1.12.0
records these policies and explicit optional external-feature dispositions. Dataset
and uncertainty-evidence contract versions remain 1.0.0.

Complete-chart output continues to mean the retained invariant subgraph. Aspect
patterns, dispositorship networks, elemental/modal balance, bounded structural
scores, and canonical claims are not inferred from candidate-chart samples or raw
row counts. Deterministic indexes and counts are navigation/topology aids only.

Published 0.7.0 artifacts additionally advertise
`agf.bounded_uncertainty_evidence.v1.0.0`. Its circular segment sets,
prerequisites, transition witnesses, and counterexamples are additive to the legacy
bounded evidence fields. Consumers must feature-detect this version and preserve
unknown evidence members; absence means an older bounded artifact, not malformed
uncertainty.

Within each generalized evidence envelope, treat `classification` as the epistemic
state. `availability` separately explains whether the calculation path was
available, disabled, unsupported, missing a prerequisite, or failed. Do not infer
one from the other: `prerequisite_variable_or_unavailable`, for example, can
accompany either a variable or unavailable classification. Preserve `status_reason`
verbatim as open explanatory text. AGF 0.8.1 reconciliation accepts the two earlier
schema-only compatibility spellings while current producers emit the canonical
vocabulary documented in the calculation contract.

SPC 0.10.0 supports exact canonical graph 1.3.0 only. AGF rejects bounded static
projection before constructing an SPC request. SPC needs a bounded-vocabulary sprint.
SBE consumes projected artifacts, so its bounded eligibility/authoring sprint follows
the SPC contract instead of consuming AGF canonical artifacts directly.

Current Transit, returns, profections, eclipse target activation, Synastry,
Composite, and Davison paths reject bounded packages. Those failures are intentional
capability boundaries, not transient provider errors.

## Migration from warned noon

A historical warned-noon exact chart is not a bounded chart. Do not relabel it.
Recalculate from the original date/time knowledge with `unknown_time` or honest
caller bounds, retain the old artifact for audit, and let product policy decide
whether dependent readings are superseded.

## Error classification

- Invalid modes, timezone resolution, coordinates, duration, schema, and downstream
  compatibility are terminal until request/policy changes.
- Provider failure, non-finite point data, and proof-budget exhaustion are
  calculation failures/inconclusive proof, not ordinary variable astrology.
- A complete artifact with variable or conditional facts is successful;
  uncertainty is expected output, not partial calculation.

## Release posture

AGF 0.7.0 adds a public package, graph, provenance, and CLI family while preserving
exact contracts. Its publication does not imply AstroWoof end-to-end readiness;
SPC, SBE, API, and frontend acceptance remain separately qualified work.

The post-0.7 expansion is not yet released. Its recommended release line is 0.8.0
because the additional bounded graph vocabulary and calculation semantics are a
material additive public capability. Publication waits for downstream review and
separate authorization.
