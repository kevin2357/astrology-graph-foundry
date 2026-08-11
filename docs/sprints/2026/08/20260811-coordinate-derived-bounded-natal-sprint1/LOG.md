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
