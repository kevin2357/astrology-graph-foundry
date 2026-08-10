# Bounded Birth-Time Natal Sprint Log

This log is append-only during execution. Planning entries do not represent
completed implementation slices.

## 2026-08-09 — Planning baseline

- User accepted bounded birth-time invariant evidence as the intended AGF direction
  and requested durable AGF/API documentation plus a sprint plan for review.
- Repository start: `C:\dev\github\astrology-graph-foundry` on `main`, tracking
  `origin/main`, clean at commit `5ff3a9e` (`Consolidate AGF 0.6 release
  documentation`).
- No production implementation was authorized or performed in this planning pass.
- Current AGF evidence: `BirthData` and `birth_data_v1` require one `birth_local`;
  `build_live_natal_chart` attaches `ZoneInfo`, calculates one UT Julian day, houses,
  bodies, angles, sect, lots, dignities, derived coordinates, and exact aspects.
- Current graph evidence: exact longitude drives object sign/degree and generated
  relationships; a midpoint/noon object would therefore become false canonical
  precision if reused unchanged.
- Current capability evidence: `TransitableChart` advertises longitude, house,
  angle, and semantic activation capabilities that need reduced bounded semantics.
- Provider evidence: Swiss Ephemeris supports arbitrary UT calculations and returns
  speed, making interval evaluation feasible; AGF still needs a versioned proof and
  classification layer above point calls.
- Cross-project evidence: AstroWoof currently implements/documents warned-noon MVP
  behavior. The roadmap now records bounded calculation as a successor, not an
  implemented replacement.
- Initial scope recommendation: signs, bounded longitude, motion state,
  sign-dependent dignity, and ordinary body-to-body aspects; houses, angles, sect,
  and dependent lots unavailable initially.
- Initial vocabulary: `invariant`, `conditional`, `variable`, `unavailable`, and
  `calculation_failed`.
- Initial input recommendation: tagged `exact`, `bounded`, and `unknown_day` basis;
  CLI names `--birth-local-earliest` and `--birth-local-latest`.
- Key safety finding: endpoint equality is insufficient because of retrograde loops,
  longitude wraparound, stations, interior aspect extrema, and multiple crossings.
- Version and release impact remain undecided pending Slice 1 audit.
- No slice result exists and no gate has been claimed complete.
