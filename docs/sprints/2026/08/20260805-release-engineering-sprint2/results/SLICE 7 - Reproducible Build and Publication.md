# Slice 7 - Reproducible Build and Publication

## Status

Published, freshly downloaded, and verified.

## Frozen release candidate

- Commit: `e36284af0f04e7380113ab141731e18f378ea2dc`.
- Version: `0.6.0`.
- Proposed annotated tag: `astrology-graph-foundry-v0.6.0`.
- Wheel: `astrology_graph_foundry-0.6.0-py3-none-any.whl`.
- Wheel size: 147,578 bytes.
- Wheel SHA-256: `d1b357b1ec0e40faf7070b29e5c25d18e54c9507406518f26587aac46300aa95`.
- Release-manifest SHA-256: `0109ff13d10ebe50b927ffc61b6a56fd2c3d5e864d61a8c2fdb2fb88b5d4c676`.
- Exact SPC 0.10.0 wheel SHA-256: `60bd0f18d3b183d2f4c6375447f90881ab6c22c6138b8f9b8ffe69a246015150`.
- Qualified live-provider wheel SHA-256: `e00d7e08aeafe00938603bc118874b6ca7871c5aaa55aafca8fa2c6d76aff812`.

## Reproducible build proof

Two independent `git archive` exports of the candidate commit were built with `SOURCE_DATE_EPOCH=1785987314`, Python 3.12.13, `build==1.5.0`, `setuptools==83.0.0`, and `wheel==0.47.0`. Both source archives were byte-identical. Both resulting wheels were byte-identical with the size and digest above.

The wheel contains 82 entries, 34 packaged JSON Schemas, MIT license metadata, both advertised console entry points, and a `py3-none-any` purelib tag. A clean outside-checkout install with the exact SPC wheel passed `pip check`, both console version checks, runtime-manifest generation, and projection doctor.

## Qualified support claim

Saved-package mode does not require pyswisseph. Projection mode is qualified with the exact SPC artifact above. Live calculation is qualified only for CPython 3.11 on glibc Linux x86-64 with exact pyswisseph 2.10.3.2, explicit Moshier mode, no external ephemeris files, and optional file-backed points disabled. Controlled live run `31065465973` passed 181 installed-wheel tests and preserved explicit source-chart identity through SPC projection.

This release does not qualify an sdist, other live platforms, Swiss/JPL file-backed modes, Chiron, asteroids, fixed stars, or external ephemeris data. Public service activation remains subject to the separately documented Swiss Ephemeris licensing gate.

## Publication assets

Only these three AGF-owned assets will be published:

1. `astrology_graph_foundry-0.6.0-py3-none-any.whl`
2. `release-manifest.json`
3. `SHA256SUMS.txt`

The independently released SPC wheel is verified input evidence and will not be republished as an AGF asset.

## Publication verification

The product owner explicitly approved publication. Annotated tag `astrology-graph-foundry-v0.6.0` points to the frozen candidate commit, and the [GitHub release](https://github.com/kevin2357/astrology-graph-foundry/releases/tag/astrology-graph-foundry-v0.6.0) contains exactly the three listed AGF assets.

All release assets were downloaded into a fresh directory and matched the published checksum file and GitHub asset digests. The downloaded wheel was installed outside the checkout with the exact SPC wheel; `pip check`, both CLI versions, the 34-resource manifest, projection doctor, and all 181 tests passed. `publication-verification.json` retains the tag object/commit identity, release URL, downloaded hashes, and installed results.
