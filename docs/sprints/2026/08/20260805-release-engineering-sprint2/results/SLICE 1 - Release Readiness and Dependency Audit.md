# Slice 1 - Release Readiness and Dependency Audit

## Outcome

AGF's Sprint 1 boundary is frozen at
`885223bbd8126b88f22399de7f889387c6180b7b`. Version 0.6.0 is confirmed as the
release candidate: the live-Natal input remains additive and legacy artifacts
remain readable, while canonical identity is a material public contract and new
Composite/Davison identity intentionally changed.

The pure-Python wheel boundary is viable. A disposable audit build produced
`astrology_graph_foundry-0.6.0-py3-none-any.whl`, contained both console-entry
metadata, the license, and all 33 declared JSON Schemas, and passed the source
baseline. This wheel is audit evidence only, was removed, and is not a release
candidate.

The material unresolved risks are live-provider packaging and licensing. PyPI's
current `pyswisseph==2.10.3.2` publishes binary wheels only through CPython 3.11.
Python 3.12 requires a controlled source build or a separate Python 3.11
domain-worker decision. Swiss Ephemeris is dual-licensed under AGPL or its
Professional License; the project owner must make and document that choice before
distribution of dependent software or public-service activation.

## Candidate identity and publication shape

- Distribution: `astrology-graph-foundry`
- Import package: `astrology_graph_foundry`
- Candidate version: `0.6.0`
- Proposed annotated tag: `astrology-graph-foundry-v0.6.0`
- Canonical graph: `1.3.0`
- Natal package schema: `1.1.0`
- Semantic identity: `semantic_sensor_identity_v1.1.0`
- Relationship identity: `relationship_chart_identity_v1.0.0`
- Proposed public assets: one qualified universal wheel, `SHA256SUMS.txt`, and
  `release-manifest.json`
- Proposed sdist policy: do not publish an unqualified alternate installation
  path. Source remains available through the immutable Git tag/archive.

The tag naming matches SPC's component-qualified release convention and avoids a
generic `v0.6.0` tag whose repository context can be lost in manifests.

## Build and dependency lock proposal

Use `build==1.5.0`, `setuptools==83.0.0`, and `wheel==0.47.0` under a controlled
`SOURCE_DATE_EPOCH`. Slice 7 must build from two clean exports and prove byte
identity; these proposed versions become authoritative only after that proof.

Keep `semantic-projection-core>=0.10.0` in general library metadata so AGF does
not pretend a hash lock can be represented by wheel dependency metadata. The
AstroWoof production handoff must install the exact release asset:

- tag: `semantic-projection-core-v0.10.0`
- commit: `68f11c56ff1ad26873958cf955b7f3699895e870`
- wheel: `semantic_projection_core-0.10.0-py3-none-any.whl`
- SHA-256: `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`

The wheel was downloaded again from the GitHub release, independently hashed,
and removed. GitHub's asset digest agrees.

For live mode, provisionally pin `pyswisseph==2.10.3.2`. Verified PyPI wheel
hashes include:

- Windows x86-64 CPython 3.10:
  `9311eac2a95dd22d1b49f7ff963807a300dd64fd178f89d92ea3d864f372154e`
- Windows x86-64 CPython 3.11:
  `2b4a24f7954e1456ecbd3bb091b7c2a8a2e9838ff56e0d8af0f9e897fa84eb25`

There is no CPython 3.12 binary in the authoritative PyPI file inventory on any
platform. The API currently requires Python `>=3.12,<3.13`, so those Windows
wheels cannot be the production handoff.

## Supported-mode matrix proposal

| Mode | Candidate claim | Qualification required |
|---|---|---|
| Pure import/schema/adapter | CPython 3.10-3.12; universal wheel | Installed-wheel smoke outside checkout on Windows 3.12; CI wheel jobs on Linux 3.10-3.12 |
| Saved/cached package workflows | CPython 3.10-3.12 without pyswisseph | Meaningful wheel-only CLI and fixture replay |
| Static/temporal projection | Same pure matrix plus exact SPC wheel | Installed AGF-to-SPC proof and exact asset hashes |
| Live calculation for local Windows | CPython 3.10 or 3.11 with exact PyPI wheel | Controlled live test; no claim for Windows 3.12 |
| AstroWoof production live worker | Linux x86-64 CPython 3.12, matching API | Must qualify a controlled source-built pyswisseph wheel, compiler/base-image identity, and ephemeris data; otherwise blocked |

macOS, 32-bit, musl, ARM, and untested interpreter combinations remain outside
the release claim even if upstream artifacts exist.

## Runtime and contract inventory

Supported pure surfaces are package import, schema/resource discovery, doctor,
saved-package reading/materialization, cached-provider generation, AGF projection
adapters, and temporal export. Static and temporal projection require SPC but not
Swiss Ephemeris. Live Natal, daily ephemeris, and live timing/relationship paths
require pyswisseph and an explicit ephemeris policy.

The release-facing schema set is the complete packaged set of 33 JSON Schemas.
The manifest must distinguish mature contracts from scaffold package schemas;
packaging a schema does not promote its pipeline to production support. Primary
AstroWoof contracts are Birth Data v1, Natal Dataset v1.1.0, Canonical Astrology
Graph 1.3.0, Structural Evidence Graph 1.3.0, semantic-boundary bundle,
TransitableChart 1.0.0, evidence provenance, and temporal source/activation
contracts where applicable.

AGF requests `FLG_SWIEPH | FLG_SPEED` and calls `set_ephe_path`. A production
claim therefore needs a closed inventory and SHA-256 for every external Swiss
Ephemeris data file. Silent dependence on a working directory or an undocumented
Moshier fallback is unacceptable. Optional-body warnings must identify missing
data without converting the output into a fully qualified profile.

## Release gaps

1. Package version is duplicated in `pyproject.toml` and `__init__.py`; it needs
   single sourcing or a mandatory consistency test.
2. Runtime code and tests still discover schemas through source-tree paths; no
   installed `importlib.resources` API or hashed resource manifest exists.
3. Neither console script exposes a stable explicit version option. Installed
   behavior is not yet tested outside the checkout.
4. CI uses editable installs and does not build/install the wheel under test.
5. Build-system requirements are lower bounds, so an isolated build is not yet a
   reproducible toolchain.
6. Project metadata includes the license file in the wheel but lacks explicit
   license, author/maintainer, project URL, classifier, and release metadata.
7. AGF has no GitHub release, release tag, checksum set, release manifest, or
   publication workflow.
8. There is no unified calculation-profile, normalization, provider/data, input,
   configuration, or output-hash contract.
9. `pyswisseph` CPython 3.12 has no upstream binary artifact; production build
   provenance is unresolved.
10. External ephemeris files are not bundled or inventoried. Current `ephe_path`
    defaults to `.`, which is not an acceptable production identity.
11. Several pipelines are explicitly scaffolds; advertised CLI inventory must
    distinguish callable commands from release-supported production behavior.
12. The current checkout is six approved commits ahead of `origin/main`; the
    release cannot tag an unpublished commit history.
13. Swiss Ephemeris licensing is not an ordinary package-metadata detail.
    Astrodienst's official terms require choosing AGPL compliance or the
    Professional License before distributing dependent software or activating a
    public service. AGF cannot make that product/legal decision.

## Risk register

| Risk | Severity | Control |
|---|---:|---|
| Python 3.12 live-provider artifact absent | Critical | Approve controlled Linux source build or separate worker runtime before Slice 6 |
| Swiss Ephemeris license not selected | Critical | Product owner obtains appropriate legal guidance and records AGPL-compliance or Professional-License authority before public activation |
| Ephemeris data/fallback drift | Critical | Closed file inventory, hashes, provider flags/results, and fail-closed profile checks |
| Source-tree imports hide missing wheel data | High | Installed tests outside checkout with import-origin assertions |
| AGF/SPC range resolves unexpected SPC | High | Exact SPC wheel/hash in constraints and worker manifest |
| Duplicate version metadata diverges | High | Single source or build/test equality gate |
| Timestamp/noncanonical JSON breaks hashes | High | Explicit semantic envelope and canonical serialization in Slice 3 |
| Reproducibility varies by build backend/time | High | Pinned toolchain, clean exports, controlled epoch, double build |
| Callable scaffold mistaken for supported feature | Medium | Runtime/contract inventory and explicit support labels |
| Publishing sdist creates unqualified path | Medium | Wheel-only GitHub release for 0.6.0 |
| Local commits not on remote | Medium | Push only after qualified commit and explicit approval; tag exact remote commit |

## Gate decision required

Approve one production-live artifact direction before Slice 6:

1. **Recommended:** retain the API's Python 3.12 contract and build
   `pyswisseph==2.10.3.2` from the exact sdist inside a pinned Linux x86-64
   compiler/base-image environment. Preserve the resulting wheel hash and qualify
   that exact artifact. If the build cannot be made stable and repeatable, block
   release rather than silently fall back.
2. Establish a separately versioned Python 3.11 domain worker and document why it
   does not share the current API package runtime. This requires API architecture
   approval and is not an AGF-local decision.

This decision does not block Slices 2-5, but it is a hard dependency for the live
release-candidate gate.

Separately, record the project owner's Swiss Ephemeris licensing path before any
public AstroWoof service invokes the provider. The
[official Astrodienst licensing page](https://www.astro.com/swisseph/swephinfo_e.htm)
describes AGPL and the Swiss Ephemeris Professional License as the two choices and
states that the choice precedes distribution or public-service activation. This
report flags the dependency; it is not legal advice and does not infer that the
current MIT repositories satisfy either path.

## Gate evidence

- Baseline: 156 tests passed on Windows CPython 3.12.13.
- Both source console-module `--help` paths returned zero without pyswisseph.
- Disposable audit wheel: 78 entries, 137,753 bytes, 33 schemas, license and
  entry-point metadata present; SHA-256 recorded as nonrelease evidence and the
  wheel removed.
- AGF GitHub releases: none found. Local tags: none found.
- Exact SPC release asset re-downloaded, hashed, and removed.
- Pyswisseph PyPI versions and complete 2.10.3.2 file inventory inspected;
  Windows 3.10/3.11 artifacts downloaded, hashed, and removed; binary 3.12
  absence reproduced.
- Official Swiss Ephemeris licensing material reviewed; unresolved license choice
  recorded as a critical production-activation dependency.
- `git diff --check`, actual diff review, and final status are recorded in the
  sprint log/handoff.
