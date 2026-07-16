# Canonical Identity and Projection Context Ownership

## Chart-scoped canonical IDs

Foundry canonical Natal chart objects use the authoritative `source_chart_id` as
their global identity scope.

Examples:

```text
natal:kevin:Moon
natal:ashley:Moon
```

Derived and auxiliary rows are scoped beneath the same chart identity. Canonical
relationship IDs are regenerated from the scoped endpoints, and exact object or
relationship references elsewhere in the finalized package are migrated with
them.

This prevents projected object-ID collisions when two independently projected
Natal graphs are later assembled into one application-level graph or registry.

The finalization path also migrates legacy Foundry canonical packages whose
objects still use local IDs such as `natal:Moon`. Repeated finalization is
idempotent.

## Projection context IDs are downstream-owned

A projection context identifier such as:

```text
mythos.gameplay.synastry.v1
```

is not a property of a Foundry canonical Natal or Synastry graph. It belongs to
the downstream projection request and its owning application or Semantic
Projection Core profile.

Foundry source packages intentionally do not invent, alias, or normalize custom
application context IDs. Two directional projections of the same application
relationship should be issued with the same canonical downstream context ID.
If one direction uses `mythos.gameplay.synastry.v1` and the reverse direction
uses `mythos.synastry.v1`, that inconsistency must be corrected in the Mythos
projection context/configuration rather than in Foundry source data.

Foundry guarantees stable source-chart identity and globally scoped canonical
object/relationship IDs so downstream request provenance can be compared
reliably.
