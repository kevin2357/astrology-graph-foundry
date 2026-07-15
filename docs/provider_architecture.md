# Provider Architecture

Cached JSONL and live Swiss Ephemeris providers expose the same `EphemerisProvider` interface: `person_metadata()`, `natal_chart()`, `iter_days()`, and `persist_jsonl(path)`.
