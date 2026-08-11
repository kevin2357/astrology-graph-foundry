# Slice 5 — Expanded Coordinate-Derived Relationships

## Outcome

Bounded Natal now assesses aspects involving body, antiscia, contra-antiscia, and
harmonic coordinates, plus declination parallels and contraparallels. Only
complete-interval invariant relationships with retained canonical endpoints enter
bounded graph 1.2.0. All scalar uncertainty stays in evidence.

## Accepted semantics

- Derived longitude aspects use the existing exact aspect angles, configured
  major/minor set, body-name orb policy, and nearest-aspect selection.
- Invariance requires a continuous safety envelope to stay within the allowed orb
  and within the selected aspect's nearest-angle identity region.
- Parallel and contraparallel are independently assessed one-degree predicates;
  both can coexist near zero declination.
- All-sample absence is assessed but retained only as an aggregate count. It is not
  a canonical negative claim.
- Applying/separating, exact strength, exact distance, and scalar orb are withheld
  from canonical bounded relationships.
- Canonical promotion requires both endpoint objects, a single invariant
  relationship type, and a resolvable uncertainty-evidence reference.

## Gate evidence

- Fixtures cover relationship entry/exit, leave-and-return, type stability,
  declination boundary crossing, simultaneous parallel/contraparallel, filtered
  endpoints, evidence references, and absence of precision/application fields.
- The controlled live result promoted 1,374 derived-coordinate aspects, seven
  parallels, and three contraparallels. See the
  [compact live summary](expanded-relationship-live-summary.json).
- The live artifact was 15.7 MB. This is preserved as a structural/selection risk
  for Slice 6 rather than “optimized” by silently dropping valid relationships.
- Focused Ruff and the full 235-test suite passed. Forty-four JSON files parsed,
  the live dataset passed its packaged schema, and `git diff --check` passed.
  Markdown, diff-review, and cleanup evidence is recorded in the sprint log.

## Deferred boundary

Slice 6 must determine which structural summaries, claims, scores, or indexes are
meaningful over this invariant subgraph. Raw derived-relationship count must not be
treated as independent astrological importance.
