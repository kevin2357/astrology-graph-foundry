# Semantic Projection Integration

Astrology Graph Foundry produces `canonical_astrology_graph`,
`structural_evidence_graph`, and projection-neutral temporal source bundles.
Semantic Projection Core or orchestration consumes those serialized contracts.
AGF no longer imports SPC, constructs projection requests, executes projection, or
materializes projected views.

For AstroWoof-specific orchestration, retention, compatibility, and provenance
policy, see the project-level
[Canonical Chart Integration](https://github.com/kevin2357/astrowoof-project/blob/main/docs/architecture/Canonical%20Chart%20Integration.md)
and
[Canonical Natal Chart Consumer Contract](https://github.com/kevin2357/astrowoof-project/blob/main/docs/contracts/Canonical%20Natal%20Chart%20Contract.md).
Those documents do not transfer canine ontology or product behavior into Foundry.

Foundry exports `temporal_projection_source_bundle.v1`; Semantic Projection Core
validates and adapts that bundle, executes projection, and owns projected
materialization. Projection profiles, contexts, projected contracts, term
registries, rendering primitives, and materialization policy are external.

Install the sibling project only for an external integration harness:

```bat
python -m pip install -e ..\semantic-projection-core
```

Foundry's frozen temporal bundle 1.0.0 retains the historical
`reserved_for_semantic_projection_core_temporal_support` consumer-status token.
SPC validates that exact value for compatibility; it no longer indicates that
execution is unavailable.

## Migration from AGF 0.7

- Replace `astrology_graph_foundry.project_dataset` and related projection exports
  with SPC-owned APIs.
- Replace `astro-package project` with an SPC or orchestration command.
- Replace `doctor --require-mode projection` with component-specific startup checks.
- Synastry analysis output is now a source-factual handoff; it contains no
  `orthodox_relationship_projection` or projection-coverage claim.
- Continue using AGF temporal export commands: they serialize source contracts and
  do not execute projection.
