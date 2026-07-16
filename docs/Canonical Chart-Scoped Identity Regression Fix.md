# Canonical Chart-Scoped Identity Regression Fix

## Problem

Legacy Foundry canonical Natal graphs used chart-local object IDs such as:

```text
natal:Moon
```

That was sufficient while each graph was consumed in isolation, but two projected
Natal graphs could produce the same downstream projected object ID when loaded
into one application-level graph or registry.

## Resolution

Canonical finalization now scopes legacy Foundry chart-object IDs beneath the
authoritative `source_chart_id`:

```text
natal:kevin:Moon
natal:ashley:Moon
```

The migration also:

- scopes derived and auxiliary objects;
- rewrites exact owner and object references throughout the package;
- regenerates relationship IDs from scoped endpoints;
- rebuilds canonical graph indexes;
- records the identity policy on the canonical graph;
- remains idempotent when applied repeatedly;
- leaves synthetic or externally supplied globally meaningful IDs untouched.

This applies defensively to existing legacy canonical packages during
finalization as well as newly generated packages.

## Projection context clarification

The reported context-ID difference:

```text
mythos.gameplay.synastry.v1
mythos.synastry.v1
```

was not present in the supplied Foundry canonical Natal packages. Custom
projection context IDs are owned by the downstream projection request and
application. Foundry therefore does not guess an alias or silently rewrite one
application context into another.

Mythos should issue both directional Synastry projections with one canonical
context ID. The chart-scoped Foundry IDs now make provenance comparison safe
once that downstream configuration is normalized.

## QA

Regression coverage checks:

- Kevin and Ashley canonical object-ID sets are disjoint;
- canonical IDs begin with their source chart scope;
- relationship endpoints and owner references are rewritten;
- indexes use scoped IDs;
- repeated finalization is idempotent;
- the one-command downstream QA runner reports canonical identity health and,
  when both fixtures are available, cross-chart collision counts.
