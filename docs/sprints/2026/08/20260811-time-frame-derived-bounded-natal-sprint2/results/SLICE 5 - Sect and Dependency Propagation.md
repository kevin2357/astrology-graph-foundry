# Slice 5 — Sect and Dependency Propagation

**Status:** Gate 5 candidate; awaiting human review

## Outcome

Bounded Natal now classifies sect as invariant day, invariant night, variable, or
unavailable using the qualified Sun-house evidence. The exact-Natal rule remains
authoritative: houses 7–12 are day and houses 1–6 are night. No independent sunrise
approximation or representative instant is introduced.

Triplicity evidence is derived only when both the body's sign and sect are
invariant. Variable sunrise/sunset domains therefore retain both sect alternatives
and promote no triplicity ruler. Canonical graph v1.6.0 adds an invariant sect-state
object and optional triplicity fields on independently canonical body objects.

## Controlled results

Four-hour daytime and nighttime Denver intervals each produced one invariant sect
and twelve invariant triplicity records. A three-hour sunrise-crossing interval
produced both day and night and zero invariant triplicity records. See
[`sect-live-summary.json`](sect-live-summary.json).

## Contracts and gate

- `include_sect=False` produces explicit unavailable evidence.
- Calculation profile advances to v1.9.0; dataset schema remains v1.0.0.
- Day, night, horizon crossing, configuration disablement, prerequisite propagation,
  schema/reference integrity, and controlled Linux execution pass.
- Full host suite: 250 passed; JSON and `git diff --check` pass.
- Lots and formula branches remain Slice 6.
- Human review: pending.
