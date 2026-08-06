# Architecture Decision Records

These records preserve consequential AGF-owned choices whose rationale should remain visible after sprint logs become historical. They complement executable contracts and current reference documentation; they do not replace schemas, tests, or release manifests.

Cross-system product and orchestration decisions belong in `astrowoof-project`. Projection-profile and target-ontology decisions belong in Semantic Projection Core.

| ADR | Status | Decision |
|---|---|---|
| [ADR-0001](ADR-0001%20-%20Accept%20Opaque%20Caller-Owned%20Canonical%20Chart%20Identity.md) | Accepted | Accept opaque caller-owned `source_chart_id` and scope canonical identity beneath it. |
| [ADR-0002](ADR-0002%20-%20Separate%20Chart%20Calculation%20Artifact%20and%20Projection%20Identity.md) | Accepted | Keep chart lineage, calculation basis, artifact bytes, and projection context as distinct identities. |
| [ADR-0003](ADR-0003%20-%20Qualify%20an%20Explicit%20Moshier%20No-File%20Live%20Profile.md) | Accepted | Qualify a narrow CPython 3.11/Linux/Moshier live profile with no external ephemeris files. |

Accepted ADRs describe the current 0.6.x contract. A later incompatible decision should supersede the relevant record rather than silently rewriting its rationale.
