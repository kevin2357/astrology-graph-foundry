# Astrology Graph Foundry 0.4.2

## Chunk 3.alpha.2

This pass closes the final schema mismatch found during rich-corpus QA of the initial temporal source boundary.

## Changes

- Renamed temporal observation-state `strength` to `strength_label`.
- Typed `strength_label` as `string | null` in `canonical_temporal_activation_graph.v1`.
- Preserved source labels including:
  - `tight`
  - `very tight`
  - `partile / extremely tight`
  - `exact / ultra-partile`
- Added regression coverage for all four observed labels.
- Added inspector output summarizing the strength-label distribution.
- Bumped the distribution and import-package version to `0.4.2`.
- Documented the initial freeze of Foundry temporal stages A and B.
- Preserved a future-work item to validate gap-based pass segmentation against source candidate-retention behavior.

## Boundary status

```text
Foundry A: canonical temporal source contract       stable
Foundry B: Transit normalization/source bundle      stable
Core C: projected temporal activation graph         next
```

The freeze is an initial integration contract, not a claim that temporal source modeling can never evolve. Material changes should use explicit versioned contract evolution.
