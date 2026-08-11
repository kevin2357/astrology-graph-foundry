# AGF/SPC Runtime and Ownership Decoupling Sprint Log

This log is append-only during execution. Planning entries do not represent
completed implementation slices.

## 2026-08-11 — Planning baseline

- Product owner moved decoupling out of the beginning of the time-frame
  bounded-Natal sprint after the audit showed a broader public migration than one
  dependency-line removal.
- Immutable pre-decoupling baseline is published AGF 0.7.0 at commit
  `8926483b38c6b5c6fd33748aa190d330bba4cd5b`, wheel SHA-256
  `fca6c153b14cd88f56ca9e151baf8d048cde4d3ac41a14af9912e3176fa52f53`.
- Known surfaces are mandatory package metadata, package-root exports,
  `projection_adapter.py`, `astro-package project`, SPC exception imports in the
  primary CLI, projection doctor readiness, SPC-derived Synastry analysis views,
  integration scripts, and tests.
- Projection-neutral temporal and canonical source contracts remain AGF-owned and
  are presumed retainable without SPC runtime imports.
- Initial version expectation is AGF 0.8.0 because public Python, CLI, doctor, and
  view behavior may change; this is a planning recommendation, not an implemented
  version decision.
- Sprint 3 is sequenced after Sprint 2. No implementation, schema, test, package
  version, tag, release, or downstream repository was changed during planning.

## 2026-08-11 — Slice 1 implementation and Gate 1 candidate

- Started from clean `main` commit `b0c2868` (`Close terrestrial bounded natal
  parity sprint`). Created and pushed annotated rollback checkpoint
  `pre-spc-decoupling-20260811` before changing the dependency boundary.
- Removed the mandatory SPC distribution dependency, installed-runtime imports,
  package-root projection exports, `astro-package project`, projection doctor mode,
  and AGF-owned projection adapter.
- Replaced the SPC-derived Synastry analysis materialization with
  `source_factual_relationship_handoff_v3`. It explicitly reports projection as
  not performed and retains the canonical source and structural-evidence graphs.
- Retained the temporal projection-source adapter because it creates an AGF-owned,
  projection-neutral serialized wire artifact and imports no SPC code.
- Removed projection-execution tests and scripts whose subject left AGF. Added
  runtime-decoupling, source-factual Synastry, clean-install, and external wire
  qualification coverage.
- Set the release-candidate package version to `0.8.0`. This is a deliberate
  public API/CLI/doctor/view migration; canonical graph schema versions did not
  change merely because execution ownership moved.
- A first external-wire check appeared to find unresolved source references. The
  finding was a harness defect: SPC uses qualified `canonical:object:` and
  `canonical:relationship:` reference namespaces while AGF node IDs are stored
  without those prefixes. Normalizing the documented namespace made every emitted
  projected source reference resolve.
- Independently built and installed candidate AGF 0.8.0 and SPC 0.10.0 wheels in a
  disposable Linux environment. Projection of the serialized Natal fixture passed:
  17 projected objects, 75 projected relationships, 17 distinct resolved source
  references, and preserved `source_chart_id=natal:kevin`.
- Clean Linux base installation contained no SPC distribution/module, reported no
  broken requirements, executed `astro-package doctor --require-mode saved`,
  runtime-manifest, and both installed entry-point help surfaces.
- Linux live qualification used CPython 3.11, pyswisseph 2.10.3.2, and Moshier.
  Exact and four-hour bounded Natal generation passed while a meta-path guard made
  any `semantic_projection` import fatal.
- Full installed-wheel suite: `226 passed` in 11.93 seconds. The sole warning was
  pytest's expected inability to write a cache into the read-only source mount.
- Compact evidence is retained in `results/no-spc-installed-qualification.json`
  and `results/independent-wire-compatibility.json`. No wheel, virtual environment,
  generated probe chart, cache, or expanded source tree was retained.
- Gate 1 is a review candidate. No decoupling commit, release tag, or publication
  has occurred.

## 2026-08-11 — Gate 1 approval

- Product owner approved Slice 1, the 0.8.0 version decision, commit and push, and
  immediate immutable wheel release qualification and publication.
- Committed the approved slice as `2e5feef35e6d7144c3e639ece0aba9ff587ea4e9`
  and pushed `main`.
- Two clean Git exports built byte-identical wheels with
  `SOURCE_DATE_EPOCH=1786474641`. Qualified wheel SHA-256 is
  `f236de0bb7c254c4421f571e816f2314251636ebbed9aa3cb9cb2a09925c04ae`.
- The exact wheel passed clean no-SPC saved mode, installed CLI execution,
  controlled exact and bounded Linux/Moshier generation, and 226 installed-wheel
  tests.
- Created and pushed annotated tag `astrology-graph-foundry-v0.8.0` at the exact
  qualified commit. Published the GitHub release with wheel, release manifest,
  runtime-package manifest, and `SHA256SUMS.txt`.
- Re-downloaded all four assets. Every checksum passed; the downloaded wheel
  reinstalled cleanly with no SPC and reproduced the published runtime manifest.
- Publication smoke initially ran from the read-only download mount and exposed
  that AGF's default file logger expects a writable current directory. Repeating
  the documented installed-runtime smoke from a writable disposable directory
  passed. This operational constraint is retained in the 0.8.0 release record.
- Release URL:
  `https://github.com/kevin2357/astrology-graph-foundry/releases/tag/astrology-graph-foundry-v0.8.0`.
