# Slice 2 - Generalized Uncertainty Evidence Primitives

**Status:** Gate candidate; uncommitted

**Starting boundary:** `bbf399f`

## Outcome

AGF now has a reusable, versioned uncertainty-evidence envelope for the richer
coordinate-derived work in later slices. Existing bounded fields remain intact;
new generated assessments dual-write structured circular/scalar ranges,
possibilities, prerequisites, transition witnesses, counterexamples, and proof
scope.

The contract is `agf.bounded_uncertainty_evidence.v1.0.0`, packaged as
`bounded_uncertainty_evidence_v1.schema.json`.

## Compatibility and version decision

This slice does not replace Bounded Natal Dataset 1.0.0 or bounded canonical graph
1.0.0. The dataset schema accepts the new top-level
`uncertainty_assessment.evidence_contract_version` additively and continues to
validate older saved artifacts that lack it. Existing body/aspect evidence fields
are unchanged.

The bounded calculation profile advances from 1.0.0 to 1.1.0 because evidence
representation affects configuration/output identity. The evidence contract begins
at its own 1.0.0 version. Exact Natal versions and behavior are unchanged. Final AGF
package/version selection remains a later sprint gate.

## Implemented primitives

- Finite ordered scalar closed ranges, optionally retaining observed bounds inside
  the conservative proof range.
- Circular closed segment sets with origin-wrap, unwrapped-envelope, and full-circle
  coverage semantics.
- Deterministically sorted unique categorical possibility sets.
- Deterministically sorted unique prerequisite references.
- Adjacent sampled transition witnesses with coordinate intervals.
- Compact bounded counterexamples showing why a proposed invariant was withheld.
- Common feature identity, classification, value kind, and proof-scope envelope.

Reference vectors:
[`uncertainty-evidence-vectors.json`](uncertainty-evidence-vectors.json).

## Integration behavior

Current interval results now add three generalized records per successfully assessed
body—longitude, sign, and motion—and one per body-pair aspect. Legacy
`longitude_range`, `motion`, `sign_dignity`, `possible_aspects`, and `orb_range`
remain authoritative compatibility fields during migration.

Body sign/motion and aspect transitions record observed adjacent-state changes.
Counterexamples are compact witnesses, not distributions or probabilities. The
conservative range/safety envelope remains the proof authority where it is broader
than observed samples.

Inconclusive whole-run results advertise the evidence contract version while
retaining the established failure representation. Per-feature generalized
inconclusive records will expand as later slices isolate additional feature-family
failures.

## Safety findings

- A longitude range is normally classified `variable` as a scalar value even when
  its containing sign is invariant. This prevents “bounded but invariant” from being
  misread as an exact longitude.
- Circular segment sets preserve a 359°–1° possibility without widening it to most
  of the zodiac.
- Transition witnesses demonstrate observed changes but never replace continuous
  safety envelopes.
- Empty counterexamples do not independently prove invariance; classification and
  range proof remain authoritative.
- Generalized evidence is nested rather than replacing legacy fields, preventing a
  silent saved-artifact migration break.

## Verification

Focused evidence, interval, bounded-artifact, calculation-provenance, and packaged-
resource tests pass. Targeted Ruff passed. The final post-review full source suite
passed **222 tests in 25.95 seconds**, including retained-vector replay, provenance
placement, and legacy-artifact schema
compatibility. All changed JSON parses, relative Markdown links resolve, no trailing
whitespace was found, and `git diff --check` passes.
