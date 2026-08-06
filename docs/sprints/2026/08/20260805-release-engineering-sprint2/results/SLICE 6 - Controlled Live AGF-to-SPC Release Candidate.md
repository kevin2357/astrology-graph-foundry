# Slice 6 - Controlled Live AGF-to-SPC Release Candidate

## Outcome

AGF 0.6.0 passed its controlled live release-candidate gate on CPython 3.11.15, Ubuntu 24.04 x86-64. The installed candidate used the exact qualified pyswisseph 2.10.3.2 manylinux wheel in explicit Moshier mode, with no external ephemeris files and optional file-backed points disabled. Installed SPC 0.10.0 projected the live canonical graph and preserved explicit chart identity.

## QA finding and correction

The first branch run failed before installation because unauthenticated HTTP access cannot download a release asset from the private SPC repository. The asset tag, filename, and hash were correct. The workflow now uses authenticated `gh release download` through the encrypted `SPC_RELEASE_TOKEN` repository secret and independently checks the downloaded wheel SHA-256. No credential is present in source, retained evidence, or logs.

## Qualified runtime and artifacts

- AGF commit: `3b34b72d97b2fc730cffec90aaef22b338e8689e`.
- Candidate AGF wheel SHA-256: `6895a744395bf07b3a554fe372dc6c85380d96552f3c19220ff524f932ed5be1`.
- SPC 0.10.0 wheel SHA-256: `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`.
- pyswisseph 2.10.3.2 wheel SHA-256: `e00d7e08aeafe00938603bc118874b6ca7871c5aaa55aafca8fa2c6d76aff812`.
- Runtime: Linux x86-64, CPython 3.11.15.
- Provider: explicit Moshier requested and observed; zero external ephemeris files; optional points disabled.

The AGF wheel is a qualification-branch candidate, not the final release artifact. Slice 7 rebuilds twice from the final approved commit and requires byte-identical output before publication approval.

## Controlled calculations

Baseline, standard-time, daylight-time, and coordinate-edge Natal fixtures all completed and validated. Every fixture reported the same canonical configuration hash, `e9ea6d38d8123a98594e542a0cb6309c9e32610e57915cacd17a75bf81e4868f`, while retaining its distinct normalized source-input and canonical-graph hashes. Repeating the calculation produced semantically identical output.

The installed AGF-to-SPC baseline projection produced 188 objects and 3,143 relationships. Its projected `source_chart_id` remained exactly `agf:qualification:baseline`, proving the Sprint 1 identity contract across installed artifacts.

## Gate verification

- Successful GitHub Actions run: [31065465973](https://github.com/kevin2357/astrology-graph-foundry/actions/runs/31065465973).
- Exact SPC and pyswisseph wheel hash checks passed before installation.
- Candidate runtime installation and `pip check` passed.
- Controlled live calculation and installed SPC projection passed.
- Full suite against installed wheel code: 181 passed in 4.15 seconds.
- Compact evidence was downloaded and retained as `controlled-live-summary.json` and `cross-repository-compatibility.json`.

The qualified claim is intentionally limited to the tested Linux x86-64/CPython 3.11/Moshier combination. It does not qualify Swiss-file mode, JPL mode, Chiron, asteroids, fixed stars, other platforms, or a public-service licensing posture.
