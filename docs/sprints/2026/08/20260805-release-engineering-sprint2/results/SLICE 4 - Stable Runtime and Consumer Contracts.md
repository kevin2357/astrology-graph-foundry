# Slice 4 - Stable Runtime and Consumer Contracts

## Outcome

The 0.6.0 candidate now has a concise release-facing runtime/contract inventory, an AGF-owned AstroWoof worker handoff, and machine-assertable startup modes. These documents correct the previous 0.5.x and name-derived-identity assumptions without changing API implementation or product behavior.

## Implemented boundary

- General dependency metadata permits SPC 0.10.x; production handoff identifies the published SPC 0.10.0 wheel and SHA-256 exactly.
- Saved, projection, and live modes have distinct dependency and guarantee statements.
- `astro-package doctor --require-mode saved|projection|live --json` exits 2 with stable failure codes when the selected installed capability is unavailable.
- Doctor reports AGF distribution/runtime agreement, SPC engine/distribution agreement and compatibility, packaged-resource manifest identity, and calculation contract versions.
- Live doctor readiness intentionally means dependency availability only. It does not claim provider, platform, or ephemeris-data qualification.
- Complete-output, warning, partial-artifact, deterministic failure, deployment failure, and orchestration-owned retry boundaries are explicit.
- The API handoff defines the input/identity boundary, retained provenance, cache ingredients, output handoff, startup assertions, and unresolved release artifact placeholders.

## Cross-repository reconciliation

Read-only review confirms SPC 0.10.0 consumes the canonical and optional structural graphs, source identity, and registries without recalculating the chart. Its published wheel SHA-256 is consistently recorded as `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`.

The API's current proposed worker contract still describes AGF 0.5.0, name-derived source identity, and absent unified calculation provenance. Those statements are now stale relative to this candidate. This slice did not edit the busy API repository; the new AGF handoff is the authoritative input for a later API-owned reconciliation.

## Remaining gates

- AGF wheel hash and release commit remain placeholders until reproducible qualification.
- SPC's published hash must still be independently re-downloaded and verified.
- Exact pyswisseph artifact, live Python/platform, ephemeris-data manifest, and Swiss Ephemeris licensing posture remain decisions before Slice 6.
- The development doctor result is not installed-wheel evidence; Slices 5 and 6 must repeat assertions outside the checkout.

## Verification

- Focused doctor, package-resource, identity, and external-projection tests: 42 passed.
- Development startup assertion: projection ready; AGF 0.6.0 metadata aligned; SPC distribution/engine 0.10.0 aligned; 34 packaged schemas inventoried.
- Full-suite, lint, link, JSON, whitespace, and diff verification are recorded in the sprint log at Gate 4 closure.
