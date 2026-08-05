# Compatibility

## Runtime packages

| Component | Current Foundry expectation |
|---|---|
| Astrology Graph Foundry | 0.5.x |
| Semantic Projection Core | 0.10.0 or newer compatible release |
| Python | 3.10 or newer |
| Swiss Ephemeris | Optional; required only for live calculation |

Foundry declares `semantic-projection-core>=0.10.0`. Repeatable production workflows should additionally pin a tested SPC release rather than relying on an unconstrained newest version.

Use `astro-package doctor --json` to compare installed distribution versions with imported engine versions. A mismatch commonly means an editable dependency was changed without being reinstalled.

## Static projection boundary

SPC 0.10.0 accepts Foundry canonical source graph version `1.3.0`. A static handoff consists of:

- `canonical_astrology_graph`;
- optional `structural_evidence_graph`;
- source identity;
- source registries needed to resolve compact references.

Profiles resolve by exact profile ID and profile version:

| Bundled profile | Profile version |
|---|---:|
| `orthodox_astrology.v1` | 1.0.0 |
| `cognitive_architecture_demo.v0` | 0.2.0 |
| `woofmapped_astrology.v0` | 0.1.0 |

Source coverage is profile-aware. Mapped, excluded-by-selection-policy, outside-scope, and eligible-but-unmapped rows are distinct outcomes.

## Temporal projection boundary

The frozen supported route is:

```text
canonical_temporal_activation_graph.v1 1.0.0
→ temporal_projection_source_bundle.v1 1.0.0
→ temporal_projection_request.v1
→ projected_temporal_activation_graph.v1
```

The bundle retains `consumer_status=reserved_for_semantic_projection_core_temporal_support` as a version-1.0.0 compatibility token. SPC 0.10.0 executes this route; the historical token does not indicate otherwise.

Static projection of Transit packages remains unsupported. Export a temporal source bundle and use SPC's temporal route.

## Change discipline

- Version source and projected contract changes explicitly.
- Do not infer compatibility from filenames.
- Pin profile and context versions for reproducible artifacts.
- Preserve deterministic route receipts when source-to-result traceability matters.
- Coordinate any change to the frozen temporal consumer-status token across both repositories.
