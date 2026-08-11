# Slice 6 — Invariant-Subgraph Structural Material

## Outcome

Bounded graph 1.3.0 exposes deterministic structural material only under an explicit
`bounded_invariant_subgraph` basis. It retains indexes, topology counts, evidence
tiers, derivation families, and root-owner family groups, while withholding scores
and claims whose semantics would not survive the exact-to-bounded transition.

## Accepted structures

- Object and relationship indexes are deterministic conveniences over retained
  canonical rows.
- Counts by type describe the invariant subgraph, not every complete candidate
  chart and not an average across candidates.
- Record independence identifies serialized rows. Evidence-family independence
  collapses shared source-body owners and is the anti-double-counting unit.
- Bounded bodies are core/direct evidence. Bounded antiscia and harmonic objects are
  derived evidence under their matching tiers. Declination relationships remain
  supplemental direct relationships.

## Withheld structures

- Structural-strength scores are unavailable. Missing exact orb cannot be replaced
  by the shared heuristic's generic fallback.
- Canonical or orthodox claims are not emitted from bounded topology.
- Raw record count is not salience, confidence, consensus, or independent support.
- No exact-chart score is reused under an invariant-subgraph label.

## Gate evidence

- Tests distinguish a sampled complete assessment from its smaller invariant
  subgraph, validate indexes and lineage, prove absence of scores/claims, and prove
  repeated finalization remains idempotent.
- The controlled live graph collapsed 1,598 retained rows into 525 root-owner
  evidence families. See the
  [compact structural summary](invariant-subgraph-structural-summary.json).
- Focused Ruff and the full 236-test suite passed. Forty-five JSON files parsed,
  the live dataset passed its packaged schema, and `git diff --check` passed.
  Markdown, diff-review, and cleanup evidence is recorded in the sprint log.

## Deferred boundary

Downstream projection, selection, and authorship decide how to use these families.
AGF supplies source topology and anti-double-counting lineage but does not assign
product importance or narrative weight.
