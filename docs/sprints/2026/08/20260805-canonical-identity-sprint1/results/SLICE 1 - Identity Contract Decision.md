# Slice 1 — Identity Contract Decision

**Status:** Gate candidate; awaiting human approval

**Scope:** Contract and identity-path audit only; no production implementation

## Decision Summary

The supported live-Natal input field will be `source_chart_id`.

It denotes the stable identity of the canonical source chart. It is supplied by the caller, is opaque to AGF, and is neither a display name nor an application/database type. AGF must not infer users, dogs, handlers, breeds, accounts, birth-data versions, or projection contexts from it.

An explicit `source_chart_id` is the production contract. The current `natal:<slug(display name)>` behavior remains an optional deterministic compatibility fallback in this sprint; it is documented as collision-prone and unsuitable for durable joins, cache lineage, or immutable production readings.

## Why `source_chart_id`

| Candidate | Decision | Reason |
|---|---|---|
| `source_chart_id` | Accept | Existing canonical graph, evidence, metadata, projection adapter, and SPC vocabulary. It describes the chart's role at the boundary without product semantics. |
| `chart_id` | Internal alias only | Already used by `TransitableChart.chart_identity`, but too generic for the live source boundary and conflicts with several target/relationship uses. |
| `subject_id` | Reject | A subject can own multiple corrected/calculated charts, and the name encourages leakage of product/database subject semantics into AGF. |
| Product-specific name | Reject | AGF is reusable and must not learn AstroWoof dog or account concepts. |

## Authoritative Semantics

`source_chart_id` answers “which canonical chart is this?” It does not answer:

- which display label should be rendered;
- which immutable birth-data revision or calculation request produced it;
- which configuration or ephemeris produced its geometry;
- which observation/technique generated a sensor artifact;
- which projection context or target ontology is active; or
- which product database row owns it.

Those identities remain separately versioned and recorded. In AstroWoof, the API may derive an AGF-safe value from product-owned stable identity, but the namespace recipe is an API/project decision. AGF sees only the opaque resulting string.

## Validation and Preservation Contract

The implementation target for Slice 2 is:

- JSON/Python type: string only; booleans, numbers, bytes, and implicit coercion are rejected.
- Length: 1–200 Unicode code points.
- Grammar: ASCII namespace-safe characters matching `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$`.
- Whitespace and control characters: rejected anywhere; values are not trimmed.
- Empty strings: rejected rather than treated as absent.
- Preservation: a valid value is retained byte-for-byte. AGF does not lowercase, slugify, Unicode-normalize, add a timestamp, or add/remove a prefix.
- Stability/uniqueness: caller responsibility. AGF prevents ambiguity within one artifact but cannot detect global collisions across requests.
- Reserved prefix: none initially. `natal:` is recommended for human clarity but is not required, because a complete opaque namespace belongs to the caller.

The ASCII grammar is deliberately narrower than “any string.” Canonical IDs are embedded into colon-delimited object and sensor IDs, registry keys, logs, CLI arguments, and downstream hashes. Excluding whitespace, control characters, and delimiter-hostile punctuation avoids ambiguous composite identifiers without altering accepted values.

Changing this grammar after release is a contract change. Slice 2 must centralize validation and apply it consistently to Python, CLI, saved-package, and descriptor carriers.

## Precedence and Conflict Rule

For a Natal package, collect every non-null explicit identity carrier:

1. invocation/BirthData `source_chart_id`;
2. `transitable_chart.chart_identity.chart_id`;
3. package metadata `source_chart_id`;
4. legacy metadata aliases `target_chart_id` or `chart_id` only where the package type historically permits them.

Rules:

- If no explicit value is present, use the documented legacy name-derived fallback.
- If one distinct explicit value is present, it is authoritative.
- If several carriers contain the same exact value, accept it.
- If carriers contain different values, fail closed with an error naming the conflicting carriers.
- Display name never participates when an explicit identity exists.

This replaces the current silent `or` precedence as the public contract. Precedence describes where identity may enter; it must not conceal disagreement.

## Canonical Scoping Contract

With authoritative source identity `S`:

- `canonical_astrology_graph.source_chart_id == S`;
- the first and only Natal entry in `source_chart_ids` is `S`;
- Natal `sensor_instance_id` currently equals `S` but remains a semantically distinct field;
- source object IDs are scoped beneath `S` exactly once;
- relationship IDs are deterministically regenerated from scoped endpoints and relationship facts;
- indexes are rebuilt after migration;
- evidence and structural-evidence `source_chart_ids` contain `S`;
- claims, operators, registries, projection views, nested exact values, and exact-key references point only to post-scope IDs;
- `TransitableChart.chart_identity.chart_id == S`; and
- the projection adapter passes `S` without introducing projection context.

The scoped object form must work for both `S = natal:example` and a caller namespace such as `S = astrowoof:dog:<uuid>`. The current helper's special handling of `natal:` means Slice 3 must specify and test the exact result rather than infer it from prefix shape.

## Rename, Collision, and Regeneration Behavior

- Changing display name while keeping `source_chart_id` fixed changes descriptive metadata only; canonical object and relationship IDs remain unchanged.
- Two subjects with the same normalized display name and different explicit IDs have disjoint canonical IDs.
- Repeating generation/finalization with identical explicit identity and inputs is idempotent.
- Changing explicit identity denotes a different canonical chart identity and therefore changes every chart-scoped object ID, affected relationship ID, source identity field, and exact reference.
- Mutation of an already-finalized artifact from identity A to B is not implicitly safe. Slice 3 must either implement a complete origin-aware rescope or reject it and require regeneration from unscoped/source facts. Prefix stacking is never valid.
- A caller correcting birth facts may keep or replace chart identity according to its own immutable-version policy, but calculation/birth-version lineage must reveal the correction. AGF does not silently derive that policy from the identifier.

## Carrier and Consumer Matrix

| Boundary | Current behavior | Sprint implication |
|---|---|---|
| `BirthData` | Name and birth geometry only | Add optional `source_chart_id`; validate centrally. |
| `natal.build` | Cannot accept explicit identity | Add keyword and pass it through live/cached package construction. |
| Provider/live helpers | Reconstruct current BirthData shape | Add/pass the same field without product assumptions. |
| `astro-package` Natal command | No identity flag | Add `--source-chart-id`; compatibility fallback remains when omitted. |
| `generate-daily-ephemeris` | Birth inputs but no identity | Add the field wherever it generates a Natal package; distinguish ephemeris-only paths. |
| Repository tools | Duplicate birth argument helpers | Add consistent single/pair flags and forwarding. |
| Birth schema | No identity property | Add optional validated property; version impact reviewed below. |
| Package metadata | Finalizer writes source identity | Treat as an output mirror and accepted saved-package carrier; detect disagreement. |
| `TransitableChart` | Uses `chart_identity.chart_id` | Preserve as the chart-interface representation of the same canonical identity. |
| Semantic finalizer | Silent ordered aliases, then name fallback | Replace with explicit collection/validation/conflict detection. |
| Canonical graph | Has `source_chart_id(s)` with weak string constraints | Apply shared identifier definition or reference; retain graph topology. |
| Objects/relationships/indexes | Scoped/rebuilt for legacy `natal:*` IDs | Generalize safely for explicit scope; prove complete exact-reference migration. |
| Claims/evidence/operators/registries | Rewritten recursively by exact match | Retain behavior and add stale-reference/integrity checks. |
| Synastry | Reads nested saved identities or name fallback | Ensure live pair inputs can carry distinct participant IDs; order remains explicit. |
| Composite/Davison | Relationship IDs often derive from participant names/label | Separate reviewed contract in Slice 4; do not silently inherit Natal behavior. |
| Transit/returns/temporal | Consume `TransitableChart.chart_id` as target identity | Explicit Natal identity must survive and be validated unchanged. |
| Projection adapter | Sends source/sensor identity to SPC | Preserve exact value; SPC context remains downstream-owned. |
| Saved fixtures | Mostly legacy/name-scoped | Keep loading deterministically; add explicit-identity fixtures rather than rewriting all history blindly. |
| AstroWoof API | Has dog/birth/calculation/request identities, no AGF identity field | Handoff must add an opaque value while retaining existing lineage hashes. |

## Relationship and Temporal Decision Boundary

This slice freezes Natal identity semantics only. Slice 4 must decide relationship artifacts independently.

Recommended direction:

- Synastry source identity remains the ordered pair of participant canonical chart IDs; same-name participants are safe when explicit IDs exist.
- Composite and Davison should ultimately derive a relationship-chart identity from stable participant chart identities plus a versioned construction rule, or accept an explicit relationship `source_chart_id`. Names must not remain the production basis.
- Transit, returns, annual profections, eclipse/lunation, and temporal activation retain target chart identity `S`; their `sensor_instance_id` separately incorporates technique/time/location as appropriate.
- No projection context enters any source or relationship chart identifier.

Because changing composite/Davison derivation can invalidate existing relationship artifacts, Slice 4 owns its compatibility/version decision and may defer a broader break while documenting the limitation.

## Version Impact

Proposed version posture:

- AGF package: target 0.6.0, subject to final Sprint 1 diff. The Python/CLI addition is backward compatible when omitted, but canonical identity is a material public contract.
- Canonical graph schema: keep 1.3.0 only if topology and required fields remain compatible; strengthen identifier validation through a reusable definition without invalidating legitimate 1.3.0 artifacts. Otherwise issue a compatible schema revision deliberately.
- Birth-data schema: add the optional property under a new documented schema/policy revision if consumers identify schema versions by content rather than filename alone.
- Semantic identity policy: increment from `semantic_sensor_identity_v1.0.0` because precedence/conflict semantics and explicit live identity are new guarantees.
- TransitableChart interface: retain 1.0.0 if `chart_id` meaning is merely clarified and existing descriptors remain valid; increment if validation or required provenance changes its accepted contract.

No version is changed until the relevant implementation slice demonstrates its exact compatibility impact.

## Migration Threat Model

| Risk | Control |
|---|---|
| Same slug collision | Explicit caller identity and same-name/different-ID regression test. |
| Rename changes graph IDs | Explicit-ID rename golden comparison. |
| Silent disagreement among carriers | Collect all carriers and fail closed. |
| Double scoping/prefix stacking | Origin-aware migration or explicit regeneration-only rejection. |
| Stale relationship endpoints | Referential integrity traversal after migration. |
| Stale evidence/claim/registry key | Recursive exact-reference audit against old-ID set. |
| Sensor and chart identity conflated | Separate assertions and technique-specific temporal tests. |
| Calculation hash used as identity | Schema/docs separation and mutation tests. |
| Projection context contaminates source identity | Adapter assertions before/after different contexts. |
| Legacy fixtures break unexpectedly | Deterministic fallback and saved-package regression suite. |
| Opaque IDs create ambiguous composed strings | Bounded namespace-safe grammar and exact preservation. |

## Required Test Matrix

1. Same display name, different explicit IDs: disjoint object/relationship IDs.
2. Different display names, same explicit ID and geometry: identical scoped IDs and references.
3. Same inputs, repeated finalization: byte-stable semantic identity sections and no second scoping.
4. Explicit ID change: complete predictable rescope or explicit regeneration error; never partial migration.
5. Conflicting input/metadata/descriptor identities: actionable failure.
6. Identical duplicate carriers: accepted.
7. Empty, whitespace, overlength, Unicode, control-character, invalid punctuation, and non-string IDs: rejected.
8. Valid mixed-case namespace ID: preserved exactly through JSON and CLI.
9. Omitted ID: deterministic legacy fallback and documented warning/status.
10. Save/reload/adapter/projection: exact identity retained.
11. All object/relationship endpoints, indexes, evidence, claims, registries, operators, and projection views: no old exact references.
12. Product dog ID, birth version, calculation/request hash, sensor identity, and projection context: not substituted for one another.
13. Synastry same-name participants with distinct explicit IDs.
14. Composite/Davison reviewed behavior and compatibility fixtures.
15. Transit/return/temporal target checks with explicit Natal identity.

## Gate 1 Conclusion

The outstanding defect is a missing public carrier plus an under-specified conflict/migration contract, not an absence of canonical identity machinery. The design above reuses AGF's established `source_chart_id` boundary, preserves backward compatibility for exploratory callers, and makes explicit identity mandatory by integration policy rather than by immediately breaking the schema.

Human approval of this gate authorizes Slice 2 implementation against these decisions. Any requested change to field name, grammar, fallback, conflict handling, or migration posture should be made before code changes begin.
