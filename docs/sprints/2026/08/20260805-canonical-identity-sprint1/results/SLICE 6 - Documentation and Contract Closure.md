# Slice 6 - Documentation and Contract Closure

## Outcome

The canonical identity contract is now durable in AGF's current documentation
and reconciled with AstroWoof's project-level contracts. The candidate package
version is 0.6.0. Canonical graph schema 1.3.0 remains unchanged, semantic
identity policy is 1.1.0, and relationship-chart identity policy is 1.0.0.

## Implemented guarantees

- Supported live Natal Python, CLI, and helper-tool paths accept optional
  `source_chart_id`.
- Valid explicit identity is preserved exactly; it is not slugged, trimmed, or
  case-folded.
- Explicit carriers must agree. Conflicts fail closed.
- Display name is descriptive when explicit identity is present.
- Canonical objects, relationships, evidence, registries, indexes, claims,
  provenance, and exact references share the resolved scope.
- Repeated finalization is idempotent; deliberate Natal rescoping uses the
  supported whole-package operation.
- Synastry participant order remains directional. Composite and Davison use the
  versioned order-independent participant-derived policy.
- Calculation, sensor, source-chart, product, and projection-context identity
  remain separate.

## Compatibility and version decision

The input field is optional and historical packages remain readable, so this is
not a required-schema break. It is nevertheless a material public identity
contract and changes newly generated Composite/Davison identity. The selected
candidate package version is therefore 0.6.0 rather than 0.5.1. Canonical graph
schema 1.3.0 is retained because no required topology changed.

The name-derived Natal fallback remains deterministic for legacy and exploratory
use, but AstroWoof production policy forbids relying on it. The exact qualified
SPC 0.10.0 wheel remains the Sprint 1 compatibility boundary; release hashes and
published-wheel qualification belong to Sprint 2.

## Documentation closure

AGF now documents validation, precedence, conflict handling, relationship and
temporal implications, projection-context ownership, and migration. A dedicated
migration guide explains regeneration, whole-package rescoping, immutability, and
downstream re-projection.

AstroWoof's integration, canonical-chart, birth-data, and open-question documents
now recognize the implemented 0.6.0 candidate contract. The unresolved product
question is narrowed to API allocation/lifecycle of the opaque ID and corrected-
birth lineage; AGF does not adopt product database semantics.

## Gate evidence

- Full AGF regression suite: 156 passed.
- Packaged schema syntax: 33 JSON Schema resources parsed.
- Current-document relative-link validation: 79 Markdown files passed across
  AGF and astrowoof-project, excluding explicitly historical AGF chat logs.
- Helper dry run preserved `astrowoof:chart:test-1` exactly in delegated CLI.
- Doctor reports source package 0.6.0. Its installed-distribution metadata remains
  0.5.0 because the candidate has not been rebuilt/reinstalled; installed-wheel
  consistency is an explicit Sprint 2 gate.
- The first `python` test invocation failed because `python` is absent from the
  sandbox PATH; the established bundled executable was used successfully.
- The first dry-run output directory under `C:\tmp` was denied by the sandbox;
  the rerun used the repository root and wrote no artifact.

Final whitespace, diff, and status checks are recorded in `LOG.md` and the gate
handoff.

## Deferred to Sprint 2

- unified calculation and normalization provenance;
- clean installed-wheel/version-metadata qualification;
- reproducible build and exact artifact hashes;
- live Swiss Ephemeris qualification;
- tag, publication, download, and re-verification;
- recording the released baseline in AstroWoof project documentation.
