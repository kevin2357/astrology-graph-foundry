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
- Initial input recommendation: tagged `exact`, `bounded`, and `unknown_time` basis;
  CLI names `--birth-local-earliest` and `--birth-local-latest`.
- Key safety finding: endpoint equality is insufficient because of retrograde loops,
  longitude wraparound, stations, interior aspect extrema, and multiple crossings.
- Version and release impact remain undecided pending Slice 1 audit.
- No slice result exists and no gate has been claimed complete.

## 2026-08-09 — Planning approval and clean boundary

- User approved the documented direction, requested all current AGF/API changes be
  committed and pushed, and authorized beginning Slice 1.
- AGF planning/design commit: `7d071d2` (`Plan bounded birth-time natal
  calculation`), pushed to `origin/main`.
- AstroWoof API roadmap commit: `143d80d` (`docs: define bounded birth-time natal
  direction`), pushed to `origin/main`.
- Slice 1 began from clean AGF `7d071d2a17b3bf91fd5244f2adefc64439d9ca24`.

## 2026-08-09 — Slice 1 contract and dependency audit

- Traced exact `birth_local` through `BirthData`, packaged schema, main and daily
  CLIs, helper tools, Natal, Synastry, Composite, and Davison live inputs.
- Confirmed live Natal computes houses before bodies and then derives house
  placements, angles, sect, lots, dignities, antiscia, harmonics, declinations, and
  exact aspects from one Julian day.
- Confirmed graph compilation turns scalar longitudes into exact sign/degree facts
  and generates additional exact relationships; midpoint filtering after compilation
  cannot produce an honest bounded graph.
- Confirmed `TransitableChart` currently hard-codes longitude-aspect capability and
  several timing pipelines use exact natal longitude, houses, or reference event.
- Audited package families. Initial recommendation is bounded Natal plus explicit
  rejection by Transit, Synastry, Composite, Davison, returns, profections, and
  temporal activation until each has reviewed bounded semantics.
- Inspected SPC 0.10.0 read-only. Its compatibility manifest accepts canonical
  static graph 1.3.0; bounded vocabulary requires a new explicit compatibility
  release rather than opportunistic projection.
- Recorded proposed input decisions: tagged `exact`, `bounded`, and `unknown_time`;
  `earliest_local`/`latest_local`; inclusive supplied bounds; calendar-day semantics;
  zero-width uses exact mode; initial 48 elapsed-hour maximum candidate.
- Recorded the initial fact matrix: invariant sign, motion, separated sign-only
  dignity, and invariant body aspects may become canonical; scalar longitude/orb are
  bounded evidence; houses, angles, sect, and dependent lots are unavailable;
  declination, antiscia, harmonics, and fixed-star interval semantics are deferred.
- Environment finding: the bundled Python initially lacked pytest and the project
  test dependencies. Installed pytest, jsonschema, and local editable SPC 0.10.0 and
  AGF 0.6.0 outside the repository.
- Initial full test attempt failed during collection because AGF/SPC/jsonschema were
  not installed; this was an environment failure, not a repository regression.
- Full baseline after environment setup: 181 tests passed in 6.15 seconds.
- Added the Slice 1 review and machine-readable fact-dependency matrix. No production
  code or schema changed.

## 2026-08-10 — Slice 1 approval and future-integration retention

- User approved the three-mode input contract with `unknown_day` renamed to the less
  ambiguous `unknown_time`.
- Approved inclusive supplied bounds, whole-local-day semantics, zero-width exact
  routing, and a hard bounded-v1 maximum of 48 elapsed UTC hours.
- Approved the conservative initial fact scope and exact-only rejection matrix for
  other package families.
- Clarified version direction: exact Birth Data v1, Natal Dataset 1.1.0, canonical
  graph 1.3.0, and existing SPC compatibility remain unchanged. Bounded output gets
  a distinct input/package/graph family and requires a later SPC compatibility
  sprint.
- User requested explicit preservation of evidence useful to later bounded Transit
  and Synastry work, especially longitude and orb ranges.
- Added append-per-slice Transit and Synastry integration journals. Slice 1 entries
  capture the evidence and contract seams discovered so far.
