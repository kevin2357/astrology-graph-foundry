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

## 2026-08-13 — Slice 2 approval and Slice 3 whole-artifact validation

- Product owner approved Slice 2. Committed and pushed it as `f5bae0f`
  (`Reconcile bounded evidence availability vocabulary`).
- Composed the standalone bounded-evidence schema into the aggregate package schema
  at homogeneous body, transform, relationship, terrestrial-frame,
  calculated-point, formula-branch, and optional-feature paths, including their
  uncertainty-assessment mirrors.
- Preserved the calculated-point available branched record and the heterogeneous
  evidence registry rather than forcing all supported records into one envelope.
- Added `iter_bounded_evidence_records()` to locate common envelopes in that
  registry by contract marker or complete structural signature and return precise
  artifact paths. The signature fallback exposes records whose version marker is
  missing instead of silently skipping them.
- Added thirteen package-mutation vectors covering every homogeneous evidence
  family, plus registry tests for unknown availability and a missing contract
  version.
- Stronger validation exposed an existing transform-test placeholder that was not
  a valid evidence envelope. Replaced it with a production-constructed fixture and
  retained the new regression coverage.
- Added `scripts/qualify_bounded_evidence_schema.py` as an installed-safe resource,
  vocabulary, and schema-composition qualification check.
- The first Docker qualification attempt failed before testing because shell
  quoting mangled inline Python. Replaced the fragile inline probe with the durable
  qualification script.
- Final focused bounded-artifact suite passed 41 tests.
- Built and installed the candidate wheel in the qualified Python 3.11 Linux image
  outside the source checkout. All 249 tests passed; the runtime manifest contained
  39 packaged resources; runtime and schema exposed 10 availability values; and
  aggregate-schema composition was confirmed.
- Candidate wheel SHA-256 was
  `76d7283239aa4a3a3fe74467c2889325ee21709f59aa0766d5c0d2dfcacbabb5`.

## 2026-08-13 — Slice 3 approval and Slice 4 release closure

- Product owner approved Slice 3. Committed and pushed it as `4ca0b7e`
  (`Validate bounded evidence across package artifacts`).
- Selected package version 0.8.1 for the additive evidence-contract repair. Dataset,
  graph, evidence-contract, and calculation-profile versions remain unchanged.
- Updated the runtime version source, version-sensitive tests and qualification,
  README candidate notice, compatibility guidance, and candidate release notes.
- Inspected SPC's active bounded intake read-only. Its 15 focused tests passed, and
  a cross-repository probe proved that all ten AGF-supported availability values
  survive adaptation verbatim while classification remains independently validated.
- SPC's bounded work is not released and its worktree contains owner changes. No SPC
  file was modified, staged, or committed by this sprint.
- Built the AGF 0.8.1 wheel twice under the same controlled source-date epoch; the
  wheels were byte-identical.
- The installed Linux candidate passed all 249 tests, exposed 39 packaged resources
  and 10 availability values, and passed aggregate-schema composition qualification.
- Base mode passed in a clean environment with SPC absent. Live mode passed with SPC
  imports forbidden. Both installed CLIs reported 0.8.1.
- Reproducible candidate wheel SHA-256 was
  `37d7efeb04ced6823c708b1ba09d4fa9a6e4ab29af32aefbcd5fe63116bc2575`.
- A final source-only focused run produced 40 passes plus the expected installed-
  distribution metadata failure because that interpreter had only checkout `src`
  on its path. The same assertion passed within the 249-test installed-wheel run.
- Ruff, machine-readable JSON parsing, and `git diff --check` passed.
- Harness corrections: ran SPC tests from their repository root after an initial
  import-path error; supplied the qualifier's required mode; and used a truly clean
  virtual environment after the QA image's system site packages exposed SPC.
- No tag, release, upload, push, or credential use occurred during Slice 4.
