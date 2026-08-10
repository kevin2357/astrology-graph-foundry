# Slice 3 - Interval Evaluation and Classification Engine

**Status:** Gate-ready for review; uncommitted

**Starting boundary:** `1f69033`

## Outcome

AGF now has a provider-independent interval evaluator and a Swiss Ephemeris bridge
for bounded Natal point calculations. It classifies configured ordinary bodies by
possible sign and motion state, classifies body-to-body aspects, retains longitude,
speed, and orb ranges, and fails closed on missing data, provider errors, or proof
budget exhaustion. It does not yet emit a bounded package or graph; that remains
Slice 4.

## Proof policy

The versioned `agf.interval_proof.v1.0.0` profile uses a one-minute refined grid for
the maximum 48-hour input interval. Every longitude segment is enlarged by a
speed-derived envelope with a 1.25 safety factor. Aspect orb ranges likewise include
relative body-motion padding. Endpoint equality is never treated as proof.

This first profile deliberately refines all segments rather than trying to identify
quiet segments heuristically. The retained `initial_step_seconds` field reserves a
future profile-compatible adaptive optimization, but it does not affect v1 results.
The algorithm is a conservative numerical contract, not an analytic proof of Swiss
Ephemeris extrema. Any missing or non-finite provider value and any evaluation-budget
overflow yields `inconclusive` evidence.

## Implemented classifications

- Body evidence retains an unwrapped longitude range and all possible sign indexes.
- Motion evidence retains a speed range and possible direct, retrograde, and
  stationary states.
- Stable signs produce invariant domicile, exaltation, detriment, and fall evidence;
  sect-dependent triplicity is explicitly unavailable rather than inferred.
- Body-to-body evidence distinguishes invariant, conditional, variable, and
  inconclusive results and retains possible aspect types and an orb range.
- Circular longitude unwrapping avoids treating the 359-to-0 crossing as a large
  discontinuity.
- Strength and applying/separating semantics remain deliberately absent.

## Swiss boundary

`evaluate_bounded_natal_interval` converts the normalized UTC interval to Julian
days and evaluates the ordinary configured Swiss body map using the requested
ephemeris mode. Optional file-dependent bodies are not included in this initial
proof set. The bridge returns assessment evidence only; the public Natal pipeline
continues to reject bounded generation until Slice 4 can produce the distinct,
schema-valid artifact family.

## Gate evidence

- Focused interval vectors: **7 passed in 0.28 seconds**.
- Focused interval/live-import/ephemeris/input boundary: **29 passed in 3.59
  seconds**.
- Final full suite: **205 passed in 17.18 seconds**.
- Machine-readable vector inventory:
  [`interval-classification-vectors.json`](interval-classification-vectors.json).
- Native Windows Python 3.12 could not install the qualified pyswisseph version
  because it has no compatible wheel and MSVC was unavailable. Docker then supplied
  the intended Linux/Python 3.11 boundary with pyswisseph 2.10.3.2 in Moshier mode.
- Controlled 24-hour unknown-time run: 1,441 evaluations across 12 bodies in 0.701
  seconds; repeat 0.698 seconds; deterministic hash
  `596d0e53c83f2b11aada42a3903ffcffd6780c54524fe6f9a12a48b0a2ec8dcf`.
- Controlled worst-case 48-hour run: 2,881 evaluations across 12 bodies in 1.273
  seconds; repeat 1.256 seconds; deterministic hash
  `0fb2982a4389c81dade0c432b9be16e7a208e1717acb89cafbad8711c4b5e056`.

## Gate assessment

Slice 3 meets the engine, controlled-live, failure, determinism, and regression
objectives. The measured worst-case calculation cost supports retaining one-minute
full refinement for v1: adaptive pruning would add proof-policy complexity to save
roughly one second per maximal chart in this runtime. `inconclusive` remains
structurally distinct from ordinary variability before Slice 4 makes these records
public.
