# Time-Frame and Derived-Structure Bounded Natal Expansion Sprint Log

This log is append-only during execution. Planning entries do not represent
completed implementation slices.

## 2026-08-11 — Planning baseline

- User requested a second sequential sprint for the more complex exact-Natal
  features after a coordinate-derived bounded-Natal expansion.
- Repository planning boundary is AGF `main` at commit `00e6c2a`, with separate
  uncommitted planning-document additions preserved.
- Entry status: blocked on successful completion and commit of
  `20260811-coordinate-derived-bounded-natal-sprint1`.
- Current implementation conservatively marks houses, house placements, angles,
  sect, lots, and related features unavailable. This is a scoped v1 contract, not a
  finding that invariance is impossible.
- Planning premise: calculate the ordinary exact feature at every allowed instant,
  compare normalized semantic predicates, promote the complete-domain intersection,
  and retain ranges, possibilities, prerequisites, transitions, and failures as
  evidence.
- Primary risks identified: moving cusp topology, house-system/polar failures,
  circular and disconnected ranges, sect formula branching, optional external-data
  provenance, and ambiguity between complete-candidate-chart scores and
  invariant-subgraph scores.
- No implementation slice has begun. No production code, schema, test, package
  version, tag, release, or downstream repository was changed during planning.

## 2026-08-11 — Pre-sprint decoupling slice added for review

- AGF 0.7.0 was published and download-verified at immutable source commit
  `8926483b38c6b5c6fd33748aa190d330bba4cd5b`; post-publication documentation is on
  `main` at `eacd34d`.
- At product-owner request, added runtime/ownership decoupling as the new Slice 1
  and renumbered the terrestrial-frame work to Slices 2–9. No decoupling code has
  been implemented.
- Read-only audit confirmed the coupling is broader than the mandatory
  `pyproject.toml` requirement. AGF package initialization exports static projection
  functions, `cli.py` imports SPC exceptions and owns `astro-package project`,
  `doctor` owns an SPC projection-readiness mode, and Synastry analysis
  materialization invokes the AGF projection adapter directly.
- The temporal source adapter is not itself evidence of improper runtime coupling:
  it builds a projection-neutral serialized handoff without importing SPC. Slice 1
  must preserve that AGF-owned source contract while removing projection execution.
- The preferred contract is no mandatory or optional AGF-to-SPC dependency. Exact
  wheel compatibility remains valuable, but belongs in an external integration
  harness that installs the artifacts independently and exchanges serialized
  packages.
- Public Python exports, the `project` CLI command, projection doctor mode, and the
  projection-derived Synastry compact view make this a likely AGF 0.8.0 API break,
  not a packaging-only patch. The gate requires an explicit migration rather than
  silently replacing projected rows with legacy theme inference.
- Cross-repository work remains read-only and separately approved. This planning
  update changes no production code, schema, package version, tag, release, or
  downstream repository.

## 2026-08-11 — Decoupling moved to a separate Sprint 3

- Product owner decided the discovered projection/Synastry/API migration surface is
  too substantial to place in front of the terrestrial bounded-Natal experiment.
- Restored this plan to its original eight terrestrial-frame and derived-structure
  slices. AGF/SPC decoupling is no longer an entry gate or exit criterion here.
- Preserved the read-only audit findings in the append-only history and moved their
  actionable contract into
  `../20260811-agf-spc-decoupling-sprint3/PLAN.md` as that sprint's first slice.
- No implementation, package, schema, test, release, or downstream repository was
  changed during this planning correction.

## 2026-08-11 — Slice 1 terrestrial-frame audit

- Began from clean synchronized `main` at `a7e2bba`; AGF 0.7.0 remains the
  immutable entry baseline.
- Audited configuration and CLI surfaces, exact `house_data`, circular
  `house_for_lon`, sect/lot dependencies, bounded dispositions, provenance, tests,
  and the prior parity matrix.
- Reviewed primary Swiss Ephemeris documentation and confirmed pinned pyswisseph
  2.10.03 exposes `houses_ex2` cusp/angle speeds.
- Ran the reproducible probe in Linux image
  `agf-bounded-qa:py311-pyswe-2.10.3.2` at digest
  `sha256:7adbd0cf756aab8fafc2b3a2f3f5e4785d77b9a0e0d7d4dfa315f2a27e0b2618`.
- Confirmed Placidus and Koch errors at tested polar latitudes and successful Whole
  Sign calculation through latitude 89.9 degrees.
- Found an exact-path defect: `house_data` rotates numbered cusps toward the
  Ascendant, corrupting systems where cusp 1 is intentionally distinct.
- Found an input/provenance defect: unrecognized code `Z` silently behaves like
  Placidus while AGF records `Z` as configured.
- Recommended initial bounded systems `P` and `W`; all others require individual
  qualification. Gauquelin is excluded from the twelve-house contract.
- Defined family-scoped failure, no fallback, half-open circular assignment, smooth
  speed-envelope, and Whole Sign ingress policies without changing Sprint 1's
  uncertainty contract.
- No runtime code, schema, version, downstream repository, tag, or release changed.
  Exact-path fixes and executable regressions open Slice 2 after Gate 1 approval.
