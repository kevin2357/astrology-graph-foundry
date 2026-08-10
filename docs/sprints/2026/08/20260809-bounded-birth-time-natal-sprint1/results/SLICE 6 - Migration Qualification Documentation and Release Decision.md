# Slice 6 - Migration, Qualification, Documentation, and Release Decision

**Status:** Gate-ready for review; uncommitted and unpublished

**Starting boundary:** `f3c1859`

## Outcome

The bounded Natal feature is documented, versioned, and qualified as the AGF 0.7.0
release candidate. Exact contracts remain unchanged. A clean installed Linux/Python
3.11 wheel generated and validated a bounded package, projected an exact package
through SPC 0.10.0, and operated in saved mode after pyswisseph removal. Publication
remains a separate explicitly approved release action.

## Version decision

AGF advances to 0.7.0 because this work adds a public CLI/Python input family,
dataset, canonical graph, evidence/provenance model, schemas, and capability
boundary. A patch release would understate consumer impact. Exact Birth Data v1,
Natal Dataset 1.1.0, canonical graph 1.3.0, and SPC 0.10.0 compatibility do not
change.

Bounded versions begin at:

- Bounded Birth Data v1;
- Bounded Natal Dataset 1.0.0;
- bounded canonical astrology graph 1.0.0;
- bounded calculation provenance 1.0.0;
- bounded normalization policy 1.0.0; and
- interval proof profile 1.0.0.

## Migration and consumer handoff

Durable documentation now distinguishes the published 0.6.0 baseline from the
unpublished 0.7.0 candidate and covers CLI/Python use, API normalization and cache
identity, immutable artifacts, warned-noon migration, evidence preservation, error
classification, current exact-only rejections, and SPC/SBE follow-on obligations.

Warned-noon artifacts are historical exact-policy artifacts. They cannot be relabeled
as bounded; consumers must recalculate from original knowledge and preserve lineage.

## Reproducible build

Two isolated builds used `SOURCE_DATE_EPOCH=1786320000`, setuptools 83.0.0, and
wheel 0.47.0. Both produced byte-identical
`astrology_graph_foundry-0.7.0-py3-none-any.whl` artifacts with SHA-256:

`181190606a9373ef3bb091803b015c2a962155e289aa04e30a20740e08e4bd05`

## Clean installed qualification

A temporary `python:3.11-slim` container received only the candidate wheel and exact
SPC 0.10.0 wheel, then installed pyswisseph 2.10.3.2 and jsonschema. Installed
execution proved:

- distribution/runtime version agreement at 0.7.0;
- both console entry points load and render help/version;
- live doctor readiness;
- 38 packaged schemas with runtime-manifest hash
  `64178c9085474eb94f7b90bd14524e883d7e941764d9ecd13779a592b1b80018`;
- schema-valid unknown-time Moshier generation with 11 invariant objects and 13
  relationships, no scalar precision, no dangling references, and resolvable
  uncertainty evidence;
- exact AGF-to-SPC Woofmap projection with 17 objects, 61 relationships, and source
  identity preserved; and
- saved/package-resource readiness after pyswisseph was uninstalled.

The generated bounded artifact byte hash was
`3f2eb682ca6e45cff54b9ed1a121344863039d584ac632392bd50c764aad6f01`.

## Source qualification

The first source-suite run correctly found stale editable distribution metadata
(0.6.0 versus runtime 0.7.0). Refreshing the temporary editable installation resolved
the environment mismatch. Final result: **214 passed in 17.40 seconds**. The only
warning reported that pytest could not update its cache directory; no test failed.

## Release decision

Do not tag or publish from this sprint gate. The candidate behavior is qualified,
but immutable publication requires explicit release authorization and a commit-bound
manifest/checksum set. AstroWoof production readiness also requires the planned SPC
and SBE bounded-consumer sprints plus API/frontend acceptance. AGF may be released
independently later, but such publication must not imply end-to-end bounded-reading
support.

Compact qualification evidence:
[`installed-qualification.json`](installed-qualification.json).

## Exit assessment

The AGF-owned bounded Natal objective is complete subject to Gate 6 review and the
approved commit. Publication, downstream enablement, and future bounded Transit or
Synastry semantics remain separate work.
