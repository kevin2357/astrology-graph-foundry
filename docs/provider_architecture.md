# Provider Architecture

AGF exposes cached and live astronomy sources through the `EphemerisProvider` boundary. Providers supply target metadata, a target chart, optional daily snapshots, an optional graph compiler, persistence helpers, and calculation-runtime provenance. Natal-named methods remain compatibility aliases over the generic target boundary.

## Cached provider

`CachedJsonlEphemerisProvider` reads saved person and optional global JSONL inputs. It can filter daily rows by date and materialize a semantic graph when the cached Natal row lacks one.

Cached replay is not evidence of the original astronomy environment. Its runtime provenance reports `cached_replay` and `calculation_runtime=not_observed`. Calculation provenance may recover birth geometry from the package, but it never upgrades unknown historical provider, data, or configuration claims by inference.

JSONL is a supported provider/persistence interface, not a release artifact format or an instruction to retain generated JSONL in the repository.

## Live provider

`LiveSwissEphemerisProvider` requires pyswisseph and accepts either birth data for a new Natal chart or an existing `TransitableChart` target for timing work. `ProviderConfig` controls date windows, snapshot timezone/time, ephemeris path and mode, house system, aspects, declinations, dignity/sect/derived techniques, harmonics, and optional objects.

`ephemeris_mode` accepts:

- `auto`: historical Swiss-first behavior that may fall back;
- `swiss`: explicitly require returned Swiss Ephemeris flags; or
- `moshier`: explicitly require returned Moshier flags.

Explicit `swiss` and `moshier` requests fail if observed returned modes do not exactly match. Ecliptic and equatorial-declination calls retain returned flags. This requested-versus-observed record is part of calculation provenance.

## External data and optional objects

AGF inventories relevant external data nonrecursively: `*.se1`, `sefstars.txt`, and `seorbel.txt`. Provenance records filename, byte size, per-file SHA-256, and a sorted aggregate hash; it does not record the machine-local ephemeris path.

Chiron, asteroids, and fixed stars are optional. Missing optional object data may produce explicit skipped-object warnings. Core calculation, house, timezone, or required-input failures do not produce a documented partial-but-valid Natal package.

The AGF 0.6.0 qualified live profile requests Moshier directly, uses no external ephemeris files, and disables optional file-backed points. Other provider/data combinations remain available implementation surfaces but are not production-qualified merely because they execute. See [Qualified Live Calculation Profile](Qualified%20Live%20Calculation%20Profile.md).

## Identity boundary

`BirthData.source_chart_id` is caller-owned canonical chart identity. The provider preserves it through metadata and the built chart; it is not derived from provider configuration, calculation hashes, ephemeris paths, or projection context. Display name is descriptive when explicit identity is present.

## Operational checks

Saved and projection modes remain available without pyswisseph. `astro-package doctor --require-mode live --json` verifies dependency availability only; release evidence determines whether a Python/platform/provider/data combination is qualified. See [Release Engineering](Release%20Engineering.md) and [Calculation Provenance and Hashing](Calculation%20Provenance%20and%20Hashing.md).
