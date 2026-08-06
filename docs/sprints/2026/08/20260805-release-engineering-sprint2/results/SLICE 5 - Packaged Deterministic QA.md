# Slice 5 - Packaged Deterministic QA

## Outcome

The corrected AGF 0.6.0 wheel passes deterministic saved-package qualification from a clean CPython 3.12 Windows environment outside the source checkout, with pyswisseph absent. Installed SPC 0.10.0 successfully projects the replayed canonical graph and preserves explicit source-chart identity.

## Successful QA findings and fixes

The first clean install exposed that Windows Python had no system IANA timezone database and AGF did not declare `tzdata`. Cached replay therefore failed while normalizing `America/Denver`. AGF now conditionally declares `tzdata>=2024.1` on Windows, the package contract documents it, and the clean environment resolved `tzdata==2026.3`.

The corrected second wheel exposed a stale Natal schema requirement for `natal.semantic_graph`. Canonical finalization intentionally removes that legacy nested alias and publishes top-level `canonical_astrology_graph`. The schema now makes the nested alias optional and retains the canonical graph requirement; a regression assertion protects that contract.

Both defects were fixed while evidence was fresh. Qualification restarted from a newly built wheel in a new environment after each fix.

## Determinism boundary

Two meaningful cached `astro-package natal` invocations were separated across timestamp seconds. Exact package bytes correctly differed because `metadata.created_at` is operational. Removing only that documented field produced byte-identical canonical JSON with SHA-256 `7d8d1087fbb51fce032fa86d442a4e81dc9aa53df32904f121daba9da36f8bab`. The canonical graph itself was identical with SHA-256 `73566ffe82267ea24daa82a959acdf5236bdd83febdc7ba992b20431ccdb9689`.

The package validated against installed schemas, retained `astrowoof:dog:slice5`, and correctly labeled cached provenance as not proving the original calculation runtime.

## Installed runtime evidence

- Candidate wheel SHA-256: `7b2101cb9bec75e29c1a274b3af04f55af73afde00d284192a53517654f8347e`.
- SPC 0.10.0 wheel SHA-256: `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`.
- Imports resolved under the isolated environment's `site-packages`; the working directory was outside the checkout.
- All 34 installed schema bytes matched the runtime manifest; canonical manifest SHA-256 was `58e351fc4a713c5cdb1a254c442ba46b586ca98fe30ff0020e5f634e6408d7f0`.
- Installed projection produced three objects and one relationship and preserved the explicit identity.
- Full tests against installed wheel code: 176 passed.
- Both console commands reported 0.6.0. The main CLI exercised Natal, projection, runtime manifest, doctor, and expected live failure; the ephemeris CLI exercised version/help and expected live failure.
- Both no-Swiss live paths exited nonzero, emitted no output artifact, and contained no traceback.

This wheel is Slice 5 evidence, not the final release artifact. Slice 7 performs controlled reproducible builds from the exact final commit.
