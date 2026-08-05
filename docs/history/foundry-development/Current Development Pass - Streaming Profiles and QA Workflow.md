# Streaming Profiles and One-Command QA Workflow

This pass added:

- Transit `standard`, `compact`, and `game` streaming profiles;
- `core`, `expanded`, `all`, and `gameplay` target sets;
- date-indexed game records with compact daily sky state;
- deterministic gzip JSON transport;
- `transit-streaming-view` for saved full Transit packages;
- diversified Solar Return compact relationship selection;
- the standard Foundry one-command QA layout.

## QA convention

Canonical user fixtures live under:

```text
outputs/fixture_test_files/
```

Every generated QA artifact lives under:

```text
outputs/fixture_outputs/
```

Run:

```bat
scripts\run_streaming_profiles_qa.bat
```

The runner executes pytest, validates fixtures, generates all three streaming profiles in plain and gzip form, validates schemas, performs plain/gzip determinism checks, executes a negative profile test, compacts a Solar Return fixture when available, profiles artifact sizes, and writes `qa_summary.json` and the Foundry application log.
