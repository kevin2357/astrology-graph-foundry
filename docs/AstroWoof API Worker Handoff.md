# AstroWoof API Worker Handoff

**Status:** release-candidate integration contract; artifact placeholders remain unresolved until qualification and publication.

This AGF-owned handoff describes what an AstroWoof worker needs from the canonical-chart stage. It does not define API persistence, jobs, retries, dog/profile models, projection policy, authoring, or UI behavior.

## Artifact lock

```yaml
agf:
  distribution: astrology-graph-foundry
  version: 0.6.0
  wheel: astrology_graph_foundry-0.6.0-py3-none-any.whl
  wheel_sha256: QUALIFY_IN_SLICE_7
  release_commit: QUALIFY_IN_SLICE_7
spc:
  distribution: semantic-projection-core
  version: 0.10.0
  wheel_sha256: 60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150
  verification_status: reverify_download_in_slice_6_or_7
live:
  pyswisseph: DECISION_REQUIRED
  python_platform: DECISION_REQUIRED
  ephemeris_data_manifest: DECISION_REQUIRED
```

Installers should use a hash-enforcing lock containing local or immutable artifact URLs and exact hashes. Install SPC's declared dependency closure, then the exact SPC and AGF wheels. A compatible version range is insufficient production evidence.

## Invocation

The supported Natal call supplies the fields defined by packaged `birth_data_v1.schema.json`: display `name`, local ISO date-time, IANA timezone, latitude, longitude, optional descriptive location label, and explicit `source_chart_id`. `source_chart_id` is the opaque stable chart scope; AstroWoof may derive it from product identity outside AGF, but AGF neither parses nor stores dog/user semantics. Do not use display name, timestamps, filesystem paths, calculation hashes, or projection context as chart identity.

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
5. run `astro-package doctor --require-mode projection --json`;
6. for live workers, also run `astro-package doctor --require-mode live --json`; and
7. separately verify the release-qualified Python/platform, pyswisseph, and ephemeris-data manifest because doctor checks availability, not qualification.

Stable doctor failure codes are deployment signals: `foundry_version_mismatch`, `packaged_resources_missing`, `spc_missing`, `spc_version_mismatch`, `spc_incompatible`, and `pyswisseph_missing`.

Input validation and deterministic contract incompatibility are terminal until inputs or the pinned generation profile change. Deployment mismatch is not a request retry. Provider/infrastructure failures require explicit API classification and bounded retry policy; AGF makes no universal retryability guarantee. Warning-bearing complete output may proceed only under the API's pinned acceptance policy. AGF does not emit a general partial-but-valid Natal artifact.
