# Astrology Graph Foundry 0.7.0

AGF 0.7.0 adds bounded birth-time Natal generation while preserving the exact
Natal contracts and explicit caller-owned chart identity introduced in 0.6.0.

Highlights:

- exact, bounded, and unknown-time birth-time modes;
- exhaustive valid-minute evaluation through a 48-hour maximum;
- continuous safety envelopes and explicit uncertainty evidence;
- invariant ordinary-body signs, motion, dignity, and aspects;
- bounded coordinate, declination, antiscia, contra-antiscia, and harmonic evidence;
- invariant derived and declination relationships;
- deterministic invariant-subgraph indexes and evidence-family grouping;
- explicit reduced capabilities and exact-only consumer rejection; and
- 39 packaged JSON Schemas plus calculation, normalization, identity, and proof
  provenance.

The qualified live profile is CPython 3.11 on glibc Linux x86-64 with
`pyswisseph==2.10.3.2`, explicit Moshier mode, no external ephemeris files, and
optional file-backed points disabled. The wheel was built twice from independent
clean exports and matched byte-for-byte.

SPC 0.10.0 remains compatible with AGF's exact canonical graph but does not yet
consume the new bounded graph vocabulary. Bounded SPC/SBE enablement is separate
follow-on work.

Published assets are deliberately wheel-only:

- `astrology_graph_foundry-0.7.0-py3-none-any.whl`
- `release-manifest.json`
- `SHA256SUMS.txt`

Production consumers must pin the wheel by the SHA-256 recorded in the checksum and
release-manifest assets.
