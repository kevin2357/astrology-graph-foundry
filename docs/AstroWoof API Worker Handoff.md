# AstroWoof API Worker Handoff

**Status:** published and download-verified 0.6.0 artifact lock.

This AGF-owned handoff describes what an AstroWoof worker needs from the canonical-chart stage. It does not define API persistence, jobs, retries, dog/profile models, projection policy, authoring, or UI behavior.

The qualified boundary in this document ends at installed AGF-to-SPC projection.
It is not evidence that the released AGF, SPC, SBE, and API artifacts compose as an
unrestricted production worker.

## Artifact lock

```yaml
agf:
  distribution: astrology-graph-foundry
  version: 0.6.0
  wheel: astrology_graph_foundry-0.6.0-py3-none-any.whl
  wheel_sha256: d1b357b1ec0e40faf7070b29e5c25d18e54c9507406518f26587aac46300aa95
  release_commit: e36284af0f04e7380113ab141731e18f378ea2dc
spc:
  distribution: semantic-projection-core
  version: 0.10.0
  wheel_sha256: 60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150
  verification_status: reverified from the published SPC 0.10.0 release asset
live:
  python_platform: CPython 3.11 / Linux x86-64 / glibc manylinux_2_17 compatible
  pyswisseph: 2.10.3.2
  pyswisseph_wheel_sha256: e00d7e08aeafe00938603bc118874b6ca7871c5aaa55aafca8fa2c6d76aff812
  ephemeris_mode: moshier
  external_ephemeris_files: none
  optional_points: false
```

Installers should use a hash-enforcing lock containing local or immutable artifact URLs and exact hashes. Install SPC's declared dependency closure, then the exact SPC and AGF wheels. A compatible version range is insufficient production evidence.

## Invocation

The supported Natal call supplies the fields defined by packaged `birth_data_v1.schema.json`: display `name`, local ISO date-time, IANA timezone, latitude, longitude, optional descriptive location label, and explicit `source_chart_id`. `source_chart_id` is the opaque stable chart scope; AstroWoof may derive it from product identity outside AGF, but AGF neither parses nor stores dog/user semantics. Do not use display name, timestamps, filesystem paths, calculation hashes, or projection context as chart identity.

The qualified live invocation also supplies `--ephemeris-mode moshier --no-optional-points`. It uses no external ephemeris files and does not qualify Chiron, asteroids, or fixed stars. A future file-backed profile is a separately versioned calculation contract.

The worker pins every live calculation option represented in `metadata.calculation_provenance.calculation_profile`. It validates the returned Natal package and archives exact returned bytes before downstream transformation.

## Retention and cache inputs

Retain the complete protected Natal package, exact artifact-byte SHA-256, AGF/SPC wheel identities, runtime manifest and digest, and the full `metadata.calculation_provenance` block. Also retain the caller's normalized request/version reference under API policy.

An AGF calculation cache key must include `source_input.sha256`, `configuration_sha256`, the exact AGF artifact identity, provider/library/data identities, and the requested output contract versions. Subject-scoped artifact reuse additionally includes `source_chart_id`, because canonical IDs are scoped beneath it even though it is deliberately excluded from the geometry hash. Display name and location label do not require astronomy recalculation, but changing them changes descriptive artifact bytes; the API decides whether to regenerate that envelope. Projection profile/context/options belong in a downstream cache key, never the AGF calculation key.

Corrected birth facts, normalization policy, calculation configuration, provider/data, source-chart identity, or AGF contract version produce a new immutable artifact. Existing readings must not be silently overwritten.

## Outputs and startup

The worker consumes the full Natal package, especially `canonical_astrology_graph`, optional `structural_evidence_graph`, registries, evidence, source identity, warnings, and calculation provenance. SPC should consume those structures rather than independently reconstructing natal facts or identity.

At image build/startup:

1. verify wheel hashes before installation;
2. run `pip check`;
3. run `astro-package --version` and compare with the lock;
4. capture and compare `astro-package runtime-manifest` with the release manifest;
5. run `astro-package doctor --require-mode saved --json` for AGF and perform a
   separate SPC startup/compatibility check in the orchestration environment;
6. for live workers, also run `astro-package doctor --require-mode live --json`; and
7. separately verify the release-qualified Python/platform, pyswisseph, and ephemeris-data manifest because doctor checks availability, not qualification.

Stable doctor failure codes are deployment signals: `foundry_version_mismatch`, `packaged_resources_missing`, `spc_missing`, `spc_version_mismatch`, `spc_incompatible`, and `pyswisseph_missing`.

Input validation and deterministic contract incompatibility are terminal until inputs or the pinned generation profile change. Deployment mismatch is not a request retry. Provider/infrastructure failures require explicit API classification and bounded retry policy; AGF makes no universal retryability guarantee. Warning-bearing complete output may proceed only under the API's pinned acceptance policy. AGF does not emit a general partial-but-valid Natal artifact.

## Downstream composition status

AstroWoof's coordinated-readiness audit records a current downstream seam that is
outside AGF's authority: released SBE 0.1.0 requires a projected graph's
`source_chart_id` to equal `natal:<subject_id>`, while AGF 0.6.0 deliberately accepts
any valid caller-owned opaque chart identity. Therefore the published AGF 0.6.0 and
SPC 0.10.0 proof must not be promoted into a claim that every AGF-valid identity is
accepted by the complete AGF/SPC/SBE tuple.

The integration layer must reconcile package subject identity and canonical chart
identity without deriving AGF identity from display name, rewriting projected
lineage, or leaking product database semantics into AGF. This is a project/SBE/API
contract change and qualification task, not a reason to narrow AGF's canonical
identity contract. See AstroWoof project's
[`MILESTONE-001 - Coordinated Natal Pipeline Readiness`](https://github.com/kevin2357/astrowoof-project/blob/main/docs/milestones/MILESTONE-001%20-%20Coordinated%20Natal%20Pipeline%20Readiness.md#blocking-compatibility-seam--opaque-agf-identity-versus-authoring-v01).
