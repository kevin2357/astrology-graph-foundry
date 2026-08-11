# Slice 1 — AGF/SPC Runtime and Ownership Decoupling

**Gate status:** Approved

## Outcome

AGF 0.8.0 is independently installable and executable without Semantic Projection
Core. AGF owns calculation, canonical source graphs, structural evidence,
registries, and projection-neutral static and temporal wire artifacts. SPC owns
projection requests, execution, target profiles, target ontologies, projected
materializations, and projection diagnostics.

## Public migration

- Removed mandatory distribution dependency `semantic-projection-core`.
- Removed package-root `project_dataset`, projection-context, projection-summary,
  and unmapped-threshold exports.
- Removed `astro-package project` and projection doctor mode.
- Removed `astrology_graph_foundry.projection_adapter`.
- Synastry `analysis_view` now emits source-factual
  `source_factual_relationship_handoff_v3`, explicitly says projection was not
  performed, and includes canonical source and structural evidence. Consumers that
  need projected Synastry semantics must invoke SPC themselves.
- Preserved canonical and temporal projection-source contracts. Their names describe
  their wire purpose; they do not transfer projection execution ownership to AGF.

This is a package/API/CLI/view break and therefore uses AGF 0.8.0. It does not alter
the canonical graph schema solely to reflect repository ownership.

## Qualification

The clean installed-runtime gate proves that AGF's base wheel operates with no SPC
module available and no SPC dependency metadata. Installed saved doctor,
runtime-manifest, `astro-package`, and `generate-daily-ephemeris` surfaces pass.
Exact and bounded live Natal generation pass under the qualified Linux/Moshier
profile while SPC imports are actively forbidden. The installed-wheel suite reports
226 passing tests.

A separate integration environment independently built and installed AGF 0.8.0 and
SPC 0.10.0 wheels. SPC projected the serialized AGF Natal fixture while preserving
source identity, and every qualified canonical object/relationship reference
resolved. This proves wire compatibility without making either package a runtime
dependency of the other.

See:

- [no-SPC installed qualification](no-spc-installed-qualification.json)
- [independent wire compatibility](independent-wire-compatibility.json)

## Finding promoted from QA

SPC source references are qualified names such as `canonical:object:<id>` and
`canonical:relationship:<id>`, whereas canonical graph rows store `<id>`. A verifier
must compare the namespace-qualified reference target, not the literal strings.
The first harness version missed this distinction; the corrected harness retains it
as executable integration knowledge.

## Gate disposition

All planned technical criteria are satisfied and the product owner approved the
slice. Commit and push establish the clean release-candidate boundary; immutable
0.8.0 qualification and publication follow as a separately controlled pass.
