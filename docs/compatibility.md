# Compatibility

## Runtime packages

| Component | Current Foundry expectation |
|---|---|
| Astrology Graph Foundry | published 0.6.0 at tag `astrology-graph-foundry-v0.6.0`; exact wheel SHA-256 `d1b357b1ec0e40faf7070b29e5c25d18e54c9507406518f26587aac46300aa95` |
| Semantic Projection Core | library compatibility range `>=0.10.0,<0.11`; production artifact is exactly 0.10.0 |
| Python | 3.10 or newer |
| Swiss Ephemeris | Optional `>=2.10,<2.11`; required only for live calculation |

Windows installs also require the declared `tzdata>=2024.1` dependency so IANA timezone normalization works in clean environments. Release deployments pin its exact artifact through the outer lock.

Foundry's library metadata permits the SPC 0.10 release line. The release handoff pins SPC 0.10.0 wheel SHA-256 `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`. This digest must be independently reverified during release qualification.

Use `astro-package doctor --json` to compare installed distribution versions with imported engine versions. Worker startup may assert `astro-package doctor --require-mode saved|projection|live --json`; failure exits with status 2 and stable failure codes. `live` proves dependency availability only, not that a Swiss Ephemeris data set has been release-qualified.

## Runtime modes

| Mode | Required runtime | Guarantee and limitation |
|---|---|---|
| Saved | AGF and its packaged schemas | Reads, validates, adapts, and transforms existing packages; cached input does not recreate original calculation provenance. |
| Projection | Saved mode plus compatible SPC | Projects canonical/static or supported temporal handoffs. Production additionally requires the exact qualified SPC wheel/hash and pinned projection resources. |
| Live | AGF plus pyswisseph and qualified ephemeris data | Calculates charts. Availability is distinct from production qualification of Python, platform, wrapper, library, and data hashes. |

The AstroWoof live candidate is CPython 3.11 on glibc-based Linux x86-64 with the published `pyswisseph==2.10.3.2` manylinux wheel (SHA-256 `e00d7e08aeafe00938603bc118874b6ca7871c5aaa55aafca8fa2c6d76aff812`). It explicitly requests Moshier, uses no external ephemeris files, and disables optional Chiron/asteroid/fixed-star inputs. See [Qualified Live Calculation Profile](Qualified%20Live%20Calculation%20Profile.md).

AGF emits complete packages or raises an error. It does not advertise a partial-but-valid Natal artifact contract. `calculation_warnings` may describe deliberately skipped optional objects; warnings do not turn a structurally incomplete package into success.

Validation and incompatibility errors are terminal for the same request/configuration. Missing packages, corrupt resources, unsupported contract versions, and provider/data incompatibility are deployment/configuration failures. Transient filesystem or provider infrastructure failures may be retried only after the orchestration owner classifies them; AGF does not make a universal retry promise.

See [Runtime and Contract Inventory](Runtime%20and%20Contract%20Inventory.md) for the release-facing schema inventory and [AstroWoof API Worker Handoff](AstroWoof%20API%20Worker%20Handoff.md) for the candidate integration boundary.

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
