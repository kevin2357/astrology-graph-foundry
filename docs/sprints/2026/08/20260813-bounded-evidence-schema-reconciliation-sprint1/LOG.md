# Bounded Evidence Schema Reconciliation Sprint Log

This log is append-only during execution. Planning entries do not represent
completed implementation slices.

## 2026-08-13 — Planning baseline

- Repository began clean on `main` at `1468ba1` (`Record immutable AGF 0.8.0
  release`), synchronized with `origin/main`.
- Triggering downstream finding came from SPC's bounded-format Slice 1 audit: AGF
  emits availability/reason tokens absent from its standalone evidence schema, and
  the containing package schema does not validate every registry record against
  that schema.
- Confirmed standalone `bounded_uncertainty_evidence_v1.schema.json` permits six
  availability values: `available`, `disabled_by_configuration`,
  `unsupported_provider_field`, `missing_provider_field`,
  `nonfinite_provider_value`, and `provider_failure`.
- Confirmed supported bounded-Natal code additionally emits at least `disabled`,
  `unsupported_profile`, `prerequisite_unavailable`, and
  `prerequisite_variable_or_unavailable`.
- Confirmed the aggregate bounded dataset schema leaves `bounded_natal` and most
  uncertainty containers open/generic, so successful package validation does not
  prove every embedded record conforms to the standalone evidence contract.
- Existing tests validate one ordinary standalone record and selected emitted
  values, but do not enforce producer/schema vocabulary closure.
- Accepted interim downstream safety posture is to treat `classification` as the
  epistemic state, preserve `availability` and `status_reason` verbatim, validate
  consumed families individually, and record the mismatch for AGF reconciliation.
- Initial release expectation is AGF 0.8.1 if the fix remains additive and does not
  change calculations or established evidence meaning. This is a planning
  recommendation, not an implemented version decision.
- No source, schema, test, package-version, SPC, tag, or release change was made
  during planning.

## 2026-08-13 — Slice 1 producer and validation-path audit

- Began from clean approved planning commit `d2c2058` on `main`.
- Audited every direct `evidence_record()` producer in `interval_evaluation.py` and
  `live_natal.py`, plus values propagated from provider result fields.
- Confirmed ten currently reachable availability tokens. Six are enumerated by the
  standalone schema and four are emitted but rejected by it. Retained the inventory
  in `results/availability-token-family-matrix.json`.
- Distinguished `status_reason` from availability vocabulary. The schema already
  permits any non-empty string, so prose such as “continuous boundary envelope
  admits adjacent house” is not an enum mismatch and should remain verbatim.
- Found two declared schema tokens with no current bounded-Natal producer:
  `disabled_by_configuration` and `unsupported_provider_field`. They appear to be
  superseded/intended spellings rather than evidence of current output.
- Confirmed provider availability is deliberately propagated by `_coordinate_evidence`
  and `_speed_evidence`. Today the live provider writes only `provider_failure`,
  but the unrestricted propagation path can pass arbitrary future tokens into an
  evidence record. Central vocabulary enforcement is therefore required at the
  producer boundary, not only in direct call sites.
- Mapped bounded evidence surfaces. The aggregate dataset schema validates metadata,
  provenance, and canonical/structural graphs, but leaves `bounded_natal`, most of
  `uncertainty_assessment`, and `evidence_registry` records generic. The registry is
  heterogeneous: some values are common evidence envelopes; other values are
  legacy body/aspect wrappers, branched calculated-point records, or relationship
  wrappers. Blindly applying the standalone schema to every registry value would
  incorrectly reject supported shapes.
- Added a temporary characterization regression proving all six declared tokens
  validate and all four additional producer tokens fail the 0.8.0 standalone
  schema. Slice 2 must replace this mismatch expectation with vocabulary-closure
  assertions.
- The first focused invocation used a bundled Python without the checkout on its
  import path and failed during collection with `ModuleNotFoundError`; no tests ran.
  Rerunning with the repository `src` on `PYTHONPATH` passed 19 focused evidence and
  bounded-artifact tests in 0.90 seconds.
- Machine-readable audit JSON parsed successfully and `git diff --check` passed.
- No production implementation or schema was changed in Slice 1.

## 2026-08-13 — Slice 1 approval and Slice 2 canonical vocabulary

- Product owner approved Slice 1. Committed and pushed it as `bf70a78` (`Audit
  bounded evidence schema drift`).
- Adopted the eight released producer values as the canonical availability
  vocabulary. Retained the two earlier schema-only spellings as accepted
  compatibility aliases so reconciliation broadens rather than narrows the 1.0.0
  evidence contract.
- Added `EvidenceAvailability`, `CANONICAL_AVAILABILITY_VALUES`,
  `COMPATIBILITY_AVAILABILITY_ALIASES`, and `SUPPORTED_AVAILABILITY_VALUES` to the
  common evidence module.
- The common `evidence_record()` boundary now rejects unregistered availability
  values before serialization. This also closes the dynamic provider-propagation
  path identified in Slice 1.
- Expanded the standalone JSON Schema enum to exactly match the supported runtime
  vocabulary. Evidence contract version remains 1.0.0 because existing artifacts
  retain their meaning and previously declared values remain valid.
- Replaced the transitional mismatch test with closure tests proving runtime/schema
  equality, acceptance of all supported values, rejection of unknown values, and
  representative independence of classification and availability.
- Updated the bounded calculation contract and consumer handoff to distinguish
  classification, availability, and free-form status reason.
- Focused evidence, interval, terrestrial-frame, and bounded-artifact suite passed:
  59 tests in 4.41 seconds.
- Full source suite ran 234 tests: 233 passed and the installed-distribution metadata
  test could not find package metadata because the bundled Python used only the
  checkout `src` path. This is an environment-only installed-boundary assertion;
  Slice 3's wheel qualification will run it from an installed artifact.
- Focused Ruff import/error checks and `git diff --check` passed.
