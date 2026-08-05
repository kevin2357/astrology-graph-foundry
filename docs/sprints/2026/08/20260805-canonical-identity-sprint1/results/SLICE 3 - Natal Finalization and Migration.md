# Slice 3 — Natal Finalization and Migration

**Status:** Gate candidate; awaiting human approval

## Outcome

Natal canonical finalization now resolves explicit identity carriers as one contract, rejects disagreement, supports deliberate complete A-to-B rescoping, refreshes graph and provenance identity, and remains idempotent. Display-name fallback remains deterministic when no explicit identity exists.

## Implemented Behavior

### Conflict-aware resolution

For Natal packages, finalization collects these explicit carriers:

- `transitable_chart.chart_identity.chart_id`
- `metadata.source_chart_id`
- legacy metadata `target_chart_id` and `chart_id`
- `person.source_chart_id`
- `natal.source_chart_id`

Every supplied value is validated under the Slice 1 grammar. Equal duplicates are accepted. More than one distinct value raises an actionable `ValueError` naming each conflicting carrier. The canonical graph's previous identity is migration provenance and is not treated as a competing caller input.

### Identity policy version

Finalized packages now report `semantic_sensor_identity_v1.1.0`. This marks explicit live identity, strict carrier agreement, and safe rescoping semantics. Package/schema release versions remain deferred to Sprint closure.

### Initial scoping and idempotence

The graph scoper now records the exact source identity in `identity_policy.source_chart_id`. It preserves an accepted identifier byte-for-byte, including a trailing namespace delimiter, while joining object-local suffixes with exactly one delimiter.

Repeated finalization under one identity leaves canonical identity and graph IDs unchanged. Relationship IDs are regenerated deterministically from scoped endpoints, and indexes are rebuilt.

### Deliberate rescoping

`rescope_natal_package_source_chart_id(package, new_id)` is the supported migration operation. It:

1. validates the existing carrier set before mutation;
2. validates the new identity;
3. updates Natal metadata, person/chart carriers, relevant legacy aliases, and TransitableChart identity together;
4. derives local object suffixes from the recorded previous source scope, preventing prefix stacking;
5. rewrites object and relationship IDs and all exact values/registry keys;
6. updates canonical source and sensor fields;
7. refreshes object/relationship evidence;
8. refreshes generated sensor/family/independence provenance across retained package layers; and
9. rebuilds graph indexes and structural evidence.

Directly editing only one carrier is not a supported migration technique and fails when another explicit carrier disagrees.

## Reference Integrity

The migration regression package contains:

- core and derived objects;
- relationship endpoints and relationship IDs;
- object-owner facts;
- indexes;
- a keyed reference registry;
- claim evidence references;
- operator source references; and
- retained projection-view rows with generated evidence provenance.

The gate asserts that no old chart ID, object ID, relationship ID, registry key, or generated source-family token survives; every relationship endpoint resolves to the rebuilt object index; and all refreshed canonical evidence names the new source chart.

## Compatibility

- Omitted identity still yields `natal:<slug(display name)>` deterministically.
- Already-finalized legacy packages retain their recorded identity even if descriptive names later change.
- Existing equal metadata/descriptor mirrors remain valid.
- Conflicting historical artifacts now fail instead of silently selecting whichever carrier appears first. This is an intentional correctness tightening and must be documented as part of the 0.6.0 compatibility guidance.
- The rescope helper is Natal-only. Relationship-chart semantics remain Slice 4 work.

## Gate Evidence

- Focused identity/finalization/source-input suite: 30 passed before the trailing-delimiter and provenance refresh additions.
- Expanded scoping and semantic-boundary suite: 27 passed after complete rescope provenance coverage.
- Final full regression suite: 149 passed.
- Targeted Ruff and machine-readable JSON validation: passed.
- Final whitespace/schema/diff checks are recorded in the sprint log and gate handoff.
- Machine-readable scenario inventory: `identity-migration-fixtures.json`.

## Files Changed

- `src/astrology_graph_foundry/common/identity.py`
- `src/astrology_graph_foundry/common/semantic_layers.py`
- `tests/test_chart_scoped_canonical_ids.py`
- `tests/test_source_chart_identity_input.py`
- `docs/sprints/2026/08/20260805-canonical-identity-sprint1/results/identity-migration-fixtures.json`
- this result and the append-only sprint log

## Gate Decision Requested

Approve the conflict-aware Natal identity finalizer, identity policy v1.1.0, and explicit rescope operation before committing Slice 3 and beginning the separate relationship/temporal identity review.
