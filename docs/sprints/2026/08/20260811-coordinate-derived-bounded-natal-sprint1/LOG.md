# Coordinate-Derived Bounded Natal Expansion Sprint Log

This log is append-only during execution. Planning entries do not represent
completed implementation slices.

## 2026-08-11 — Planning baseline

- User requested two sequential sprints to pursue fuller exact-Natal feature
  assessment under the invariant-over-the-complete-sampled-range rule.
- Repository start: `C:\dev\github\astrology-graph-foundry` on `main`, tracking
  `origin/main`, at clean committed boundary `00e6c2a` before existing uncommitted
  planning-doc additions.
- Existing uncommitted planning work was preserved: `docs/Near-Term Engineering
  Outlook.md` and its documentation-index link. It predates these sprint skeletons
  and is not implementation evidence.
- Current bounded-Natal evidence: version 0.7.0 candidate, bounded graph 1.0.0,
  minute-resolution evaluation with safety envelopes, invariant body/sign/motion/
  dignity and ordinary aspect promotion, explicit uncertainty evidence, and
  conservative exclusion of terrestrial-frame features.
- Kevin's four-hour Denver example evaluated 241 inclusive minute states, retained
  twelve invariant body placements including the Pisces Moon, and promoted 21
  invariant relationships.
- Planning decision: Sprint 1 covers coordinate-derived features and shared evidence
  infrastructure; Sprint 2 begins only after Sprint 1 closes and covers houses,
  angles, sect, branching lots, optional data, and complete-chart structures.
- No production code, schema, test, package version, tag, release, or downstream
  repository was changed during sprint planning.

## 2026-08-11 — Slice 1 exact-to-bounded parity audit

- Began from approved planning commit `0534c35` on `main`, one commit ahead of
  `origin/main` because the user requested a commit but not a push.
- Audited exact and bounded live calculation, provider configuration, interval
  evaluation, Natal package construction, graph compilation, semantic finalization,
  structural evidence, JSON Schemas, exact fixtures, bounded tests, and capability
  boundaries.
- Produced a machine-readable feature matrix and normalized semantic predicate
  contract for exhaustive exact-chart oracle comparison.
- Confirmed the Sprint 1 boundary covers celestial coordinate paths and accepted
  transforms; houses, angles, sect, branching lots, optional data, and complete-
  chart semantics remain Sprint 2.
- Found that exact triplicity dignity depends on sect, exact `applying_delta` is not
  yet a complete application doctrine, optional Chiron is attempted by default but
  skipped in no-file mode, and exact graph compilation generates relationships
  beyond the raw aspect buckets.
- Full baseline suite passed 214 tests in 25.03 seconds. JSON parsing, changed-
  Markdown relative-link validation, whitespace validation, and `git diff --check`
  passed.
- The first JSON validation command asserted an incorrect expected row count of 31;
  inspection confirmed the valid matrix intentionally contains 32 feature families,
  and the corrected parse check passed. No artifact content changed as a result.
- No production code, schema, package version, or downstream repository was changed.
  Slice remains uncommitted pending Gate 1 approval.

## 2026-08-11 — Slice 2 generalized uncertainty evidence

- Began from approved, committed, and pushed Slice 1 boundary `bbf399f`.
- Added standalone `agf.bounded_uncertainty_evidence.v1.0.0` helpers and packaged
  JSON Schema for scalar ranges, circular/disjoint segments, categorical
  possibilities, prerequisites, transitions, counterexamples, and proof scope.
- Chose additive dual-write migration: legacy bounded evidence fields remain intact,
  and the Bounded Natal Dataset 1.0.0 schema accepts but does not require the new
  contract marker so older saved artifacts remain valid.
- Advanced the bounded calculation profile to 1.1.0 because evidence representation
  changes configuration/output identity. Exact Natal and bounded graph versions are
  unchanged at this slice.
- Integrated generalized longitude, sign, motion, and aspect evidence into real
  interval evaluation while preserving the existing conservative safety envelopes.
- Added deterministic unit/schema/integration tests and compact retained vectors.
- Focused gate suite passed 34 tests after correcting two expected development
  findings: the wrap fixture initially did not actually cross 360°, and the bounded
  calculation-provenance schema needed the approved profile-version advance.
- Targeted lint exposed the bounded artifact's operational `created_at` as a naive
  datetime. Corrected it to an offset-aware UTC timestamp; it remains operational
  envelope metadata and does not enter semantic identity.
- Added an explicit legacy-artifact schema regression: Bounded Natal Dataset 1.0.0
  with calculation profile 1.0.0 and no generalized evidence marker remains valid.
- Targeted Ruff passed. The broad suite passed 221 tests in 22.27 seconds before the
  final retained-vector replay assertion was added.
- Final targeted Ruff and full-suite rerun passed 222 tests in 22.01 seconds.
- Final diff review found the evidence-contract version initially attached to the
  returned source-input provenance rather than the calculation profile. Moved it to
  configuration provenance and added a regression assertion so birth-input identity
  remains independent of evidence serialization policy.
- Post-correction targeted Ruff passed and the full suite passed 222 tests in 25.95
  seconds.
- No downstream repository, release tag, or published artifact was changed. Slice
  remains uncommitted pending final Gate 2 validation and approval.

## 2026-08-11 — Slice 3 rich body coordinate, motion, and dignity evidence

- Began from approved, committed, and pushed Slice 2 boundary `229b8a2`.
- Confirmed Swiss Ephemeris point results already include ecliptic latitude speed;
  the equatorial calculation likewise supplies right-ascension and declination
  speeds. AGF had discarded those fields rather than lacking provider support.
- Exposed latitude speed at the provider boundary and used bounded-only equatorial
  speed extraction so the established exact-Natal serialized contract remains
  unchanged.
- Added conservative speed-enveloped evidence for ecliptic latitude, right
  ascension, declination, and all four available coordinate speeds. Numeric ranges
  remain uncertainty evidence and are never promoted as exact canonical positions.
- Added generalized evidence for all five non-sect-dependent sign-dignity booleans;
  sect-dependent triplicity remains deferred.
- Added feature-local availability and reason fields that distinguish missing
  provider fields, non-finite values, and provider calculation failure. An
  equatorial failure no longer invalidates a valid ecliptic placement.
- Advanced bounded calculation profile 1.1.0 to 1.2.0 because the assessed feature
  set and resulting configuration/output identity changed. Bounded Dataset 1.0.0,
  bounded graph 1.0.0, evidence contract 1.0.0, and exact Natal contracts remain
  unchanged; the provenance schema continues to accept profiles 1.0.0 and 1.1.0.
- Focused tests passed 27 cases after correcting a synthetic dignity fixture that
  unintentionally began on a sign boundary. The full suite passed 224 tests in
  25.80 seconds before final provider-failure-path assertions were added.
- Controlled Linux/Python 3.11 with exact pyswisseph 2.10.3.2, explicit Moshier,
  no external ephemeris files, and optional points disabled evaluated a four-hour
  interval at 241 inclusive minutes. All 12 ordinary bodies had available
  longitude, latitude, right ascension, declination, four speed, motion, sign, and
  dignity evidence; all 132 body evidence records validated against the packaged
  schema. Calculation-only wall time was 1.773 seconds.
- The first two disposable-container harness attempts found harness issues rather
  than product failures: minimal Debian lacked `time`, and source import required
  the currently declared SPC dependency. The corrected harness preserved Docker's
  exit status. The named performance container was removed after measurement.
- With product-owner approval, created reusable local QA image
  `agf-bounded-qa:py311-pyswe-2.10.3.2` (image digest
  `sha256:7adbd0cf756aab8fafc2b3a2f3f5e4785d77b9a0e0d7d4dfa315f2a27e0b2618`).
  It contains Python 3.11, pyswisseph 2.10.3.2, SPC 0.10.0, and test tooling but
  does not bake the changing AGF source tree; later runs mount AGF read/write.
- No downstream repository, release tag, or published artifact was changed. Slice
  remains uncommitted pending final Gate 3 validation and approval.
- Final focused Ruff passed. The final full suite passed 225 tests in 26.25
  seconds. Forty-two schema/result JSON files parsed, 132 live evidence records had
  already validated against the packaged evidence schema, five changed Markdown
  files passed relative-link and trailing-whitespace checks, and `git diff --check`
  passed.
- Reviewed the implementation and documentation diff. Removed both temporary live
  output directories from `C:\tmp`; retained only compact summary, artifact size,
  and SHA-256 evidence. The reusable QA image remains intentionally available for
  later slices.
