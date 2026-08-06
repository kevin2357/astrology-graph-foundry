# Qualified Live Calculation Profile

## AstroWoof qualified profile

AGF 0.6.0 intentionally qualifies a narrow live runtime:

| Dimension | Qualified value |
|---|---|
| Python | CPython 3.11 on Linux x86-64 |
| Linux ABI | glibc `manylinux_2_17` or newer-compatible host |
| Swiss wrapper distribution | `pyswisseph==2.10.3.2` |
| Published wheel SHA-256 | `e00d7e08aeafe00938603bc118874b6ca7871c5aaa55aafca8fa2c6d76aff812` |
| AGF ephemeris mode | `moshier` |
| External ephemeris files | none |
| Optional Chiron | disabled |
| Asteroids and fixed stars | disabled |
| Calculation profile | `agf.calculation_profile.v1.1.0` |

This profile uses the published CPython 3.11 manylinux wheel instead of creating
an AGF-owned native build. The production lock must install that exact artifact
by hash. A source build, a musllinux/Alpine wheel, another Python ABI, or the
separate `pysweph` distribution is a different runtime and requires separate
qualification.

## Explicit provider behavior

Invoke live Natal generation with:

```text
--ephemeris-mode moshier --no-optional-points
```

AGF requests `FLG_MOSEPH` directly and records the ephemeris flags returned by
Swiss Ephemeris. Explicit `moshier` and `swiss` modes fail if the observed mode
does not exactly match the request. Legacy `auto` retains historical Swiss-first
fallback behavior but is not the qualified AstroWoof production profile.

The no-file profile does not claim Swiss `.se1`, JPL, Chiron, asteroid, or fixed
star support. Adding any of those later creates a new calculation-profile version
with separately pinned data and runtime evidence; it does not alter this profile.

## Qualification evidence

The retained Linux evidence proves:

- imports originate from installed AGF and SPC wheels rather than source trees;
- the exact pyswisseph wheel hash and Python/platform tags;
- an empty external-data inventory and an isolated empty ephemeris directory;
- returned flags report only Moshier for all calculated ecliptic and equatorial positions;
- explicit source-chart identity survives Natal generation, schema validation, serialization, and installed SPC projection;
- repeated controlled inputs preserve canonical semantic content;
- DST-valid and coordinate-boundary fixtures behave under the accepted birth-input contract; and
- optional Chiron, asteroids, and fixed stars are absent rather than warning-skipped into the qualified result.

The Swiss Ephemeris licensing activation gate remains project-owned. Passing
technical qualification does not authorize public service use.

The successful controlled-live run and exact artifact hashes are retained in
the [Slice 6 report](sprints/2026/08/20260805-release-engineering-sprint2/results/SLICE%206%20-%20Controlled%20Live%20AGF-to-SPC%20Release%20Candidate.md)
and the [0.6.0 release manifest](sprints/2026/08/20260805-release-engineering-sprint2/results/release-manifest.json).
