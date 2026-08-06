# ADR-0001: Accept Opaque Caller-Owned Canonical Chart Identity

- **Status:** Accepted
- **Date:** 2026-08-05
- **Applies from:** Astrology Graph Foundry 0.6.0
- **Decision owner:** Astrology Graph Foundry

## Context

Natal generation historically derived `source_chart_id` from a slug of display name. Renaming a subject therefore changed canonical object and relationship IDs, while equal normalized names could collide. Saved-package paths already carried chart identity through much of the graph boundary, but ordinary live generation could not accept a caller's stable identity.

AGF must support durable consumers without learning their user, dog, account, database, or product semantics. Calculation fingerprints and projection contexts cannot substitute for chart lineage.

## Decision

AGF accepts optional `source_chart_id` through supported live Natal Python, CLI, provider, pair-input, and helper boundaries. A valid value is a bounded namespace-safe ASCII string that AGF preserves exactly. The caller owns uniqueness and lifecycle.

Production callers supply an explicit stable value. Equal explicit carriers agree; conflicting carriers fail closed. Display name is descriptive only when explicit identity exists. The deterministic name-derived fallback remains for legacy compatibility but is not a production identity contract.

Canonical object IDs, relationship IDs, indexes, structural evidence, registries, claims, provenance references, and other exact references scope beneath the resolved chart identity. Deliberate A-to-B changes use whole-package rescoping or regeneration; isolated field edits are invalid.

Synastry preserves directional participant order. Composite and Davison use order-independent IDs derived from sorted participant chart identities under `relationship_chart_identity_v1.0.0`. Temporal packages preserve target chart identity and keep technique/window sensor identity separate.

## Alternatives rejected

- **Continue using display-name slugs:** collision-prone and unstable under rename.
- **Use a calculation hash:** identical geometry can belong to distinct chart lineages, and corrected calculations can remain within one subject lineage.
- **Accept product database objects or semantics:** leaks application ownership into reusable infrastructure.
- **Use projection context:** one canonical chart may be projected many ways; context is downstream-owned.
- **Silently choose the first identity carrier:** hides corrupt mixed-lineage packages.

## Consequences

Explicit identity is additive at the input boundary, but it materially changes canonical identity semantics and justified the 0.6.0 minor release. Semantic identity policy is `semantic_sensor_identity_v1.1.0`; canonical graph topology remains version 1.3.0. Legacy packages remain readable, but regenerated Composite/Davison IDs may differ from historical name-derived output.

See [Canonical Identity and Projection Context Ownership](../Canonical%20Identity%20and%20Projection%20Context%20Ownership.md) and the [migration guide](../Canonical%20Identity%20Migration%20Guide.md).
