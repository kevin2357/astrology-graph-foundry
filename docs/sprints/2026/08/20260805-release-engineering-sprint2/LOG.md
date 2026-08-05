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

