# ADR-0003: Qualify an Explicit Moshier No-File Live Profile

- **Status:** Accepted
- **Date:** 2026-08-05
- **Applies to:** AGF 0.6.0 AstroWoof live qualification
- **Decision owner:** Astrology Graph Foundry qualification boundary; public-service licensing remains project-owned

## Context

The initially assumed API runtime used CPython 3.12, but no suitable published binary pyswisseph wheel was available for the intended live qualification. A source-built native dependency would add compiler, base-image, and native-build provenance. AstroWoof did not require external Swiss Ephemeris data files, Chiron, asteroids, or fixed stars for this release.

Historical `auto` behavior requests Swiss Ephemeris first and may fall back. An empty data directory alone does not prove which calculation path actually ran.

## Decision

Qualify live calculation only for CPython 3.11 on glibc Linux x86-64 using the exact published `pyswisseph==2.10.3.2` manylinux wheel with SHA-256 `e00d7e08aeafe00938603bc118874b6ca7871c5aaa55aafca8fa2c6d76aff812`.

The invocation explicitly requests `moshier`, uses an isolated empty ephemeris directory, and disables optional file-backed points. AGF records returned Swiss Ephemeris flags, decodes the observed mode, and fails if explicit requested and observed modes disagree. Calculation profile `agf.calculation_profile.v1.1.0` includes the requested ephemeris mode.

## Alternatives rejected or deferred

- **Build pyswisseph from source for CPython 3.12:** technically possible but creates a larger native artifact qualification surface without product need.
- **Use historical `auto`:** fallback is observable but not a sufficiently explicit production assumption.
- **Bundle `.se1`, JPL, star, asteroid, or Chiron data now:** no current requirement justified choosing, licensing, packaging, and hashing those assets.
- **Generalize from one Linux run to all platforms:** unsupported by evidence.

## Consequences

The qualified claim is intentionally narrow. Other Python ABIs, operating systems, libc families, source builds, Swiss/JPL modes, and external data sets require separate evidence and likely a new calculation-profile version. Saved-package and projection modes remain usable without pyswisseph.

Technical qualification does not authorize public Swiss Ephemeris service use. The owning project must approve an AGPL-compliance or Professional License path before activation.

See [Qualified Live Calculation Profile](../Qualified%20Live%20Calculation%20Profile.md).
