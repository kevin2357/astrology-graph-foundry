# Slice 2 — Canonical Vocabulary and Standalone Contract

**Gate status:** Candidate; awaiting human approval

## Outcome

AGF now has one centralized bounded-evidence availability vocabulary shared by its
runtime construction boundary and standalone JSON Schema. Every currently emitted
value validates, unknown values fail before serialization, and the released
semantic distinctions remain intact.

## Vocabulary decision

The canonical vocabulary follows AGF 0.8.0 producer behavior:

- `available`
- `disabled`
- `missing_provider_field`
- `nonfinite_provider_value`
- `prerequisite_unavailable`
- `prerequisite_variable_or_unavailable`
- `provider_failure`
- `unsupported_profile`

The schema-only values `disabled_by_configuration` and
`unsupported_provider_field` remain accepted compatibility aliases. Current
producers do not emit them. Retaining them avoids invalidating any external artifact
that followed the published standalone schema, while documentation directs new
producers to the canonical values.

See the [machine-readable vocabulary](canonical-availability-vocabulary.json).

## Contract semantics

`classification` remains the epistemic state. `availability` describes the state of
the configured calculation path and its prerequisites. `status_reason` remains open
explanatory text. No inference from availability to classification is safe;
`prerequisite_variable_or_unavailable` can accompany either `variable` or
`unavailable` depending on the derived feature's remaining possibility set.

The evidence contract stays at `agf.bounded_uncertainty_evidence.v1.0.0`. The schema
change is additive, existing meanings are unchanged, and both previously accepted
schema values remain accepted. Package version recommendation remains 0.8.1.

## Enforcement and tests

The common evidence constructor validates availability against the centralized set.
This protects direct producers and provider-field propagation alike. Tests prove:

- runtime and schema sets are identical;
- all canonical and compatibility values validate;
- an unknown value raises before artifact construction; and
- representative classification/availability combinations validate independently.

Focused contract suite: 59 passed. The full source suite produced 233 passes plus
one expected installed-metadata failure in a source-only bundled Python. Installed
wheel validation is intentionally Gate 3 work.

## Gate recommendation

Approve the additive vocabulary and compatibility-alias policy, then proceed to
whole-artifact path-aware validation. No producer token migration is needed.
