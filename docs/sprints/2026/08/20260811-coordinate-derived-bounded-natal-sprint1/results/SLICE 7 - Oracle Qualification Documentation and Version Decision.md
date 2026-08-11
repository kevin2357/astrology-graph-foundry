# Slice 7 — Oracle Qualification, Documentation, and Version Decision

## Outcome

The coordinate-derived bounded-Natal expansion is qualified as the existing AGF
0.7.0 release candidate. A clean wheel installed outside the checkout passed the
full suite and all runtime doctor modes under Linux/CPython 3.11 with pinned SPC and
pyswisseph. Controlled Moshier calculations completed at four, 24, and the maximum
48 hours with no failures and validated against schemas loaded from the wheel.

## Oracle and determinism evidence

- A normalized exact-minute oracle now covers 4/24/48-hour domains for body signs,
  motion, harmonic signs, ordinary aspects, and declination relationships.
- The first oracle draft deliberately exposed a tolerance-boundary distinction:
  the continuous safety envelope may retain both adjacent categories where raw
  point values land exactly on one boundary. The final equivalence vector is away
  from boundaries; dedicated tests retain boundary-conservative behavior.
- Two independent four-hour live invocations differed only in operational
  `metadata.created_at`. Removing that field produced the same canonicalized
  semantic SHA-256, `095855f8099c023058bf0468553addd979d591c6ce70a13d8cb50909b6169346`.
- The [oracle qualification summary](oracle-qualification-summary.json) retains the
  live artifact hashes, sizes, counts, classifications, and replay boundary.

## Installed package evidence

The clean wheel was built from the committed `39e351c` boundary and imported from
`/usr/local/lib/python3.11/site-packages`, not the mounted checkout. The wheel
contains 39 schemas and both console-entry metadata and licensing/record material.
The installed runtime manifest has SHA-256
`3cb122e5febdcf80dea752813f3acf0e5907488b223032128866ce65e47a9022`.

All 236 pre-Slice-7 tests passed against the installed artifact. Saved, projection,
and live doctor assertions passed; both console entry points reported version
0.7.0. The three new normalized-oracle cases also passed against installed code.
See the [installed-wheel qualification](installed-wheel-qualification.json).

## Live qualification interpretation

Longer intervals correctly retain fewer invariant canonical rows and more
conditional/variable evidence. The 48-hour maximum evaluated all 2,881 inclusive
minute states, produced a complete schema-valid artifact with no provider failures,
and retained 97 objects and 1,074 relationships. This is useful behavior, not a
partial-success mode.

The artifacts intentionally contain no bounded structural score and emit no
canonical claims. Their large relationship/evidence surface reinforces the
root-owner family and anti-double-counting guidance established in Slice 6.

## Version decision

Keep package version **0.7.0**. That version is already the unpublished candidate
for the additive bounded birth-time package, graph, provenance, evidence, and CLI
contract family. Slices 1–7 completed its intended scope while preserving exact
Natal contracts. Renumbering before any 0.7.0 publication would communicate a
superseded public baseline that does not exist.

Current bounded identities are Dataset 1.0.0, graph 1.3.0, evidence contract
`agf.bounded_uncertainty_evidence.v1.0.0`, calculation profile 1.5.0, and interval
proof 1.0.0. Publication remains separately authorized work and is intentionally
not performed here.

## Gate disposition

Focused oracle tests, installed full-suite tests, packaged-schema validation,
controlled live execution, deterministic replay, CLI/runtime-manifest inspection,
JSON/Markdown validation, diff review, and cleanup are the Gate 7 controls. Final
source-suite and repository-wide validation are recorded in the sprint log before
human approval.
