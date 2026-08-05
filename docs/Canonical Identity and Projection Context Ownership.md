# Canonical Identity and Projection Context Ownership

## Authoritative chart identity

Foundry 0.6.x accepts an optional caller-owned `source_chart_id` through the
supported live Natal Python, CLI, and helper-tool boundaries. Production callers
should always supply it. It answers “which canonical chart is this?” and is not
a display name, database object type, calculation fingerprint, request ID, or
projection context.

The identifier is an opaque, namespace-safe ASCII string. It must be 1–200
characters, start with an ASCII letter or digit, and then contain only ASCII
letters, digits, `.`, `_`, `:`, `/`, or `-`. Foundry validates but does not slug,
case-fold, trim, or otherwise rewrite an accepted value. Uniqueness and lifecycle
are caller responsibilities.

When explicit identity is supplied, display-name changes do not change canonical
object or relationship IDs. If no explicit carrier exists, Natal retains the
deterministic legacy fallback `natal:<slug(display name)>`. That fallback is
collision-prone and must not be used for production persistence, cache lineage,
or immutable reading references.

## Precedence and conflict handling

Finalization collects every non-null explicit identity carrier in a Natal
package, including the transitable-chart descriptor and package, person, and
Natal metadata. Equal values agree. Distinct values fail closed; Foundry never
silently chooses one carrier over another. Display name participates only when
there is no explicit carrier.

Canonical object IDs are scoped beneath the resolved identity. Derived and
auxiliary rows inherit the same scope; canonical relationship IDs are rebuilt
from scoped endpoints; indexes, source registries, structural evidence, claims,
provenance references, and other exact nested references are synchronized.
Repeated finalization under one identity is idempotent.

The emitted identity policy is `semantic_sensor_identity_v1.1.0`. Canonical
graph schema version remains `1.3.0`: the topology and required fields did not
change, while accepted identity values are now more tightly validated.

## Relationship and temporal packages

Synastry preserves participant `source_chart_ids` in person-A/person-B order
because directional aspects and house overlays depend on role order. Composite
and Davison generation use order-independent, versioned relationship-chart IDs
derived from sorted participant chart identities. Their identity policy is
`relationship_chart_identity_v1.0.0`. Historical saved packages without explicit
identity retain their documented compatibility behavior.

Transit, return, and other temporal packages carry target chart identity rather
than inventing a new subject identity. Conflicting explicit target carriers are
rejected. Calculation-window, technique, and sensor-instance identity remain
distinct from target `source_chart_id`.

## Projection context IDs are downstream-owned

A projection context identifier such as `astrowoof.woofmap.natal.v1` is not a
property of a Foundry source graph. It belongs to the downstream projection
request and its owning application or Semantic Projection Core profile.

Foundry does not invent, alias, or normalize application context IDs. The same
canonical chart may be projected into multiple contexts without changing its
source identity. Foundry guarantees scoped source identity and references so
downstream provenance can be compared reliably; SPC owns projection identity
and target-domain semantics.

## Migration

Legacy local-ID packages are upgraded during finalization. A deliberate change
from one already explicit Natal identity to another must use the supported
`rescope_natal_package_source_chart_id` operation so every scoped ID and exact
reference migrates together. See the
[Canonical Identity Migration Guide](Canonical%20Identity%20Migration%20Guide.md).
