# Fixture inputs

Place canonical QA inputs here. The streaming-profile QA runner looks for:

- `transit.full.json` — a full Transit package.
- `solar_return.full.json` — a full Solar Return package (optional but recommended).

For compatibility with the repository's historical fixture corpus, the runner falls back to the matching files under `scripts/outputs/kevin_bre_test/` when these canonical names are absent.
