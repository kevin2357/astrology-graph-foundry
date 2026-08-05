# Runtime and Contract Inventory

This is the concise consumer inventory for the AGF 0.6.0 release candidate. The packaged JSON Schemas remain authoritative; enumerate and hash the installed bytes with `astro-package runtime-manifest` rather than locating source-tree files.

## Stable public boundary

- Distribution: `astrology-graph-foundry`; import package: `astrology_graph_foundry`.
- Python: 3.10–3.12 are the declared pure-mode matrix. A live production platform is not supported until Slice 6 qualifies it.
- Commands: `astro-package` and `generate-daily-ephemeris`.
- Base dependency: `semantic-projection-core>=0.10.0,<0.11`; production uses the exact qualified artifact.
- Optional live dependency: `pyswisseph>=2.10,<2.11`; its presence alone is not a production qualification.
- Canonical graph: `canonical_astrology_graph.v1`, graph version 1.3.0.
- Canonical identity: `agf.source_chart_identity.v1.0.0`; callers should supply opaque `source_chart_id` through live Natal generation. The deterministic name fallback is compatibility behavior, not a production identity.
- Calculation provenance: `agf.calculation_provenance.v1.0.0`; calculation profile `agf.calculation_profile.v1.0.0`; normalization policy `agf.normalization_policy.v1.0.0`.

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
