# Slice 2 - Input, Normalization, and Provenance Boundary

**Status:** Gate ready for review

**Starting boundary:** `41994dc` (`Document bounded natal Slice 1 contract`)

## Outcome

AGF now has a separate bounded birth-data boundary without changing exact Birth Data
v1 or exact Natal output. It accepts and normalizes bounded and `unknown_time`
evidence through Python, packaged JSON Schema, the Natal CLI, and the standard Natal
helper. Bounded package calculation remains deliberately unavailable until Slice 3.

## Implemented contract

### Models

- Existing `BirthData` remains unchanged for exact input.
- New `BirthTimeBasis` represents `exact`, `bounded`, and `unknown_time` for shared
  normalization and testing.
- New `BoundedBirthData` accepts only `bounded` or `unknown_time`, validates common
  coordinates/identity, and retains its normalized basis.
- The hard bounded-v1 maximum is 48 elapsed UTC hours.

The exact tagged basis exists so normalization semantics can be compared and tested,
but exact production invocation still uses the existing `BirthData` contract.

### Civil-time normalization

- Local values must be timezone-naive ISO datetimes.
- IANA timezone must resolve through `ZoneInfo`.
- Nonexistent local walls fail closed.
- Ambiguous folds fail closed until a fold/offset contract is explicitly supported.
- Optional caller-resolved UTC endpoints are accepted by the Python model only when
  they exactly match local datetime plus timezone.
- Caller bounded endpoints are inclusive.
- `unknown_time` spans local midnight inclusive to the next local midnight exclusive
  and therefore correctly produces 23- or 25-hour elapsed intervals on DST days.
- Inverted/empty bounds and intervals over 48 hours are rejected.

Rare zones whose calendar-day boundary itself is ambiguous or nonexistent currently
fail closed. This is preferable to inventing a local date interval and can be
revisited with explicit transition-aware calendar-day resolution.

### Schema and installed resources

Added packaged `bounded_birth_data_v1.schema.json`. It accepts only bounded or
`unknown_time` bases and enforces coordinate/identity structure. The existing
`birth_data_v1.schema.json` still requires `birth_local` and has no
`birth_time_basis` property.

The installed runtime manifest now contains 35 schemas rather than 34; installed
resource tests assert the new schema is discoverable and byte-hashed.

### CLI and helper boundary

Only the `natal` command exposes:

- `--birth-local-earliest`;
- `--birth-local-latest`;
- `--birth-date`; and
- `--birth-time-unknown`.

Transit and other package-family CLIs do not expose them. Exact `--birth-local`
conflicts with bounded carriers. The standard `tools/build_natal.py` helper forwards
the new form without fabricating `--birth-local`.

A valid bounded invocation currently raises a clear `NotImplementedError` before
provider calculation. This is an intentional gate: accepting and then generating an
exact-looking package would violate Slice 1.

## Hash and provenance boundary

Added `agf.bounded_birth_time.normalization_policy.v1.0.0` and a bounded source-input
provenance builder. Its hash includes mode, supplied values, normalized local/UTC
bounds, boundary policy, duration, timezone, and coordinates. Display name, location
label, and `source_chart_id` remain excluded as descriptive/lineage values.

Compact golden vectors are retained in
[`bounded-input-normalization-vectors.json`](bounded-input-normalization-vectors.json).
Full calculation/configuration provenance waits for Slice 3 because the uncertainty
algorithm/profile does not yet exist.

## Findings and defects

- Adding a packaged schema correctly broke three resource-count assertions. They
  were updated to 35 and now explicitly require the bounded schema.
- The bundled Python initially needed local editable AGF/SPC and declared test
  dependencies; this affects only the external workspace runtime.
- Python floating NaN can bypass ordinary range comparisons, so bounded coordinates
  explicitly require finiteness in addition to signed-degree ranges.
- “Whole local date” cannot be implemented as 24 hours; tests prove 23- and 25-hour
  normalization.

## Test evidence

- Initial focused boundary/provenance/identity suite: 48 passed.
- First full suite after adding the schema: 193 passed, 3 failed. All three failures
  were expected resource-count assertions (34 versus 35), not behavior regressions.
- Full suite after manifest assertions: 196 passed in 16.29 seconds.
- Final focused bounded/helper/resource suite after finiteness and helper coverage:
  34 passed in 8.75 seconds.
- `compileall` passed for `src`, `tests`, and `tools`.
- Targeted Ruff passed after import normalization, excluding one documented
  pre-existing timezone warning in the legacy exact Natal `created_at` field.
- Final full suite after helper and retained-vector coverage: 198 passed in 18.57
  seconds.

## Slice 3 handoff

Slice 3 may consume `BoundedBirthData.resolved_birth_time_basis` and
`build_bounded_source_input_provenance`. It must replace the deliberate
`NotImplementedError` only after the interval engine can emit real bounded evidence.
It must not modify exact `BirthData`, exact Natal schema, or exact graph behavior.

The first calculation profile must bind sampling/refinement policy, tolerances,
configured feature set, and proof status. It must generate longitude ranges and
transition evidence suitable for the Transit and Synastry research journals.
