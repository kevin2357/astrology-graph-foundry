# Semantic Projection Integration

Astrology Graph Foundry produces `canonical_astrology_graph` and `structural_evidence_graph`. Its `projection_adapter.py` converts saved SDK packages and source registries into generic Semantic Projection Core requests.

The static adapter rejects temporal activation packages because they require the dedicated temporal route. Foundry exports `temporal_projection_source_bundle.v1`; Semantic Projection Core 0.10.0 validates and adapts that bundle, executes projection to `projected_temporal_activation_graph.v1`, materializes the selected view, and can emit a deterministic route receipt. Projection profiles, projected contracts, schemas, term registries, rendering primitives, and materialization policy are external.

Install the sibling project during development:

```bat
python -m pip install -e ..\semantic-projection-core
```

Foundry's frozen temporal bundle 1.0.0 retains the historical
`reserved_for_semantic_projection_core_temporal_support` consumer-status token.
SPC validates that exact value for compatibility; it no longer indicates that
execution is unavailable.
