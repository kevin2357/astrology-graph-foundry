# Slice 1 — Producer and Validation-Path Audit

**Gate status:** Candidate; awaiting human approval

## Outcome

The SPC finding is reproduced and bounded precisely. AGF 0.8.0 has a closed
standalone availability enum that rejects four values emitted by supported
bounded-Natal paths. Aggregate package validation does not expose the defect because
it does not apply the common evidence schema to embedded records.

## Token findings

Current bounded-Natal producers can emit eight observed values:

- schema-valid: `available`, `missing_provider_field`,
  `nonfinite_provider_value`, and `provider_failure`;
- schema-invalid: `disabled`, `unsupported_profile`,
  `prerequisite_unavailable`, and
  `prerequisite_variable_or_unavailable`.

The schema additionally declares `disabled_by_configuration` and
`unsupported_provider_field`, neither of which has a current producer. Slice 2 must
decide whether these are retained aliases, deprecated unused spellings, or replaced
by the released implementation vocabulary.

Provider-field availability is dynamically propagated. Although the current live
provider writes only `provider_failure`, the producer boundary does not constrain a
future value before constructing evidence. Vocabulary enforcement must therefore
be centralized rather than inferred only from literal call sites.

## Validation findings

The evidence registry is not homogeneous. It contains common evidence envelopes,
body aggregates, aspect/relationship wrappers, branched calculated-point records,
and nested evidence. Applying the standalone schema blindly to every registry value
would be incorrect. The fix should combine direct `$ref` composition at homogeneous
paths with an AGF-owned path-aware validator for mixed legacy structures.

`status_reason` is already an unrestricted non-empty string. The varied prose
reason values reported by SPC are expected and should remain preserved verbatim;
the closed-vocabulary defect concerns `availability`.

## Evidence

- [Availability token/family matrix](availability-token-family-matrix.json)
- [Validation-path map](validation-path-map.json)

A focused characterization test now proves the exact released mismatch. It is
intentionally transitional: Slice 2 must replace the “these producer values fail”
expectation with producer/schema closure.

## Gate recommendation

Proceed with an additive vocabulary centered on released producer semantics. Do not
collapse prerequisite state into generic unavailability, and do not rewrite status
reasons. Review the two unused schema spellings explicitly before implementation.
