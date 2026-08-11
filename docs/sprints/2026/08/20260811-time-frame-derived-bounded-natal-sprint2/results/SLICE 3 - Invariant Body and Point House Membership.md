# Slice 3 — Invariant Body and Point House Membership

**Status:** Gate 3 candidate; awaiting human review

## Outcome

Bounded Natal now evaluates house membership for every core body and every enabled
antiscia, contra-antiscia, and harmonic point at every valid state. An invariant
house number is copied onto a canonical bounded object only when all sampled charts
agree and a conservative relative-motion envelope cannot reach either moving cusp
between samples. Otherwise, the uncertainty registry preserves all observed or
continuously admitted houses and transition witnesses.

No exact longitude, representative frame, or majority vote participates in
promotion. Sign and house certainty remain independent: either may be invariant
while the other varies.

## Continuous boundary proof

For each minute segment, the evaluator considers the body's maximum endpoint speed,
each bounding cusp's maximum endpoint speed, elapsed Julian time, and the accepted
1.25 safety factor. If that combined envelope can reach a boundary, the adjacent
house is added to the possibility set even when both sampled endpoints occupy the
same house. This fails safely near cusps and handles the house-12/house-1 wrap using
the same half-open rule as exact Natal.

Invariant objects receive `house_number` plus a resolvable
`house_uncertainty_evidence_ref`. Variable objects carry no canonical house field.
The full membership registry remains available for later Transit and Synastry work.

## QA finding

Kevin's generated four-hour chart exposed Julian-day float noise that produced 242
states instead of the intended inclusive 241. A shared grid helper now snaps values
within a small numerical tolerance to the nearest integral segment count. Both the
celestial and terrestrial evaluators use it, preventing date-dependent phantom
evaluations without reducing the requested one-minute resolution.

## Controlled live results

- Kevin 1:00–5:00 PM: 241 states, 108 membership records, zero invariant and 108
  variable. The implementation correctly refuses to rescue a house placement across
  such a wide rotating-frame interval.
- Kevin 1:00–1:30 PM: 31 states, 83 invariant and 25 variable records. Ordinary
  positive examples include Sun house 9, Moon house 2, Mercury house 10, Venus house
  11, and Mars house 8 for that earlier half-hour—not Kevin's exact 4:15 chart.

See [`house-membership-live-summary.json`](house-membership-live-summary.json).

## Contract and versioning

- `house_placements` now means `assessed_with_invariant_house_promotion`.
- Capability `supports_bounded_invariant_house_membership` is true.
- Bounded calculation profile advances to v1.7.0.
- Dataset schema remains at 1.0.0. Bounded canonical graph advances additively to
  1.4.0 so an object may carry an invariant house even when sign and motion vary.
- No house-transit capability is enabled; range-aware Transit remains separate.

## Gate checks

- All cusp boundaries and circular wrap: covered.
- Positive invariant and negative variable promotion: covered.
- Continuous near-boundary safety: covered by relative-motion admission.
- Body and derived-point evidence references: deterministic and resolvable.
- Exact four-hour grid regression: covered.
- Controlled Linux live qualification: passed.
- Full host suite: 246 passed.
- JSON validation and `git diff --check`: passed.
- Human review: pending.
