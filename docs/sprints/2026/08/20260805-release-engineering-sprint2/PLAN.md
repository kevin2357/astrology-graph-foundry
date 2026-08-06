# Immutable Release Engineering Sprint Plan

**Status:** Completed; AGF 0.6.0 published and download-verified at tag `astrology-graph-foundry-v0.6.0`

**Planned sequence:** Sprint 2 of 2. It begins only from the clean, approved, committed canonical-identity boundary.

**Repository:** `astrology-graph-foundry`

## Outcome

Qualify and publish AGF as a reproducible, immutable production dependency whose exact wheel and SHA-256 digest can be pinned by the AstroWoof API. The release must prove deterministic saved-package behavior, controlled live calculation, installed AGF-to-installed-SPC compatibility, packaged-resource integrity, explicit calculation provenance, and re-verifiable publication.

## Current Evidence and Assumptions

- AGF currently declares distribution/package version 0.5.0 in more than one location, Python `>=3.10`, SPC `>=0.10.0`, and an optional `pyswisseph>=2.10` live extra.
- Package data declares JSON Schemas and console scripts `astro-package` and `generate-daily-ephemeris`; source-tree tests do not by themselves prove installed-wheel resource and CLI behavior.
- CI presently exercises editable/source checkout installs on Ubuntu and Python 3.10–3.12. It is not an installed-wheel, reproducibility, publication, or live-provider qualification matrix.
- AGF has version/doctor reporting and substantial saved-package, fixture, adapter, projection, and live tests, but no unified calculation-profile/configuration fingerprint covering all materially relevant choices.
- AGF has no current immutable release tag or repository release bundle identified during planning, and no complete manifest/checksum/publication-verification workflow.
- SPC 0.10.0 already has a qualified immutable wheel. Its documented SHA-256 is `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`; Sprint 2 must re-download and independently verify the authoritative artifact before using it.
- A permissive library dependency lower bound is not a production lock. The API/runtime environment must install an exact SPC artifact/hash pair.
- Current documentation contains historical platform cautions for Swiss Ephemeris. Supported Python/platform/live-data combinations must be demonstrated, not inferred from dependency metadata.

## Scope

- Version consistency, package metadata, resource inventory, installed CLIs, wheel-only runtime, and build reproducibility.
- Pure saved-package mode without Swiss Ephemeris and live mode with an exactly qualified provider stack.
- A versioned calculation/normalization provenance contract and deterministic hashes.
- Exact installed SPC compatibility and an API-worker release handoff.
- Release candidate qualification, manifests, checksums, compatibility guide, release notes, annotated tag, GitHub release, download verification, and cleanup.
- Project-level released-baseline documentation within explicitly approved repository scope.

## Non-goals

- Altering Sprint 1 identity semantics.
- Releasing a new SPC build; use its already qualified immutable release unless a proven incompatibility requires a separate SPC process.
- Implementing API persistence/orchestration or product behavior.
- Publishing before explicit approval at the publication gate.
- Claiming all platforms supported from a single-platform test.
- Embedding credentials, machine paths, timestamps, or mutable URLs as semantic provenance.

## Slice 1 — Release-Readiness, Packaging, and Dependency Audit

Freeze the exact Sprint 1 commit as the candidate base. Audit distribution/import/version consistency, source layout, build backend and versions, package data, schemas/resources, both console scripts, dependency/extras metadata, installed resource access, sdist policy, current CI, license/readme metadata, tags, and release automation. Inventory every supported runtime mode.

Choose deliberately:

- release version and tag convention;
- whether package/library metadata retains an SPC compatibility range while the production handoff pins an exact wheel;
- exact SPC artifact and hash;
- exact build frontend versions;
- Python/platform matrix for pure and live modes;
- exact pyswisseph version and ephemeris-data policy;
- which schemas/contracts are release-facing; and
- whether an sdist is published or only a qualified wheel.

**Gate 1:** Release gap report, dependency/artifact lock proposal, version-impact decision, supported-mode matrix, risk register, and release checklist. Run baseline tests and metadata/build inspections; `git diff --check`; diff review; log/result; stop for approval and commit only after approval.

## Slice 2 — Installable Package Boundary

Make package version single-sourced or mechanically verified. Ensure all required schemas, registries, defaults, and runtime resources are package data and are accessed via installed-resource APIs. Define a compact runtime package manifest containing resource paths, schema/contract versions, and SHA-256 digests. Ensure console scripts provide stable `--help`/version behavior and fail clearly when optional live dependencies are absent.

Build a wheel, install it into clean environments outside the source checkout, and run using an unrelated working directory with the source tree excluded from imports. Verify every advertised pure-mode command and library entry point.

**Gate 2:** `runtime-package-manifest.json` and `installed-smoke.json`; wheel-content inventory; metadata/version checks; every supported CLI exercised from an installed wheel; pure-mode import/run without pyswisseph; full package tests; `git diff --check`; diff review; log/result; stop for approval and commit.

## Slice 3 — Calculation Profile and Provenance Contract

Design and implement a unified, versioned calculation profile that records or hashes every material assumption:

- calculation-profile and normalization-policy versions;
- zodiac framework and house system;
- included planets, luminaries, points, asteroids, nodes, angles, and derived objects;
- node policy;
- aspect definitions and orb policy;
- lots, Part of Fortune, sect/day-night behavior;
- derived-technique options;
- coordinate and timezone normalization policy;
- provider identity and adapter version;
- Swiss Ephemeris wrapper/library version and ephemeris data source/version/checksum where applicable; and
- explicit defaults versus invocation overrides.

Define canonical serialization and a configuration hash. Define a normalized source-input hash that excludes descriptive-only fields while retaining all calculation-relevant facts/policies. Define an output content hash over a precise immutable payload envelope, excluding the hash field itself and nonsemantic operational fields, or explicitly assign final artifact-envelope hashing to orchestration. Avoid self-referential hashes and false claims about external ephemeris reproducibility.

**Gate 3:** Versioned provenance schema, canonicalization specification, golden hash vectors, mutation-sensitivity tests, default/override coverage, saved and live provenance examples, and a documented orchestration boundary. Run schema, calculation, identity, serialization, and determinism suites; `git diff --check`; diff review; log/result; stop for approval and commit.

## Slice 4 — Stable Runtime and Consumer Contracts

Publish a concise contract/schema inventory and compatibility guide for pure versus live modes. Specify required and optional dependencies, supported versions/platforms, failure classes, partial-artifact policy, installed resource discovery, identity-policy version from Sprint 1, graph/schema versions, and exact SPC compatibility.

Create the AstroWoof API worker handoff: exact AGF and SPC wheel/hash pairs, install order or lock format, invocation/input schema, stable identity field, provenance fields to retain, cache-key ingredients, expected outputs, retryable versus terminal failures, and startup health/doctor assertions. Do not decide API persistence or UX.

**Gate 4:** Compatibility guide, API handoff, contract inventory, and startup/doctor assertions reviewed against current implementation and exact SPC release. Contract and documentation link checks; focused consumer tests; `git diff --check`; diff review; log/result; stop for approval and commit.

## Slice 5 — Packaged Deterministic QA

From clean wheel-only environments outside the checkout, run fixture replay and saved-package/contract flows with pyswisseph absent. Validate every packaged schema/resource against the manifest. Generate the same canonical fixture repeatedly and across clean environments, comparing canonical semantic content and documented nonsemantic fields separately. Exercise every supported CLI meaningfully, not only `--help`.

**Gate 5:** Deterministic replay evidence, installed smoke report, resource-manifest verification, CLI transcripts/summaries, and failure-mode evidence. Full pure-mode suite from the installed artifact; `git diff --check`; diff review; log/result; stop for approval. Fix any nondeterminism before proceeding.

## Slice 6 — Controlled Live AGF-to-SPC Release Candidate

Install the candidate AGF wheel, the independently verified exact SPC 0.10.0 wheel, and the selected pyswisseph artifact into a clean supported environment. Record Python, OS/architecture, wheel digests, library versions, provider identity, and ephemeris-data provenance. Run controlled Natal inputs, including Sprint 1 explicit identity, DST/coordinate edge cases within the accepted contract, and a known deterministic baseline. Validate and project the resulting canonical artifact through installed SPC.

Separate tolerances for astronomy/library behavior from exact deterministic semantic serialization. Do not generalize a platform guarantee beyond tested combinations. If live behavior depends on unpinned external data, either bundle/hash the data, constrain the support claim, or block release.

**Gate 6:** `controlled-live-summary.json` and `cross-repository-compatibility.json`; exact installed artifact inventory; live Natal validation; explicit identity preservation; installed AGF-to-SPC projection proof; provider/data provenance; supported-matrix decision. Run full relevant live and projection suites; `git diff --check`; diff review; log/result; stop for approval and commit.

## Slice 7 — Reproducible Build, Release Handoff, Tag, and Publication

Build twice from clean exports of the exact candidate commit using pinned build tooling and controlled `SOURCE_DATE_EPOCH`; compare wheel bytes and SHA-256. Inspect wheel metadata and contents again. Assemble compact release evidence: release manifest, artifact hashes/sizes, resource manifest hash, compatibility guide, API handoff, release notes, qualification summaries, and cleanup record.

At the publication sub-gate, present the exact commit, version, tag, wheel hash, SPC hash, provider matrix, and commands for approval. Only after explicit approval: create an annotated immutable tag at the qualified commit, push the approved references, publish the wheel and checksums in a GitHub release, download them into a fresh location, verify hashes/signatures if adopted, install the downloaded wheel, rerun the release smoke/projection proof, and update the project released baseline.

**Gate 7:** Byte-identical build proof, final manifest/checksums, clean-candidate status, and explicit publication approval before any external mutation. After publication, create `publication-verification.json`, record tag/release URLs and downloaded hashes, rerun installed smoke, clean temporary environments/build trees, run `git diff --check`, verify clean worktrees, review final log/result, and seek final acceptance.

## Controls and Safety Rules

- Sprint 2 cannot begin until Sprint 1 is approved, committed, and clean.
- The release sprint may not redesign identity; a discovered identity-contract defect returns work to a separately approved Sprint 1 correction boundary and invalidates the candidate.
- Inspect worktrees before editing and preserve unrelated changes.
- Cross-repository inspection is read-only unless separately authorized.
- No destructive Git operations; no tags, pushes, publication, or credentials before explicit approval.
- Credentials never enter source, wheels, requirements, manifests, logs, results, command captures, or image layers.
- Installed tests run outside the checkout with source imports excluded.
- Prefer deterministic saved-package evidence before live calculation.
- Production compatibility is an exact artifact/hash pair, not a version-range assertion.
- Keep only compact evidence and hashes in `results`; remove environments, caches, build trees, downloaded duplicates, and generated ephemeris data after verification.
- Every gate requires tests, `git diff --check`, actual diff review, append-only log, slice result, report, approval, and only then a commit.

## Dependencies

- The exact approved Sprint 1 commit and its frozen identity/schema versions.
- A re-verified immutable SPC 0.10.0 wheel; any incompatibility blocks the AGF candidate rather than silently rebuilding SPC.
- Approved exact pyswisseph version and ephemeris-data policy for live mode.
- Pinned build frontend/toolchain and controlled build time/source archive.
- Access to the intended GitHub repository and release credentials only at the explicitly approved publication gate.
- AstroWoof API owner acceptance of the exact artifact handoff and project owner acceptance of the released baseline update.

## Versioning Implications

The current 0.5.0 version must not be reused. If Sprint 1 remains optional/additive at the input/schema surface while introducing a new documented identity policy, the planning recommendation is 0.6.0 rather than 0.5.1 because canonical identity is a material public contract. If Sprint 1 removes fallback behavior, changes required schema shape, or makes existing saved packages invalid, a larger compatibility break may be warranted. Gate 1 selects the version from actual accepted diffs and schema compatibility; Sprint 2 never retrofits the decision after qualification starts.

## Exit Criteria

- Reproducible, byte-identical wheel builds under controlled documented inputs.
- Clean wheel-only installation and runtime outside the source checkout.
- Every supported CLI executed from the installed artifact.
- Packaged schemas/resources verified against a hashed manifest.
- Saved-package mode passes with live dependencies absent.
- Controlled live mode passes with an exact compatible pyswisseph/provider/data stack.
- Exact qualified SPC wheel compatibility is proven and recorded by hash.
- Calculation and normalization provenance, source-input/configuration hashes, and output-hash ownership are explicit.
- Sprint 1 stable subject/chart identity is preserved through live generation, serialization, and projection.
- Canonical fixture replay is deterministic under the documented envelope.
- Installed AGF-to-installed-SPC projection succeeds.
- Release manifest, compatibility guide, API handoff, release notes, and checksums are complete.
- Annotated immutable tag points to the exact qualified commit.
- Published wheel/checksum are re-downloaded, hash-verified, reinstalled, and smoke-tested.
- Large temporary environments, build trees, caches, and generated data are removed.
- AGF and authorized project released-baseline documentation are current.
- All approved commits and tags are recorded; relevant worktrees are clean.

## Deferred Work

- Additional Python/platform combinations not proven by the release matrix.
- Signing/SBOM/attestation infrastructure beyond the approved release scope, unless Gate 1 makes it mandatory.
- Private package index or container image publication.
- API deployment, migration, persistence, queueing, and rollback behavior.
- New SPC, SBE, projection ontology, authoring, or frontend releases.
