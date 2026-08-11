# Slice 1 — Terrestrial-Frame Contract and House-System Audit

**Status:** Gate 1 candidate; awaiting human review

## Outcome

The bounded terrestrial-frame contract is now narrow and testable. The recommended
initial profile supports Placidus (`P`) as AGF's production default and Whole Sign
(`W`) as a deliberately qualified polar-capable alternative. Every other system is
unsupported in bounded mode until it receives its own topology and provider
qualification; Gauquelin sectors are structurally outside the twelve-house contract.

This slice changes no runtime behavior. It found one exact-Natal defect that must be
corrected before Whole Sign can enter the bounded implementation: `house_data()`
rotates Swiss Ephemeris' already-numbered cusp sequence toward the Ascendant. That is
harmless for systems whose first cusp equals the Ascendant, but it renumbers valid
Whole Sign, Vehlow, Meridian, Horizon, and Morinus output.

## Evidence

The controlled probe used Swiss Ephemeris 2.10.03 in the retained Linux QA image.
Placidus and Koch succeeded at latitude 66.0 degrees and raised `swisseph.Error` at
66.6, 67, 80, and 89.9 degrees for the fixed probe instant. Whole Sign and the other
probed nonquadrant alternatives completed at all tested latitudes. The official
documentation confirms that Placidus and Koch cannot be calculated beyond the polar
circle and documents fallback/error behavior:
[Swiss Ephemeris programming interface](https://www.astro.com/swisseph/swephprg.htm?lang=t&nho2=1041&nhor=1).

The probe exposed another unsafe boundary: unrecognized code `Z` has no house name
but behaves like Placidus in the binding. AGF currently records requested `Z` as
provenance, creating mislabeled output instead of rejecting the configuration.

Swiss Ephemeris exposes `houses_ex2` cusp and auxiliary-point speeds in the pinned
pyswisseph binding. Upstream documents those daily motions and the twelve-versus-36
cusp distinction:
[Swiss Ephemeris house API](https://www.astro.com/swisseph/swephprg.htm?nhor=1024).

Machine-readable policy is in
[`house-system-audit-matrix.json`](house-system-audit-matrix.json); the reproducible
probe is [`house-system-probe.py`](house-system-probe.py).

## Contract candidate

- Preserve provider cusp numbering after numeric normalization. Do not equate house
  1 with the Ascendant for systems that define them differently.
- Assign longitudes on half-open circular intervals: cusp N is included in house N;
  the twelfth interval wraps through zero.
- Minute enumeration remains the oracle and witness set, but is not alone continuous
  proof. For smooth systems, unwrap labeled points independently and conservatively
  envelope between-minute motion with `houses_ex2` speeds.
- Whole Sign is piecewise constant. Ascendant sign ingress changes all twelve cusps
  and must create alternative frame states unless continuous evidence excludes it.
- Provider error, non-finite output, topology violation, or inadequate speed proof
  makes the terrestrial family inconclusive. Independent celestial evidence remains
  valid.
- Never silently substitute another system. No midpoint/noon frame is canonical.

## Implementation consequence

Slice 2 must begin with two exact-path regression repairs: preserve Swiss cusp order,
and reject unrecognized or structurally unsupported codes before provider calls.
The bounded profile should initially admit only `P` and `W`. Placidus failure
invalidates the terrestrial family, not the complete artifact. Whole Sign must pass
numbering and Ascendant-ingress fixtures before it is advertised.

This is additive bounded capability, but correcting mislabeled or renumbered exact
output is behaviorally significant and belongs in the next release notes.

## Gate checks

- Supported-system matrix: complete; `P`/`W` recommended initially.
- Failure and continuity policy: complete.
- Polar and wraparound fixtures: specified; executable regressions open Slice 2.
- Sprint 1 evidence contract: unchanged.
- Baseline suite: passed (239 tests).
- Markdown/whitespace and diff checks: passed.
- Human review: pending.

## Deferred systems

Koch, Porphyry, Regiomontanus, Campanus, equal variants, Vehlow, Meridian,
Horizon/Azimuth, Polich/Page, Alcabitius, Morinus, and Krusinski require individual
qualification. Gauquelin's 36 clockwise sectors require a different schema.
