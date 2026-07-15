# Rich Natal Facts in the Standard Natal Package

We are keeping one canonical facts+semantics package, not splitting out a facts-only extraction layer. Consumers that do not care about semantics can ignore semantic fields.

This update adds or formalizes these natal facts:

- Chiron/optional bodies skipped gracefully when Swiss Ephemeris files are missing.
- Optional asteroids when enabled.
- Sect.
- Lightweight essential dignities.
- Lots: Fortune and Spirit.
- Declinations, right ascension, parallels, and contra-parallels.
- Antiscia and contra-antiscia.
- Harmonic positions.
- Optional fixed stars when enabled.
- Calculation warnings for skipped optional bodies/fixed stars.

Skipped optional bodies are stored under:

```json
natal.calculation_warnings.skipped_optional_bodies
```

So a missing `seas_18.se1` no longer crashes the chart build.
