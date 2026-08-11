# Runtime and Contract Inventory

This is the concise consumer inventory for the published AGF 0.7.0 wheel. The packaged JSON Schemas remain authoritative; enumerate and hash the installed bytes with `astro-package runtime-manifest` rather than locating source-tree files.

## Unreleased bounded expansion

Current source after the two bounded-parity sprints emits bounded canonical graph
1.7.0 and bounded calculation profile 1.12.0. It adds terrestrial-frame, invariant
house/cusp/angle, sect/triplicity, branched lot, Vertex-house, and optional-feature
disposition semantics while keeping Bounded Natal Dataset 1.0.0 and bounded
uncertainty evidence 1.0.0. This source state is qualified as a release candidate,
not a published immutable artifact; consumers must continue pinning published 0.7.0
until a separately authorized release occurs.

## Published 0.7.0 bounded additions

The current source adds bounded Birth Data v1, Bounded Natal Dataset 1.0.0, bounded
canonical graph 1.3.0, bounded calculation provenance 1.0.0, bounded normalization
policy 1.0.0, bounded uncertainty evidence 1.0.0, bounded calculation profile
1.5.0, and interval proof profile 1.0.0. Its installed wheel exposes 39 schema
resources and clean-release runtime-manifest hash
`4f4b344cf1bd344c0b3d76400982bbf9c5d9f1b3852b4d2660631299603fd93a`.

These contracts do not change exact canonical graph 1.3.0.

The previously recorded 38-resource manifest hash describes the earlier `00e6c2a`
candidate boundary and must not be reused. The published wheel is built from commit
`8926483b38c6b5c6fd33748aa190d330bba4cd5b`; its SHA-256 is
`fca6c153b14cd88f56ca9e151baf8d048cde4d3ac41a14af9912e3176fa52f53`.

## Stable public boundary

- Distribution: `astrology-graph-foundry`; import package: `astrology_graph_foundry`.
- Python: 3.10–3.12 are the declared pure-mode matrix. The only qualified live profile is CPython 3.11 on glibc Linux x86-64 with the exact Moshier configuration documented below.
- Commands: `astro-package` and `generate-daily-ephemeris`.
- Base dependencies: no SPC runtime dependency; Windows additionally uses the
  declared `tzdata` dependency. Projection orchestration installs SPC independently.
- Timezone database: `tzdata>=2024.1` on Windows, where Python does not normally have an operating-system IANA timezone database. Production locks its exact artifact.
- Optional live dependency: `pyswisseph>=2.10,<2.11`; its presence alone is not a production qualification.
- Canonical graph: `canonical_astrology_graph.v1`, graph version 1.3.0.
- Canonical identity: semantic identity policy `semantic_sensor_identity_v1.1.0`; relationship identity policy `relationship_chart_identity_v1.0.0`. Callers should supply opaque `source_chart_id` through live Natal generation. The deterministic name fallback is compatibility behavior, not a production identity.
- Calculation provenance: `agf.calculation_provenance.v1.0.0`; calculation profile `agf.calculation_profile.v1.1.0`; normalization policy `agf.normalization_policy.v1.0.0`.
- Published AGF wheel SHA-256: `fca6c153b14cd88f56ca9e151baf8d048cde4d3ac41a14af9912e3176fa52f53`; installed resource count: 39; canonical runtime-manifest SHA-256: `4f4b344cf1bd344c0b3d76400982bbf9c5d9f1b3852b4d2660631299603fd93a`.

The runtime manifest is the complete machine-readable inventory for the installed build. Release-significant families include birth input, Natal packages, canonical and structural graphs, evidence provenance, projection requests/results, transitable charts, temporal activation/source handoffs, and calculation provenance. Consumers must inspect each resource's declared version rather than infer a contract from its filename.

## Consumer guarantees

AGF preserves explicit source-chart identity through canonical objects, relationships, evidence, adapters, serialization, and SPC handoff. Display-name changes do not rescope canonical IDs when `source_chart_id` is unchanged. Projection context is not part of source identity.

Collections intended for canonical serialization are deterministic under identical semantic inputs, configuration, package versions, and provider/data behavior. Operational fields such as generation timestamps are not semantic identity. The persistence owner hashes the exact returned artifact bytes; AGF supplies normalized-source and calculation-configuration hashes without claiming those are the persisted artifact hash.

Saved packages may predate current provenance. Cached replay provenance explicitly reports that it cannot establish the original calculation runtime. Consumers must not upgrade that status by inference.

## Failure and output policy

Supported generation produces a complete schema-valid package or fails. Optional-object omissions may appear as warnings when the configured policy allows them. AGF does not expose a general partial-artifact success contract.

- Request validation failures (identity syntax, coordinates, timezone/date parsing, missing fields) are terminal until input changes.
- Schema, version, or SPC incompatibility is terminal until artifacts/configuration change.
- Missing installed resources or distribution/runtime version mismatch is a deployment defect.
- Missing pyswisseph disables live mode but does not disable saved mode.
- Ephemeris calculation or data failures require operator classification; retryability is not implied by exception type alone.

Run `astro-package doctor --require-mode MODE --json` at startup. Its live assertion checks installed dependency availability; release manifests and controlled-live evidence remain authoritative for provider/data qualification.
