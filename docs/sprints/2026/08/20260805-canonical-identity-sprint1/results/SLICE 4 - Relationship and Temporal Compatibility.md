# Slice 4 — Relationship and Temporal Compatibility

**Status:** Gate candidate; awaiting human approval

## Outcome

AGF now distinguishes three related identity patterns without using display names as the production basis:

- Natal: one explicit caller-owned canonical source chart ID.
- Synastry: an ordered pair of participant canonical chart IDs because person-A/person-B roles are directional.
- Composite and Davison: an order-independent, technique-specific relationship chart ID derived from the stable participant chart IDs.

Transit, return, profection, eclipse/lunation, and temporal artifacts retain the target canonical chart ID and separate their technique/time/location identity in `sensor_instance_id`.

## Relationship Identity Contract

`relationship_chart_identity_v1.0.0` derives Composite and Davison identity from:

1. the relationship identity policy version;
2. chart type (`composite` or `davison`); and
3. the two validated participant canonical chart IDs sorted lexically.

The canonical ID is `<chart-type>:<32 lowercase hexadecimal characters>`, using the first 128 bits of SHA-256 over the canonical payload.

Properties:

- changing display names does not change relationship chart identity;
- reversing participant input order does not change Composite or Davison identity;
- Composite and Davison IDs differ for the same participants;
- calculation geometry, pipeline timestamps, filesystem paths, projection context, and product metadata are excluded;
- the ordered participant IDs remain recorded in package metadata for provenance even though derivation canonicalizes their order; and
- the derivation version is recorded so a future identity-algorithm change is explicit.

This preserves the distinction between chart identity and calculation identity. A later calculation-profile change does not silently produce a new relationship subject identity.

## Synastry Contract

Synastry continues to expose `source_chart_ids` in person-A/person-B order and forms its sensor identity from that ordered pair. This is deliberate because directional aspects and house overlays depend on role order.

Nested participant metadata now uses the same equal-or-conflict rule as Natal identity. Same-named participants with distinct explicit IDs remain distinct. Renaming either participant does not alter source identity when explicit IDs are unchanged.

The current colon-concatenated Synastry `sensor_instance_id` is retained for compatibility; the authoritative unambiguous representation is the ordered `source_chart_ids` array. Any future change to a hashed/length-delimited sensor ID belongs to a separately versioned contract.

## Composite and Davison Integration

- Composite computes participant source IDs before chart construction, records the derived relationship source ID and policy version, and passes that ID through TransitableChart and canonical finalization.
- Davison derives the same way under its own chart-type namespace and supplies the relationship source ID to the internal live midpoint-event Natal calculation, preventing a display-name-derived intermediate scope.
- Existing legacy relationship packages without explicit identity retain the documented name-derived fallback. Newly generated relationship packages use the versioned derivation.

## Temporal and Transitable Boundaries

- Direct target identity carriers now use strict validation and conflict detection rather than silent first-truthy precedence.
- `TransitableChart.from_package` checks descriptor, package metadata, chart, and canonical graph carriers for agreement.
- Transit and timing sensor IDs remain derived from target chart identity plus technique-specific period/year/location data.
- Temporal projection continues to compare target and static canonical chart identity and remains downstream projection-context neutral.

## Compatibility Impact

- New Composite and Davison generation changes relationship chart identity from name-derived IDs to versioned participant-derived IDs. This is an intentional 0.6.0 behavior change.
- Legacy saved packages that already record a TransitableChart identity keep that identity unless explicitly migrated under a future relationship migration contract.
- No relationship rescope helper was added. Natal's helper remains Natal-only because relationship artifacts have participant and technique semantics requiring their own migration design.
- SPC's source-identity shape is unchanged: one relationship chart ID for Composite/Davison, ordered participant IDs for Synastry, target chart ID for temporal sensors.

## Gate Evidence

- Relationship/temporal focused suite: 37 passed.
- Transitable/source/relationship focused suite after strict descriptor conflicts: 34 passed.
- Final focused relationship/source/temporal suite: 51 passed.
- Final full suite: 154 passed.
- Targeted Ruff passed; final diff checks are recorded in the sprint log and handoff.

Coverage proves:

- Composite identity survives display-name changes.
- Composite identity is invariant under participant reversal.
- Composite and Davison identities are technique-specific.
- Same-named Synastry participants remain distinct by explicit ID.
- Temporal target carrier disagreement fails closed.
- Transitable descriptor carrier disagreement fails closed.

## Files Changed

- `src/astrology_graph_foundry/common/identity.py`
- `src/astrology_graph_foundry/common/semantic_layers.py`
- `src/astrology_graph_foundry/common/transitable_chart.py`
- `src/astrology_graph_foundry/pipelines/composite.py`
- `src/astrology_graph_foundry/pipelines/davison.py`
- `tests/test_synastry_composite_pipelines.py`
- `tests/test_semantic_boundary_chunk1.py`
- `tests/test_source_chart_identity_input.py`
- this result and the append-only sprint log

## Gate Decision Requested

Approve the versioned participant-derived Composite/Davison contract, ordered Synastry contract, and strict temporal/Transitable identity checks before committing Slice 4 and beginning installed downstream migration/compatibility QA.
