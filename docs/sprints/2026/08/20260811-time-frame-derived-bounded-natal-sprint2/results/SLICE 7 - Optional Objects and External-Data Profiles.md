# Slice 7 — Optional Objects and External-Data Profiles

## Outcome

Gate 7 is ready for human review. The bounded no-file profile remains independent
of external ephemeris resources, while requests for Chiron, asteroids, or fixed
stars are now visible in both evidence and calculation provenance rather than being
silently ignored.

## Audit findings

- Exact Natal can probe Chiron and asteroids through Swiss Ephemeris and can read
  fixed-star catalogs. Provider runtime provenance inventories nonrecursive `*.se1`,
  `sefstars.txt`, and `seorbel.txt` resources by filename, size, and SHA-256.
- The qualified AstroWoof profile deliberately uses Moshier with no external files
  and disables these features.
- Bounded Natal uses the twelve core bodies. Before this slice, optional flags did
  not alter evaluation but also lacked explicit bounded evidence, and bounded
  provenance flattened their status to `optional_file_dependent: false`.

## Accepted contract

- No external-data-backed bounded profile is qualified now.
- Requested Chiron, asteroid, or fixed-star families emit `unavailable` evidence
  with availability `unsupported_profile`.
- Disabled families emit `unavailable` evidence with availability `disabled`.
- Core bounded calculation remains complete in either case.
- Request flags, asteroid IDs, and fixed-star names affect configuration identity.
- Local paths never become semantic identity or appear in retained provenance.
- A future profile must pin library and data artifacts, resource hashes, supported
  coverage, provider mode, and fallback behavior under a new profile version.

## Verification

- Focused artifact/provenance suite: 21 passed.
- Controlled Linux requested and disabled cases both completed with the same twelve
  core bodies and the expected explicit evidence classifications.
- No external data was downloaded, copied, bundled, or consulted.

## Gate disposition

Candidate for Gate 7 approval. No downstream repository, release, tag, or external
data resource changed.
