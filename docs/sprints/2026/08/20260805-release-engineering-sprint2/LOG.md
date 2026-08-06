# Immutable Release Engineering Sprint Log

This log is append-only during execution. The sprint is blocked on Sprint 1, and planning entries are not release qualification evidence.

## 2026-08-05 — Planning Baseline

- Scope authorized: read-only investigation and sprint planning only. No production changes, commits, tags, pushes, publication, credential use, or cross-repository modifications authorized.
- Repository start: `C:\dev\github\astrology-graph-foundry` on `main`, tracking `origin/main`, clean before sprint skeleton creation.
- Starting commit: `259058d` (`Link AstroWoof integration authority`). Sprint 2 must instead start from the later exact approved Sprint 1 commit.
- Current metadata observed: distribution `astrology-graph-foundry`, package/version 0.5.0, Python `>=3.10`, SPC `>=0.10.0`, optional live dependency `pyswisseph>=2.10`, console scripts `astro-package` and `generate-daily-ephemeris`, packaged JSON Schema declaration.
- Version duplication observed between project metadata and package runtime constant; release qualification must make these single-sourced or mechanically checked.
- Existing CI is source/editable-install oriented on Ubuntu/Python 3.10–3.12. It does not prove wheel-only installed behavior, byte reproducibility, all resource inclusion, live provider support, or publication integrity.
- Existing doctor/version reporting distinguishes saved/projection/live capabilities and SPC mismatch, but does not yet provide a unified calculation-profile/resource fingerprint.
- Tests and docs sometimes rely on source-tree schema paths. Installed resource access and wheel content require independent proof.
- Release infrastructure gap: no current AGF immutable release tag, release manifest, checksum bundle, publication-verification record, or complete reproducible-build workflow was identified.
- SPC baseline: version 0.10.0 has a documented qualified wheel SHA-256 `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`. This must be independently downloaded and verified during execution.
- Dependency conclusion: `semantic-projection-core>=0.10.0` is not a production lock. The runtime handoff must name an exact SPC wheel and hash even if library metadata retains a compatible range.
- Live-mode risk: Python/platform support and exact pyswisseph/Swiss Ephemeris data behavior are not established by current metadata. Qualification claims must be limited to demonstrated combinations.
- Provenance gap: no single emitted contract currently fingerprints all calculation choices, provider/library/data identity, normalized inputs, canonical configuration, and output content boundary.
- Initial version recommendation: do not reuse 0.5.0. Prefer 0.6.0 for an additive but materially new identity/provenance contract; escalate if Sprint 1 creates a required-schema or compatibility break. Final decision waits for Sprint 1 and Release Gate 1.
- No slice result or release artifact exists. The `results` directory is intentionally empty.

## 2026-08-05 — Sprint Activation and Slice 1

- Human approved beginning Sprint 2 after Sprint 1 completed and both AGF and
  astrowoof-project were committed cleanly.
- Froze the Sprint 1 base as
  `885223bbd8126b88f22399de7f889387c6180b7b`; AGF was clean on `main`, six
  commits ahead of `origin/main`.
- Confirmed candidate package version 0.6.0, canonical graph 1.3.0, semantic
  identity policy 1.1.0, and relationship identity policy 1.0.0.
- Audited `pyproject.toml`, source layout, 33 schemas, console scripts, optional
  dependencies, CI, resource lookup, version reporting, license, Git state,
  local tags, and GitHub releases.
- Confirmed there is no existing AGF tag or GitHub release. Proposed annotated
  tag `astrology-graph-foundry-v0.6.0` and wheel-only release assets plus manifest
  and checksums.
- Built a disposable nonrelease wheel with the isolated backend. It contained 78
  entries, all 33 schemas, license, metadata, and entry points; SHA-256
  `54d9e4704de612b57ee87eeea69f761729f4060e3eca4f0c3a2fce0c3bd8855d`.
  Removed the wheel and temporary directory after inspection.
- Re-downloaded the SPC 0.10.0 release wheel. Independent SHA-256 remained
  `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`,
  agreeing with GitHub's release-asset digest. Removed the temporary copy.
- Proposed pinned build frontend `build==1.5.0`, backend `setuptools==83.0.0`,
  and `wheel==0.47.0`; byte reproducibility remains a later gate.
- PyPI reports `pyswisseph==2.10.3.2` as current. Downloaded and hashed its
  Windows x86-64 CPython 3.10 and 3.11 wheels, then removed them.
- Critical finding: pyswisseph 2.10.3.2 publishes no CPython 3.12 binary on any
  platform, while astrowoof-api requires Python `>=3.12,<3.13`. A controlled
  Linux source-built wheel or separately approved Python 3.11 domain worker is
  required for production live calculation.
- Critical licensing finding: Astrodienst's official Swiss Ephemeris materials
  require a choice between AGPL compliance and the Swiss Ephemeris Professional
  License before dependent distribution or public-service activation. Recorded
  this as a product-owner/legal gate without making a legal conclusion in AGF.
- Confirmed AGF explicitly requests Swiss Ephemeris flags and sets `ephe_path`;
  production must pin data files and prevent undocumented fallback behavior.
- Baseline suite: 156 passed in 4.58 seconds on Windows CPython 3.12.13.
- Both console module `--help` paths returned zero without pyswisseph. A combined
  display command returned one because output truncation interrupted a pipeline;
  direct exit-code reruns confirmed both commands themselves return zero.

## 2026-08-05 — Slice 1 Gate Ready for Review

- Wrote the release gap report, proposed artifact/dependency lock, supported-mode
  matrix, risk register, checklist decisions, and compact machine-readable audit.
- Reviewed the complete Slice 1 diff. Changes are documentation/evidence only;
  no runtime, schema, packaging metadata, dependency, or identity behavior changed.
- Parsed the JSON evidence, checked all changed and untracked files for trailing
  whitespace, and ran `git diff --check` successfully.
- Verified every temporary wheel/download directory was removed. No wheel, sdist,
  build tree, environment, cache, or ephemeris data was retained.
- Slice 1 is paused for human approval. No files are staged or committed.

## 2026-08-05 — Slice 1 Approval and Commit

- Human approved Slice 1 and authorized continuation.
- Committed the audit and evidence as `8757398` (`Audit AGF release readiness`).
- Began Slice 2 from that clean named boundary.

## 2026-08-05 — Slice 2 Installable Package Boundary

- Single-sourced version 0.6.0 in `_version.py` and changed setuptools metadata
  to derive the distribution version from it.
- Pinned the build backend versions and added explicit package license, author,
  repository, and Python-version metadata.
- Bounded general SPC compatibility to 0.10.x and the optional Swiss dependency
  to 2.10.x; exact production artifacts remain an outer-manifest responsibility.
- Added installed-safe schema access and a deterministic runtime package manifest
  with path, size, SHA-256, descriptive schema metadata, and declared versions.
- Added `astro-package runtime-manifest`, `--version` to both console scripts, and
  concise console failures when optional live calculation lacks pyswisseph.
- Refreshed the external editable development install from stale 0.5.0 metadata
  to 0.6.0. This changed no repository files.
- Focused initial resource/version tests exposed only the expected stale external
  distribution metadata; after reinstall, focused tests passed.
- First wheel-only qualification intentionally installed the two top-level wheels
  with `--no-deps` and exposed absent `jsonschema`. SPC correctly declares that
  dependency; corrected the harness to install SPC's declared closure.
- Second clean smoke passed version/help, doctor, resource manifest, site-packages
  import origin, no-Swiss mode, and `pip check`.
- Added console wrappers and reran a final clean smoke. Both live entry paths now
  fail concisely without a traceback when pyswisseph is absent.
- Final nonrelease smoke wheel SHA-256:
  `87f8df63ce0ff6ce1f35830c846a36e5f8c32a6e51984573fc5123b94a342de6`.
  Exact SPC wheel SHA-256 remained
  `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`.
- Captured compact installed-smoke evidence and the complete 33-resource runtime
  manifest, then removed every temporary environment and wheel.
- Focused tests: 8 passed. Full regression suite: 164 passed in 4.93 seconds.
- Targeted Ruff passed for every changed Python file.

## 2026-08-05 — Slice 2 Gate Ready for Review

- Reviewed the complete runtime, packaging, test, documentation, and evidence
  diff. No identity semantics, calculation behavior, or schema bytes changed.
- Recomputed the runtime manifest from current package resources and confirmed it
  exactly equals the retained installed evidence.
- Parsed both JSON evidence files and checked all tracked and untracked Slice 2
  files for whitespace errors. `git diff --check` passed.
- Verified the final qualification environment and all intermediate environments,
  wheels, and downloads were removed.
- Slice 2 is paused for human approval. No files are staged or committed.

## 2026-08-05 — Slice 2 Approval and Commit

- Human approved Slice 2 and authorized continuation.
- Committed the installable package boundary as `037f1c5`
  (`Define installed AGF package boundary`).
- Began Slice 3 from that clean named boundary.

## 2026-08-05 — Slice 3 Calculation Profile and Provenance

- Added versioned calculation provenance, calculation profile, normalization,
  and canonical JSON policies plus a packaged JSON Schema.
- Normalized birth geometry separately from display name, location label, and
  source-chart identity. Included normalization-policy identity inside the source
  hash envelope.
- Added a deterministic configuration profile covering zodiac, houses, objects,
  node alternatives, aspects/orbs, declination, lots/sect, derived techniques,
  invocation settings, provider runtime, and ephemeris data.
- Distinguished complete live profiles from cached replay profiles that cannot
  prove the original calculation runtime.
- Chose an explicit orchestration-owned exact artifact-byte hash boundary instead
  of emitting a self-referential or misleading AGF content hash.
- Added nonrecursive Swiss Ephemeris data inventory by filename, size, per-file
  SHA-256, and sorted aggregate hash while excluding the machine path.
- Recorded primary ecliptic and equatorial-declination calculation flags
  separately after reviewing the actual live code.
- Added provenance to newly built Natal package metadata without changing Sprint
  1 source identity or making the field required for historical Natal schemas.
- Packaged schema resource count increased from 33 to 34. Updated current tests;
  retained Slice 2's manifest unchanged as evidence for its committed tree.
- Added golden mutation vectors, synthetic live-contract and cached examples,
  authoritative documentation, schema validation, provider inventory tests, and
  live-Natal integration assertions.
- Focused provenance/identity/resource suite: 40 passed.
- Full suite before final evidence closure: 171 passed in 4.65 seconds.
- Targeted Ruff passed while explicitly leaving the pre-existing naive
  `metadata.created_at` behavior unchanged.

## 2026-08-05 — Slice 3 Gate Ready for Review

- Added a regression test that recomputes every retained golden vector and
  validates both retained examples against the packaged provenance schema.
- Final focused provenance/identity/resource suite: 41 passed.
- Final full regression suite: 172 passed in 5.14 seconds.
- Targeted Ruff passed, current-document links passed across 43 Markdown files,
  all JSON evidence/schema parsed, tracked and untracked whitespace checks passed,
  and `git diff --check` passed.
- Reviewed the complete diff for source/chart/calculation identity conflation,
  machine-path leakage, false cached provenance, unrecorded material defaults,
  self-referential hashing, and projection-context leakage.
- No temporary environment, generated chart, downloaded provider, build artifact,
  or ephemeris data was created or retained in this slice.
- Slice 3 is paused for human approval. No files are staged or committed.

## 2026-08-05 - Slice 3 Approval and Commit

- Human approved Slice 3 and authorized continuation.
- Committed the calculation provenance contract as `7f522cf` (`Add calculation provenance contract`).
- Began Slice 4 from that clean named boundary.

## 2026-08-05 - Slice 4 Stable Runtime and Consumer Contracts

- Replaced stale AGF 0.5.x/open-ended SPC compatibility guidance with the 0.6.0 candidate, bounded 0.10.x library compatibility, and exact published SPC 0.10.0 artifact hash for production handoff.
- Defined saved, projection, and live runtime modes, including the important distinction between live dependency availability and qualified provider/data reproducibility.
- Added an installed-runtime contract inventory covering public commands, schemas, canonical graph/identity/provenance versions, completeness policy, and failure ownership.
- Added an AGF-owned AstroWoof worker handoff with unresolved AGF/live placeholders, explicit `source_chart_id`, provenance retention, cache inputs, outputs, startup assertions, and retry/terminal boundaries.
- Read-only API review found its proposed worker contract still records AGF 0.5.0, name-derived identity, and missing unified provenance. The API repository was not modified; its owner must later reconcile against the AGF release handoff.
- Read-only SPC release evidence confirmed published SPC 0.10.0 SHA-256 `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150` and the canonical graph/structural evidence/source identity/registry intake boundary.
- Extended doctor with distribution/runtime alignment, exact supported SPC release line, installed resource-manifest identity, calculation contract versions, and stable required-mode failure codes.
- Development `--require-mode projection` assertion passed on CPython 3.12.13/Windows with AGF 0.6.0, SPC distribution/engine 0.10.0, and 34 packaged schemas. Swiss was absent as expected. This is not substituted for later wheel-only evidence.
- Focused consumer suite passed: 42 tests.

## 2026-08-05 - Slice 4 Gate Ready for Review

- Full regression suite passed: 175 tests in 4.28 seconds.
- Targeted Ruff passed for the changed runtime and test files after correcting import-only lint findings.
- Checked 51 relative Markdown links across the repository README and current/history docs; none were broken.
- Parsed retained startup JSON evidence, ran `git diff --check`, and reviewed the complete runtime, tests, compatibility, handoff, sprint report, and evidence diff.
- Confirmed no API, SPC, SBE, or project repository was modified and no production code changed identity or calculation behavior.
- No environment, wheel, downloaded dependency, generated chart, or provider data was created in this slice.
- Slice 4 is paused for human approval. No files are staged or committed.

## 2026-08-05 - Slice 4 Approval and Commit

- Human approved Slice 4 and authorized continuation.
- Committed stable runtime and consumer contracts as `f2bfdf5` (`Define stable runtime consumer contracts`).
- Began Slice 5 from that clean named boundary.

## 2026-08-05 - Slice 5 Packaged Deterministic QA

- Built initial nonrelease candidate wheel and created a clean CPython 3.12 environment outside the checkout with exact SPC 0.10.0 and no pyswisseph.
- The first installed cached-Natal run found a Windows packaging defect: IANA timezone normalization failed because no system timezone database existed and AGF did not declare `tzdata`.
- Added conditional Windows dependency `tzdata>=2024.1`, documentation, and a metadata regression assertion. Rebuilt and restarted from a new environment; it resolved `tzdata==2026.3` and passed timezone normalization.
- The next schema validation found `natal_dataset_v1.schema.json` still required removed legacy alias `natal.semantic_graph`. Canonical finalization has intentionally published top-level `canonical_astrology_graph` since the dual-write removal.
- Corrected the schema to keep the nested alias optional while retaining the canonical top-level graph requirement and added a regression assertion. Rebuilt and restarted qualification in a third clean environment.
- Final Slice 5 wheel: 145,720 bytes, SHA-256 `7b2101cb9bec75e29c1a274b3af04f55af73afde00d284192a53517654f8347e`.
- Reverified local published SPC wheel SHA-256 `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150` before install.
- Generated the same cached Natal package twice with executions separated across timestamp seconds. Exact bytes differed only because of documented operational `metadata.created_at`; semantic content excluding that field was identical.
- Semantic replay SHA-256: `7d8d1087fbb51fce032fa86d442a4e81dc9aa53df32904f121daba9da36f8bab`; canonical graph SHA-256: `73566ffe82267ea24daa82a959acdf5236bdd83febdc7ba992b20431ccdb9689`.
- Validated the Natal package against installed schemas, verified all 34 installed resource hashes, and recorded runtime-manifest SHA-256 `58e351fc4a713c5cdb1a254c442ba46b586ca98fe30ff0020e5f634e6408d7f0`.
- Installed SPC projection succeeded with three objects, one relationship, and exact `astrowoof:dog:slice5` identity preservation.
- Doctor projection assertion passed. Doctor live assertion returned exit 2 with `pyswisseph_missing` as designed.
- Meaningfully exercised both console entry points. Both live invocations failed concisely without traceback and created no artifact while pyswisseph was absent.
- Installed-wheel full suite, launched outside the checkout against the repository test inventory: 176 passed in 5.20 seconds.

## 2026-08-05 - Slice 5 Gate Ready for Review

- Source-environment full regression suite also passed: 176 tests in 5.20 seconds.
- Targeted Ruff passed; both retained JSON evidence files parsed; 51 relative Markdown links passed; `git diff --check` passed.
- Reviewed the complete dependency, schema, regression-test, compatibility, evidence, result, and log diff. Changes are limited to the two installed-QA defects and their durable contract/evidence updates.
- Verified exact cleanup targets before recursively removing `C:\tmp\agf-slice5-20260805` and the repository-local `.slice5-transfer` directory. All three virtual environments, generated inputs/outputs, candidate wheels, and duplicate SPC wheel were removed successfully.
- The retained wheel and manifest hashes identify the tested candidate even though the nonrelease binaries were intentionally cleaned. Slice 7 will rebuild final artifacts reproducibly from the approved commit.
- Slice 5 is paused for human approval. No files are staged or committed.

## 2026-08-05 - Slice 5 Approval and Commit

- Human approved Slice 5 and authorized continuation.
- Committed deterministic installed qualification as `b5459d4` (`Qualify deterministic installed workflows`).
- Began Slice 6 from that clean named boundary.

## 2026-08-05 - Slice 6 Controlled Live Candidate

- Product owner selected CPython 3.11 on glibc-based Linux x86-64 and the published `pyswisseph==2.10.3.2` manylinux wheel as the first qualification route.
- Pinned published pyswisseph wheel SHA-256 `e00d7e08aeafe00938603bc118874b6ca7871c5aaa55aafca8fa2c6d76aff812`.
- Product owner confirmed the current AstroWoof profile uses no external ephemeris files. Chiron's file-backed possibility is acknowledged but explicitly deferred with asteroids and fixed stars.
- Selected explicit Moshier calculation rather than Swiss-first automatic fallback for the no-file profile.
- Added `ephemeris_mode` to provider configuration and calculation-profile hashing, bumping the calculation profile from 1.0.0 to 1.1.0 without changing the enclosing provenance contract version.
- Added `--ephemeris-mode` and `--no-optional-points` to both supported live console boundaries and forwarded them through Natal/daily provider construction.
- Live calculations now retain Swiss Ephemeris returned flags, decode the observed provider mode, and reject mismatches for explicit `moshier` or `swiss` requests. Legacy `auto` remains compatibility behavior.
- Added the candidate live-profile contract, refreshed the AstroWoof worker handoff, and added a reusable installed Linux qualification harness.
- Added a manual GitHub Actions workflow targeting Ubuntu 24.04 and CPython 3.11. It hashes the exact SPC and pyswisseph wheels, builds/installs AGF, runs controlled Natal fixtures with an empty ephemeris directory, projects through installed SPC, and runs the full suite against installed code.
- The project repository now has uncommitted, user-requested release-strategy and open-question notes recording that technical qualification does not satisfy the Swiss Ephemeris public-activation licensing gate.
- Focused mode/provenance/identity/package tests passed: 51. Full source suite after the first implementation pass passed: 181.

## 2026-08-05 - Slice 6 Linux Qualification Attempt 1

- Committed the controlled-live implementation on `codex/live-qualification` as `f3be5fb` and pushed only that qualification branch; `main` was not pushed.
- GitHub Actions run `31064829608` failed before installation in the dependency-acquisition step. The pinned SPC asset name, tag, and SHA-256 were correct, but unauthenticated `curl` received HTTP 404 because the SPC repository is private.
- Confirmed the released SPC wheel asset still reports SHA-256 `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150` through authenticated GitHub release metadata.
- Corrected the workflow to acquire that private release asset with authenticated `gh release download` through the narrowly named `SPC_RELEASE_TOKEN` secret, while retaining the independent SHA-256 check.
- No release credential was copied, printed, or stored during the correction. A rerun requires explicit authorization to configure the repository secret or another approved credential provision.
