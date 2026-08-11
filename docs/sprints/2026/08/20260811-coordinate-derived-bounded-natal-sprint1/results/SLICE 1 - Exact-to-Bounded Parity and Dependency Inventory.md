# Slice 1 - Exact-to-Bounded Parity and Dependency Inventory

**Status:** Gate candidate; uncommitted

**Starting boundary:** `0534c35`

## Outcome

The exact Natal surface is inventoried in 32 feature-family entries against bounded
Natal and divided into a reviewable coordinate-derived Sprint 1 boundary and
terrestrial/branching Sprint 2 boundary. The machine-readable matrix also defines
the normalized semantic predicate contract that exhaustive exact-chart fixtures
will use as the correctness oracle.

Primary evidence:
[`exact-to-bounded-parity-matrix.json`](exact-to-bounded-parity-matrix.json).

## Architectural findings

Exact Natal is not one flat calculation result. Its output layers include raw chart
facts, promoted graph objects, generated graph relationships, canonical boundary
annotations, structural evidence, projection views, claims, and exact-only timing
capabilities. Bounded parity must be assessed at each layer rather than copying raw
fields into a smaller graph.

Sprint 1 can safely own features computed from celestial coordinate paths and
versioned transforms: richer body coordinates, declination, antiscia, harmonics,
ordinary and derived coordinate relationships, and structural material explicitly
scoped to the invariant subgraph.

Sprint 2 must own houses, angles, body-house membership, cusp rulership, sect,
sect-dependent triplicity, lots, Vertex, angle relationships, optional-data
profiles, and complete-chart structures whose meaning depends on those features.

## Important corrections and surprises

### Dignity is not one dependency family

The existing bounded artifact correctly retains domicile, exaltation, detriment,
and fall from invariant sign. Exact `dignity_for`, however, also selects a
triplicity ruler using `day_birth`. Triplicity therefore remains Sprint 2 and may not
be promoted merely because the body's sign is invariant.

### Exact applying data is not yet a settled applying/separating contract

Exact aspects expose `applying_delta`, which is a signed geometric delta. It is not
by itself a reviewed traditional application algorithm using relative motion.
Sprint 1 may preserve a range or adopt an explicitly defined category, but must not
rename the current scalar as authoritative applying/separating semantics.

### Optional points are not ordinary no-file baseline bodies

`include_optional_points` defaults true and attempts Chiron, but the provider skips
it when required Swiss Ephemeris data is absent. Asteroids and fixed stars have
similar external-data concerns. They belong to an optional qualified profile in
Sprint 2, not the deterministic Moshier/no-file Sprint 1 baseline.

### Exact graph generation broadens the relationship surface

After raw exact aspects are calculated, graph compilation generates aspects among
all longitude-bearing objects, including derived points and lots, and retains some
legacy longitude-only antiscia/harmonic relationships. Bounded parity must define
invariant semantic relationships directly; it cannot reuse rows containing exact
`target_longitude` values.

### Structural evidence needs an explicit scope label

The structural-evidence graph mostly aggregates canonical evidence lineage and
operator families. It can be produced for an invariant bounded graph, but its counts
describe that invariant subgraph—not every complete candidate chart. Existing
mechanical `structural_strength_score` assignment also needs semantic review before
being treated as parity.

## Normalized oracle contract

The oracle intersects normalized semantic predicates, never complete JSON rows.
Predicate identity includes feature kind, stable source endpoints, categorical
value, relevant configuration/profile identity, and prerequisites. It excludes
display names, timestamps, pretty strings, sampled indices, filesystem paths,
projection context, and exact scalars not explicitly modeled as ranges.

A predicate promotes only if its meaning is identical in every valid state and
continuous-safety evidence does not permit an unobserved transition. A non-promoted
predicate is not false: alternatives, ranges, transitions, and counterexamples stay
in uncertainty evidence. Missing or failed prerequisites make only the affected
feature family inconclusive where safe isolation is possible.

## Version impact at this gate

No version is selected in Slice 1. Generalized range schemas and new public graph
vocabulary will likely require new bounded package/graph/evidence profile versions
and an AGF minor release. Exact Natal package 1.1.0 and canonical graph 1.3.0 should
remain unchanged unless later implementation evidence proves otherwise.

## Verification

- Full source suite: **214 passed in 25.03 seconds**.
- Machine-readable parity matrix parses as JSON with 32 feature-family entries.
- Changed Markdown relative-link validation: zero broken links.
- Markdown whitespace and `git diff --check`: passed.
- Repository diff and status reviewed; only Sprint 1 documentation is new or
  modified after the approved planning boundary.

## Gate assessment

Gate 1 is ready for human review. No production implementation, schema, package
version, or downstream repository has changed in this slice.
