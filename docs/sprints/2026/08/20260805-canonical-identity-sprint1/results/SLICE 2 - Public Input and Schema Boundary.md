# Slice 2 — Public Input and Schema Boundary

**Status:** Gate candidate; awaiting human approval

## Outcome

AGF's supported live Natal boundary now accepts the optional caller-owned `source_chart_id` decided in Slice 1. The value is validated once at the `BirthData` boundary, carried through provider construction and serialized Natal metadata, represented by the `TransitableChart` descriptor, and exposed by the Python and CLI entry points used to create Natal packages.

This slice establishes the public carrier. Slice 3 still owns authoritative multi-carrier conflict detection and general canonical reference migration.

## Implemented Contract

- Added `BirthData.source_chart_id: str | None = None` without breaking positional legacy construction.
- Added a centralized validator with the approved 1–200 character namespace-safe ASCII grammar.
- Rejected non-string, empty, whitespace-bearing, Unicode, control/delimiter-hostile, and overlength values.
- Preserved valid values exactly, including case.
- Added `source_chart_id` to `natal.build` and propagated it into live `BirthData`.
- Serialized explicit identity into live provider metadata, person metadata, and the calculated Natal chart.
- Made `TransitableChart` recognize explicit package metadata identity before its legacy label-derived fallback.
- Mirrored provider source/target chart identity into Natal package metadata.
- Added CLI arguments:
  - `astro-package natal --source-chart-id`
  - `astro-package generate-ephemeris --source-chart-id`
  - `generate-daily-ephemeris --source-chart-id`
  - `astro-package synastry --person-a-source-chart-id` and `--person-b-source-chart-id`
  - equivalent pair arguments on the Composite path that shares the pair-input helper
- Updated the guided Natal and Synastry tools to accept and forward the same flags.
- Added optional identity validation to the birth-data schema and consistent constraints to canonical graph and TransitableChart identity fields.

## Compatibility

- Existing callers may omit the field and retain the current deterministic name-derived fallback.
- The birth schema property is optional.
- Existing `BirthData` positional arguments retain their order because the new field is last.
- Existing saved `TransitableChart` descriptors remain valid when their IDs satisfy the newly documented grammar.
- No package/schema version has changed yet. Final version decisions remain evidence-gated in later slices.

## Deliberate Boundaries

- This slice does not replace `_semantic_identity`'s current truthy alias precedence. Slice 3 will collect carriers, accept exact duplicates, and reject conflicts.
- This slice does not promise mutation from finalized identity A to B.
- This slice does not change Composite or Davison relationship identity derivation.
- This slice does not define AstroWoof's product namespace recipe.
- Cached/saved packages continue to carry identity through their existing metadata/descriptors; the new invocation parameter is specifically the supported live-generation carrier.

## Tests Added

- Valid identifier preservation, including mixed case and 200-character boundary.
- Invalid string and non-string rejection.
- Optional legacy behavior.
- Birth-schema acceptance/rejection.
- Transitable descriptor recognition without slugging.
- Installed-module CLI help surfaces for Natal, Synastry, and standalone ephemeris generation.
- Live pair-input forwarding.
- End-to-end mocked live Natal construction proving the ID reaches `BirthData`, package metadata, `TransitableChart`, and the canonical graph.

## Gate Evidence

- New identity tests: 23 passed.
- Identity plus workflow helper tests: 31 passed before the final end-to-end test was added.
- Full suite after the final end-to-end test: 142 passed.
- Python compilation: passed for `src`, `tools`, and the new test module.
- Targeted Ruff check for the new validator and test module: passed. Repository-wide Ruff currently reports pre-existing style debt outside this slice, so it is not used as a release gate here.
- `git diff --check` and final diff review are recorded in the sprint log/gate handoff.

## Files Changed

- `src/astrology_graph_foundry/common/identity.py`
- `src/astrology_graph_foundry/ephemeris/models.py`
- `src/astrology_graph_foundry/ephemeris/providers.py`
- `src/astrology_graph_foundry/ephemeris/live_natal.py`
- `src/astrology_graph_foundry/ephemeris/generate_daily_ephemeris.py`
- `src/astrology_graph_foundry/common/transitable_chart.py`
- `src/astrology_graph_foundry/pipelines/natal.py`
- `src/astrology_graph_foundry/pipelines/composite.py`
- `src/astrology_graph_foundry/cli.py`
- `src/astrology_graph_foundry/schemas/birth_data_v1.schema.json`
- `src/astrology_graph_foundry/schemas/canonical_astrology_graph_v1.schema.json`
- `src/astrology_graph_foundry/schemas/transitable_chart_v1.schema.json`
- `tools/_foundry_cli.py`
- `tools/build_natal.py`
- `tools/build_synastry.py`
- `tests/test_source_chart_identity_input.py`

## Gate Decision Requested

Approve this public carrier and schema boundary before committing Slice 2 and beginning Slice 3's conflict-aware finalization and migration work.
