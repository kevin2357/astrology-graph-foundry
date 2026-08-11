# Astrology Graph Foundry documentation

These pages describe the published Astrology Graph Foundry 0.7.0 release. Documents under
[`history/`](history/) are implementation records and are not normative.

Release notes: [published 0.7.0](releases/0.7.0.md); [previous 0.6.0](releases/0.6.0.md).

Astrology Graph Foundry calculates astrology packages and compiles canonical source graphs, structural evidence, temporal activation graphs, and consumer-oriented materializations. Semantic Projection Core owns target-domain projection. Reasoning, claims, game rules, report planning, and publication remain downstream.

AstroWoof is one downstream consumer, not an organizing assumption of Foundry.
Cross-repository AstroWoof integration policy, product contracts, release
requirements, and API decisions live in the
[astrowoof-project repository](https://github.com/kevin2357/astrowoof-project).
Foundry remains authoritative for calculation behavior, canonical graph
semantics, schemas, and implementation.

## Start here

- [How to Use Astrology Graph Foundry](How%20to%20Use%20Astrology%20Graph%20Foundry.md) — installation and CLI workflows.
- [Architecture](architecture.md) — package, graph, timing, and downstream boundaries.
- [Developer Manual](Astrology%20Graph%20Foundry%20Developer%20Manual.md) — implementation and consumer guidance.
- [Package Types](package_types.md) — current pipeline and materialization status.
- [Compatibility](compatibility.md) — Foundry/SPC, graph, temporal, and profile-version expectations.
- [Runtime and Contract Inventory](Runtime%20and%20Contract%20Inventory.md) — installed modes, public contracts, guarantees, and failures.
- [Qualified Live Calculation Profile](Qualified%20Live%20Calculation%20Profile.md) — released Linux/Moshier qualification boundary.
- [AstroWoof API Worker Handoff](AstroWoof%20API%20Worker%20Handoff.md) — published artifact lock and worker integration boundary.
- [Release Engineering](Release%20Engineering.md) — reproducible build, installed qualification, private dependency, publication, and cleanup controls.
- [Architecture Decision Records](decisions/README.md) — durable rationale for identity, provenance, and live-profile choices.
- [Ideas and Improvements](ideas_and_improvements.md) — active Foundry-owned roadmap.

## Calculation and package guides

- [Provider Architecture](provider_architecture.md)
- [Live Natal Generation](live_natal_generation.md)
- [Rich Natal Facts](rich_natal_facts.md)
- [Bounded Birth-Time Natal Calculation](Bounded%20Birth-Time%20Natal%20Calculation.md) — published 0.7.0 contract and uncertainty model.
- [Bounded Natal Consumer Handoff](Bounded%20Natal%20Consumer%20Handoff.md) — API, SPC, SBE, storage, caching, and migration obligations.
- [Near-Term Engineering Outlook](Near-Term%20Engineering%20Outlook.md) — visible but non-normative follow-up opportunities and sprint questions.
- [Unified Transit Dataset](transit_dataset.md)
- [Legacy Transit Period Note](transit_period_dataset.md)
- [Transit Streaming Profiles and Game Index](Transit%20Streaming%20Profiles%20and%20Game%20Index.md)
- [Synastry and Composite Pipelines](synastry_and_composite_pipelines.md)
- [Timing Pipelines](timing_pipelines.md)
- [TransitableChart Interface](transitable_chart.md)
- [Logging](logging.md)
- [Workflow Tools](../tools/README.md)

## Canonical and cross-repository contracts

- [Canonical Identity and Projection Context Ownership](Canonical%20Identity%20and%20Projection%20Context%20Ownership.md)
- [Canonical Identity Migration Guide](Canonical%20Identity%20Migration%20Guide.md)
- [Calculation Provenance and Hashing](Calculation%20Provenance%20and%20Hashing.md)
- [Canonical Temporal Activation Graph](Canonical%20Temporal%20Activation%20Graph.md)
- [Semantic Graph Ingestion](semantic_graph_ingestion.md)
- [Semantic Projection Integration](Semantic%20Projection%20Integration.md)

Semantic Projection Core's current documentation is authoritative for projection requests, profiles, contexts, projected contracts, term registries, materialization, temporal execution, Synastry preparation, audit, and diagnostics.

## Ecosystem and future-layer design

These documents describe downstream boundaries and research direction. They are not claims that the corresponding reasoning or publishing systems are implemented in Foundry.

- [Astrology Ecosystem Architecture](Astrology%20Ecosystem%20Architecture.md)
- [Consumer Cookbook](Consumer%20Cookbook.md)
- [Multi-Pipeline Semantic Synthesis](Multi-Pipeline%20Semantic%20Synthesis.md)
- [Report Blueprint Specification](Report%20Blueprint%20Specification.md)

## Implementation history

Completed release notes, migrations, regression records, and the former in-repository projection extraction history are retained under [`history/`](history/). Historical files explain why contracts evolved but may describe superseded package shapes, ownership, commands, or implementation status.

The [Foundry 0.6.0 identity and release retrospective](history/foundry-development/Foundry%200.6.0%20Identity%20and%20Release%20Retrospective.md) promotes the day's reusable lessons without turning sprint chronology into a current contract.

## Documentation authority

Current code and packaged JSON Schemas are the executable contracts. Current reference pages explain those contracts; guides show supported workflows. When historical prose conflicts with code, schemas, or this index, treat the current implementation as authoritative.
