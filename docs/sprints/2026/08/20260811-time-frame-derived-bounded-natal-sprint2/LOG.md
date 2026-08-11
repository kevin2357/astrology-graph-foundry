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
