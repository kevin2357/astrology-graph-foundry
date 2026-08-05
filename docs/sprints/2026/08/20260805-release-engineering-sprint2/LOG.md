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
