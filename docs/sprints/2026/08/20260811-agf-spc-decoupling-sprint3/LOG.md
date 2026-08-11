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
