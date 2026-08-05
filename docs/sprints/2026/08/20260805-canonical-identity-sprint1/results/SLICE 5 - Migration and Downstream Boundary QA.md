# Slice 5 — Migration and Downstream Boundary QA

**Status:** Gate candidate; awaiting human approval

## Outcome

The new identity contract passes saved-package replay and AGF-to-SPC projection against the exact qualified SPC 0.10.0 wheel. Explicit source identity survives unchanged, while different projection contexts produce different projection identities without contaminating AGF source identity.

## Exact SPC Artifact

- Distribution: `semantic-projection-core`
- Version: 0.10.0
- Wheel SHA-256: `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`
- Installed editable: false
- Runtime smoke: `ok`
- Release compatibility contract: `semantic_projection.release_compatibility.v1`
- Runtime package fingerprint: `209be10ee879312293d7955f76dc7d9c0ade2dcb4e3a2fead11d424483f80611`
- Semantic resource fingerprint: `74ba2450c20e4b8c636ba2ffcb0a8b6db8ae3e0964f552cfdfbf78bde1145afd`

The wheel's bytes were independently hashed before installation and matched SPC's consumer handoff.

## Qualification Shape

A clean temporary Python 3.12 environment was created outside normal source imports. SPC was installed from the exact wheel. The current AGF candidate was installed editable because AGF wheel qualification belongs to release Sprint 2.

SPC's installed runtime smoke verified:

- distribution, package, and engine version 0.10.0;
- non-editable SPC installation;
- all six console scripts;
- all three profile entry points;
- 13 packaged contexts;
- 101 runtime resources;
- 44 semantic resources;
- 21 schemas; and
- the release compatibility contract.

## Boundary Assertions

- An explicit mixed-case AGF `source_chart_id` survives projection exactly in `source_identity.source_chart_id`, `source_chart_ids`, and `sensor_instance_id`.
- Changing only downstream `ProjectionContext.application_context` changes SPC projection/context identity but not AGF source identity.
- AGF input is not mutated by projection.
- Source-selection policy still selects True Node and Part of Fortune canonical representatives without treating excluded aliases as mapping failures.
- Saved explicit-identity packages serialize, reload, and re-finalize idempotently.
- Legacy name-derived fixtures remain deterministic.
- Temporal target/static identity guards continue to reject mismatches.

## QA Finding

The first new projection test expected a nonexistent top-level `projection_identity` field. Inspection showed SPC's public native artifact carries `metadata.projection_id` and a runtime context content hash instead. The test was corrected to the real contract. Source identity preservation had already passed; no production defect was concealed.

The first attempt to create a temporary environment under `C:\tmp` was denied by local filesystem permissions. The qualification environment was instead created under AGF's ignored `outputs` directory. This did not change repository content and is cleaned at the gate.

## Test Evidence

- Exact-SPC installed boundary suite: 53 passed.
- Full AGF regression suite: 156 passed.
- SPC runtime smoke: status `ok`.
- Compact evidence: `cross-repository-compatibility.json`.

## Compatibility Conclusion

AGF's identity contract remains compatible with SPC 0.10.0's public static and temporal source boundary. SPC does not reconstruct, normalize, or reinterpret canonical chart identity. The production handoff must still pin the exact SPC wheel/hash; AGF's permissive dependency declaration alone is not a production lock.

The next release sprint must repeat this proof with an installed AGF wheel rather than an editable candidate checkout.

## Files Changed

- `tests/test_external_projection_integration_chunk28.py`
- `tests/test_chart_scoped_canonical_ids.py`
- `docs/sprints/2026/08/20260805-canonical-identity-sprint1/results/cross-repository-compatibility.json`
- this result and the append-only sprint log

## Gate Decision Requested

Approve the saved-package and exact-SPC compatibility evidence before committing Slice 5 and beginning final documentation/version closure.

