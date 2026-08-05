# Canonical Identity Sprint Log

This log is append-only during execution. Planning entries do not represent completed implementation slices.

## 2026-08-05 — Planning Baseline

- Scope authorized: read-only investigation and sprint planning only. No production code, cross-repository edits, commits, tags, pushes, or publication authorized.
- Repository start: `C:\dev\github\astrology-graph-foundry` on `main`, tracking `origin/main`, clean before sprint skeleton creation.
- Starting commit: `259058d` (`Link AstroWoof integration authority`).
- Recent relevant history reviewed: SPC 0.10 alignment, documentation reorganization, helper tools, cleanup, and AstroWoof integration authority.
- Distribution evidence: `astrology-graph-foundry` 0.5.0, package `astrology_graph_foundry`, Python `>=3.10`, SPC declaration `>=0.10.0`, optional `pyswisseph>=2.10`, and two console scripts.
- Identity finding: supported live Natal input has no explicit stable chart identity. Saved-package finalization already recognizes `transitable_chart.chart_identity.chart_id` and several metadata identity fields. The ordinary fallback is `natal:<slug(display name)>`.
- Migration finding: current finalization rewrites legacy IDs, relationship endpoints/IDs, nested exact references, and indexes, and is covered for idempotence. A general explicit-ID-A to explicit-ID-B migration is not yet a proven contract.
- Package-family finding: synastry, composite, Davison, transit, returns, and temporal paths do not all derive identity in the same way; relationship-chart identity needs an explicit review rather than accidental inheritance from the Natal change.
- Downstream finding: SPC 0.10.0 consumes source chart/sensor identity and incorporates source identity in projected request identity. Projection context remains downstream-owned.
- AstroWoof finding: its accepted contracts and API work distinguish dog identity, birth-data version, calculation-input hash, subject-calculation hash, and request hash. The AGF input currently lacks `source_chart_id`; the new contract must preserve these distinctions.
- Cross-repository state: SPC, SBE, API, and `astrowoof-project` were inspected read-only. The API repository contained unrelated existing documentation changes and was not touched.
- Initial recommendation for Gate 1: use `source_chart_id`; validate a bounded namespace-safe opaque value; preserve it exactly; explicit value wins; reject conflicting explicit carriers; retain name-derived identity only as an explicit compatibility fallback if approved.
- Version remains undecided. Planning recommendation is a package minor release (likely 0.6.0), with graph/schema/identity-policy versions determined by the actual accepted contract impact.
- No slice result exists. The `results` directory is intentionally empty.

## 2026-08-05 — Slice 1 Identity Contract Audit

- Authorization: sprint plan approved; Slice 1 contract audit begun. Production implementation remains out of scope until this gate is approved.
- Starting state rechecked: branch `main` at `259058d`; only the approved, uncommitted sprint planning tree was present.
- Traced identity carriers through `BirthData`, Natal construction, CLI argument builders, semantic finalization, canonical/structural schemas, `TransitableChart`, temporal adapters, projection adapters, tools, fixtures, and package-family tests.
- Confirmed that explicit identity already enters saved-package paths through `transitable_chart.chart_identity.chart_id` and metadata aliases, but ordinary live Natal generation cannot supply it.
- Confirmed that current alias selection is silent first-truthy precedence. The proposed contract instead accepts equal duplicates and rejects differing explicit values.
- Confirmed that current object migration only activates when an object begins with historical `natal:`. This is not sufficient evidence for arbitrary explicit scope or A-to-B rescoping and is assigned to Slice 3.
- Confirmed that `source_chart_id` is passed into canonical graphs, structural evidence, source registries, projection requests, and temporal target validation; it is therefore the least disruptive public field name.
- Decision candidate recorded in `results/SLICE 1 - Identity Contract Decision.md`: bounded namespace-safe ASCII value, exact preservation, explicit identity over display-name fallback, conflict rejection, caller-owned uniqueness, no product semantics.
- Compatibility candidate: retain deterministic name-derived identity as a documented legacy fallback; production integrations must supply explicit identity.
- Relationship finding: Synastry can consume participant identities, while Composite/Davison derivations remain name/label-sensitive and require the independent Slice 4 decision.
- Version candidate: AGF 0.6.0 and an incremented semantic identity-policy version; exact schema/interface changes wait for implementation evidence.
- Gate tests and repository checks follow in the next log entry.

## 2026-08-05 — Slice 1 Gate Evidence

- The first test command could not run because no `python` executable was present on `PATH`; no repository behavior was exercised by that failed command.
- Located the bundled workspace Python at `C:\Users\kevin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
- The bundled environment initially lacked pytest. A normal editable install could not resolve unpublished `semantic-projection-core>=0.10.0` from the package index.
- Installed declared test tools, then installed the local SPC 0.10.0 and AGF 0.5.0 checkouts editable into the bundled workspace environment. This changed only the external workspace runtime, not either repository.
- Focused identity/boundary gate: 48 tests passed in 2.32 seconds across chart scoping, semantic identity, downstream regressions, temporal activation/source bundles, Synastry projection, and temporal projection guards.
- Full regression gate: 119 tests passed in 3.15 seconds.
- No production source or schema was changed in Slice 1.
- Pending final gate checks: whitespace, `git diff --check`, actual diff review, and repository status.

## 2026-08-05 — Slice 1 Gate Ready for Review

- Reviewed the complete Slice 1 result and sprint-log additions against the approved plan.
- Confirmed the result distinguishes observed behavior, proposed binding decisions, recommended relationship direction, and deferred implementation/version choices.
- Confirmed that the gate contains a carrier/consumer matrix, validation and conflict rules, before/after behavioral expectations, schema/version impact, migration threat model, and required test matrix.
- Final repository validation completed after this entry; results are reported in the gate handoff.
- Slice 1 is paused for human approval. No files are staged and no commit has been created.
