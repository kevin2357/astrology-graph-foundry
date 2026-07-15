# Semantic Projection Integration

Astrology Graph Foundry produces `canonical_astrology_graph` and `structural_evidence_graph`. Its `projection_adapter.py` converts saved SDK packages and source registries into generic Semantic Projection Core requests.

The adapter also rejects temporal activation packages until `projected_temporal_activation_graph.v1` is implemented. Projection profiles, contracts, schemas, term registries, rendering primitives, and materialization policy are external.

Install the sibling project during development:

```bat
python -m pip install -e ..\semantic-projection-core
```
