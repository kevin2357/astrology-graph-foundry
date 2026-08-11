# Near-Term Engineering Outlook

**Status:** Living, non-normative planning context

**Authority:** Astrology Graph Foundry repository concerns only

This document preserves near-term engineering opportunities that are important
enough to remain visible but are not yet approved sprint commitments. Normative
behavior remains in the schemas, contract documentation, accepted ADRs, and released
artifacts.

## Completed candidate: decouple AGF from Semantic Projection Core

### Current state

AGF 0.8.0 candidate source has no SPC distribution or runtime dependency. The
projection adapter, Python exports, CLI command, and projection doctor mode are
removed. Synastry analysis now emits a source-factual handoff. Canonical graphs and
projection-neutral temporal exports remain intact.

### Accepted direction

- AGF's base installation should calculate, validate, serialize, reload, and inspect
  its artifacts without SPC installed.
- SPC should consume AGF artifacts through versioned schemas and documented wire
  contracts without importing AGF.
- Projection contexts, target ontologies, projection request identity, and projected
  artifacts remain SPC/downstream-owned.
- Cross-repository qualification should continue against exact immutable artifacts
  in an integration harness or consumer environment.
- A convenience command may orchestrate both packages, but it should live in an
  explicitly optional integration layer rather than making either core package a
  runtime dependency of the other.

### Remaining acceptance boundary

A clean AGF base wheel must install and pass saved/live workflows without SPC. A
clean SPC wheel must install and project a compatible saved fixture without AGF.
The integration gate must then install the two exact artifacts independently and
prove their wire compatibility, identity preservation, and evidence preservation.

## Completed: invariant terrestrial-frame semantics for bounded Natal

### Current state

The two August 2026 bounded-parity sprints implemented this work. Current unreleased
source evaluates Placidus and Whole Sign terrestrial frames minute by minute,
preserves cusp/angle ranges, and promotes independently invariant house membership,
cusp signs/rulers, angle signs/relationships, sect/triplicity, Vertex house, and
branched Fortune/Spirit semantics. Provider failures remain family-scoped and no
representative degree is emitted.

Bounded graph 1.7.0 and calculation profile 1.12.0 express the completed contract.
Published 0.7.0 remains the immutable baseline until a later release is explicitly
authorized.

### Remaining work

- SPC and SBE need explicit bounded graph 1.7.0 compatibility sprints.
- Transit and Synastry need distinct range-aware contracts; they may reuse evidence
  but cannot align bounded participants by sample index.
- Additional house systems require individual qualification.
- Optional ephemeris files and catalogs require separately pinned data profiles.
- Pattern, score, and claim semantics remain unavailable rather than inferred from
  invariant-subgraph row counts.
