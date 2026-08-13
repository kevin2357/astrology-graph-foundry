# Slice 3 — Whole-Artifact Evidence Validation

**Gate status:** Candidate; awaiting human approval

## Outcome

The containing bounded-Natal package schema now applies the standalone evidence
contract to homogeneous evidence-bearing paths. AGF also provides path-aware
discovery for common evidence envelopes inside the deliberately heterogeneous
evidence registry. Malformed evidence no longer passes merely because its parent
container is generic.

## Validation boundary

The aggregate schema composes `bounded_uncertainty_evidence_v1.schema.json` for
body, transform, relationship, terrestrial-frame, calculated-point,
formula-branch, and optional-feature evidence in both the bounded-Natal result and
its uncertainty-assessment mirror. The calculated-point family retains its
supported available branched shape instead of being incorrectly forced into the
common envelope.

The registry cannot safely apply one schema to every value because it contains
common envelopes, legacy wrappers, relationship wrappers, and branched records.
`iter_bounded_evidence_records()` therefore discovers common envelopes by their
contract marker or complete structural signature and yields the precise artifact
path. The structural fallback means a record missing its contract-version marker
is still discovered and rejected by focused standalone validation.

See the [machine-readable validation matrix](whole-artifact-validation-matrix.json).

## QA finding

The stronger package schema exposed placeholder transform evidence in an existing
test fixture that was never a valid common evidence envelope. The fixture was
corrected to use the production evidence constructor. This was a test-data defect,
not a released producer defect, and the regression suite now exercises genuine
contract shapes.

## Verification

- Thirteen whole-package mutation vectors prove unknown availability is rejected
  across every homogeneous evidence family.
- Registry tests prove exact-path discovery for unknown availability and for a
  common envelope missing its contract version.
- Focused bounded-artifact suite: 41 passed.
- Linux candidate wheel installed outside the source checkout: 249 passed.
- Packaged runtime qualification found 39 resources, 10 supported availability
  values, and confirmed aggregate-schema composition.
- Candidate wheel SHA-256:
  `76d7283239aa4a3a3fe74467c2889325ee21709f59aa0766d5c0d2dfcacbabb5`.

## Gate recommendation

Approve the aggregate-schema and heterogeneous-registry boundary. A runtime
dependency on `jsonschema` is unnecessary: package consumers can validate the
homogeneous contract through the shipped schemas, while AGF's lightweight iterator
supplies paths for consumers that inspect heterogeneous registry contents.
