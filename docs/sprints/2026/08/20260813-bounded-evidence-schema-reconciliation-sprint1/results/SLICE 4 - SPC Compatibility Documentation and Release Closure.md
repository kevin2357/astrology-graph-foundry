# Slice 4 — SPC Compatibility, Documentation, and Release Closure

**Gate status:** Candidate; awaiting human approval

## Outcome

AGF 0.8.1 is prepared as an unpublished patch candidate. Its repaired bounded
evidence contract crosses SPC's current bounded-intake boundary without changing
epistemic meaning or recreating a package dependency. Release publication remains
an explicit later decision.

## Version decision

The package advances from 0.8.0 to 0.8.1 because the change is additive contract
repair:

- astrological calculations and exact-Natal output do not change;
- bounded dataset schema remains 1.0.0;
- bounded canonical graph remains 1.7.0;
- bounded evidence contract remains 1.0.0;
- bounded calculation profile remains 1.12.0; and
- previously accepted evidence values retain their meanings.

The source of truth, installed distribution metadata, both CLI version surfaces,
and version-sensitive qualification tests now agree on 0.8.1.

## SPC boundary

SPC's active bounded-consumer worktree was inspected and exercised read-only. Its
validator treats `classification` as the epistemic state and preserves availability
and status reason in the immutable source artifact. All ten AGF-supported
availability values survived adaptation verbatim, and its 15 bounded-intake tests
passed.

This is candidate compatibility evidence, not a claim that released SPC 0.10.0
supports bounded projection. SPC's worktree contains its owner's uncommitted Slice 2
implementation; AGF neither modified nor committed it. Production must pin the
eventual independently qualified SPC release artifact and hash.

## Release-candidate qualification

- Two builds under the same controlled source-date epoch were byte-identical.
- Linux installed-wheel suite: 249 passed.
- Saved/base mode passed in a clean environment with SPC absent.
- Live mode passed with SPC imports actively forbidden.
- Both installed CLIs reported 0.8.1.
- Packaged resource count remained 39 and evidence vocabulary count remained 10.
- Reproducible candidate wheel SHA-256:
  `37d7efeb04ced6823c708b1ba09d4fa9a6e4ab29af32aefbcd5fe63116bc2575`.

See the [machine-readable candidate evidence](spc-compatibility-and-release-candidate.json).

## Qualification notes

The first cross-repository pytest invocation ran from the AGF working directory and
could not resolve SPC's `tests.paths`; rerunning from SPC's root passed. A release
probe then invoked the existing no-SPC script without its required `--mode` and was
corrected. Finally, the inherited QA image exposed SPC through system site packages,
so base-mode proof was rerun in a genuinely isolated virtual environment while live
mode retained the qualified provider stack. These were harness corrections, not
product defects.

## Gate recommendation

Approve 0.8.1 as the qualified candidate boundary and close the sprint. Commit and
push may follow approval. Do not tag or publish until separately requested.
