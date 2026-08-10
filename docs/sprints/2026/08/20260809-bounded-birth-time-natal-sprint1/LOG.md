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

## 2026-08-10 — Slice 1 approval and commits

- Committed approved AGF Slice 1 documentation and evidence as `41994dc`
  (`Document bounded natal Slice 1 contract`).
- Committed the two authorized API terminology updates independently as `2df7b4c`
  (`docs: rename unknown birth-time mode`), preserving unrelated API sprint work.
- Began Slice 2 from AGF `41994dc`.

## 2026-08-10 — Slice 2 input, normalization, and provenance boundary

- Added separate `BirthTimeBasis`, `NormalizedBirthTimeBasis`, and
  `BoundedBirthData` models while leaving exact `BirthData` unchanged.
- Implemented unique-wall-time resolution with explicit nonexistent/ambiguous
  rejection, optional caller-resolved UTC verification, inclusive bounded endpoints,
  whole-local-day `unknown_time`, and hard 48-hour validation.
- Added packaged `bounded_birth_data_v1.schema.json`; exact Birth Data v1 is unchanged.
- Added bounded-only source normalization/provenance hashing under
  `agf.bounded_birth_time.normalization_policy.v1.0.0`.
- Added Natal-only CLI flags and standard helper forwarding. Other package-family
  CLIs intentionally do not expose bounded input.
- Valid bounded invocation stops before calculation with a deliberate implementation
  error assigned to Slice 3.
- Added focused schema, normalization, DST, cross-midnight, invalid-bound, hash,
  identity, CLI, helper, and pipeline-boundary tests.
- Initial focused suite: 48 passed.
- First full suite found three installed-resource count assertions after adding the
  new schema: 193 passed, 3 failed. Updated the count from 34 to 35 and asserted the
  new schema name explicitly.
- Full suite after the resource fix: 196 passed in 16.29 seconds.
- Final focused bounded/helper/resource suite: 34 passed in 8.75 seconds.
- `compileall` passed.
- Retained compact normalization vectors with deterministic hashes for bounded,
  DST-short, and DST-long examples.
- Installed the declared Ruff development dependency into the external bundled
  Python runtime. Import-only formatting was applied to changed files.
- Targeted Ruff passed with the pre-existing legacy exact-Natal naive `created_at`
  warning explicitly excluded; this slice did not alter that artifact field.
- Full suite after helper coverage and import normalization: 197 passed in 17.10
  seconds.
- Added a regression test tying retained normalization vectors back to the live
  normalization/hash implementation.
- Final full Slice 2 suite: 198 passed in 18.57 seconds.
## 2026-08-10 - Slice 3 interval evaluation and classification

- Began from approved Slice 2 commit `1f69033` with a clean worktree.
- Added provider-independent interval evaluation under proof profile
  `agf.interval_proof.v1.0.0`.
- Chose full one-minute refinement for v1 rather than endpoint or sparse-sample
  inference. Longitude and aspect ranges carry speed-derived safety envelopes.
- Added circular unwrapping, ingress classification, station-aware motion ranges,
  sign-only dignity classification, invariant/conditional/variable aspects, orb
  ranges, evaluation budgets, and fail-closed provider behavior. Sect-dependent
  dignity components remain explicitly unavailable.
- Added the Swiss Ephemeris bridge for ordinary configured bodies without yet
  producing a bounded package.
- Focused vectors: 7 passed; combined affected tests: 29 passed; final full suite:
  205 passed in 17.18 seconds.
- Attempted controlled live evidence in bundled Python 3.12. No compatible
  pyswisseph wheel was available and source build failed for lack of MSVC. Recorded
  this as an environment limitation; it does not convert into ordinary uncertainty.
- Added compact machine-readable vectors and updated both future-integration
  journals. Slice remains uncommitted pending Gate 3 approval.

### Controlled-live follow-up

- User authorized Docker for the missing Linux/Python 3.11 evidence.
- First container import correctly exposed AGF's SPC runtime dependency. PyPI did not
  publish SPC 0.10.0, and a Windows-mounted wheel was unreadable inside Docker, so
  the successful proof mounted the local SPC 0.10.0 source boundary read-only.
- Docker `python:3.11-slim` installed pyswisseph 2.10.3.2 and ran Moshier calculations
  against the AGF checkout mounted read-only.
- The 24-hour case completed 1,441 evaluations over 12 bodies in 0.701 seconds; its
  repeat took 0.698 seconds and produced an identical hash.
- The maximum 48-hour case completed 2,881 evaluations over 12 bodies in 1.273
  seconds; its repeat took 1.256 seconds and produced an identical hash.
- This closes the Slice 3 controlled-live gap and supports keeping full one-minute
  refinement in proof profile v1 rather than adding adaptive pruning now.
- User approved Gate 3 and expressed a firm preference for the simple, intuitive
  minute-by-minute proof model unless later production profiling demonstrates a
  pressing need to optimize it.

## 2026-08-10 - Slice 4 bounded artifact and canonical graph

- Began from approved and pushed Slice 3 commit `b6e9a9b`.
- Added distinct bounded Natal Dataset 1.0.0 and bounded canonical graph 1.0.0
  schemas; exact schemas remain unchanged.
- Added invariant-only canonical promotion, complete uncertainty assessment,
  resolvable uncertainty references, explicit feature dispositions, and reduced
  capability advertisement.
- Added bounded calculation provenance binding normalized input, proof profile,
  object/aspect policy, and configuration hash.
- Artifact tests found local bounded IDs were not recognized by shared source-chart
  scoping. Changed only their pre-finalization namespace to `natal:bounded:*`; the
  finalized vocabulary remains `bounded_natal_body`.
- Artifact tests also found bounded packages needed chart-stable sensor identity for
  repeat finalization. The semantic identity classifier now treats bounded Natal as
  a Natal chart family while calculation identity remains separate.
- Added a dedicated bounded calculation-provenance schema rather than leaving the
  new profile as an unconstrained metadata object.
- Focused suite: 36 passed. Final full suite: 209 passed in 17.54 seconds.
- Docker Linux/Python 3.11 generated a real Moshier unknown-time package in 0.655
  seconds with 11 invariant objects, 13 invariant relationships, no scalar canonical
  precision, no dangling endpoints, and 78 complete body/aspect assessments.
- Added compact artifact evidence and updated both future-integration journals.
  Slice remains uncommitted pending Gate 4 approval.

## 2026-08-10 - Slice 5 downstream and package-family compatibility

- Began from approved and pushed Slice 4 commit `930a3cc`.
- Added a shared bounded-package classifier and an explicit compatibility error for
  exact-only consumers.
- Guarded AGF static projection, `TransitableChart`, Synastry/Composite participant
  loading, and Davison participant loading. Transit, returns, eclipse target
  activation, and profections inherit the `TransitableChart` guard.
- Tests prove analysis type or graph type independently triggers rejection and that
  serialization/reload does not weaken the boundary.
- Read SPC 0.10.0 compatibility and validation contracts: static graph 1.3.0 is the
  only supported version; bounded graph 1.0.0 requires a separate SPC sprint.
- Read the SBE authoring boundary: it consumes projected artifacts and retains
  source graph references; it should not receive bounded AGF canonical input before
  SPC defines the projection contract.
- Existing qualified worker image passed SPC runtime smoke and AGF doctor with
  installed AGF 0.6.0/SPC 0.10.0/Python 3.11.15.
- Installed live exact Natal-to-Woofmap proof produced 17 objects, 61 relationships,
  full eligible coverage, and preserved `gate:exact` identity. Initial inspection
  used an obsolete result wrapper key; the actual SPC root contract passed.
- Focused compatibility suite: 16 passed in 0.40 seconds. Full suite: 214 passed in
  17.33 seconds.
- Added compact cross-repository compatibility evidence and updated both future
  integration journals. Slice remains uncommitted pending Gate 5 approval.

## 2026-08-10 - Slice 6 migration, qualification, and release decision

- Began from approved and pushed Slice 5 commit `f3c1859`.
- Selected AGF 0.7.0 as the candidate version; exact graph/package contracts remain
  unchanged while bounded contracts begin at their own v1/1.0.0 versions.
- Updated the bounded calculation guide from proposed to implemented, added CLI and
  package guidance, consumer/API handoff, candidate release notes, compatibility and
  runtime-inventory notes, and explicit published-versus-candidate status.
- Built two byte-identical wheels under controlled build inputs. Candidate wheel
  SHA-256: `181190606a9373ef3bb091803b015c2a962155e289aa04e30a20740e08e4bd05`.
- Clean installed Linux/Python 3.11 qualification used exact SPC 0.10.0 and
  pyswisseph 2.10.3.2. Both CLIs loaded; live doctor passed; all 38 schemas were
  packaged with manifest hash
  `64178c9085474eb94f7b90bd14524e883d7e941764d9ecd13779a592b1b80018`.
- Installed unknown-time Moshier generation was schema-valid and precision-safe;
  installed exact Woofmap projection produced 17 objects and 61 relationships with
  source identity preserved.
- Uninstalled pyswisseph inside the temporary container; saved mode and packaged
  bounded schema access remained ready.
- First source-suite run found stale editable 0.6.0 distribution metadata. Refreshed
  the external editable install to 0.7.0; final suite passed 214 tests in 17.40
  seconds with only a non-failing pytest-cache permission warning.
- Release decision: no tag, publication, or release credential use in this sprint.
  A separately approved immutable release must bind the final Gate 6 commit.
- Added compact installed qualification evidence and updated both future-integration
  journals. Slice remains uncommitted pending Gate 6 approval.
- Removed the two temporary wheel-build directories, repository `build` and generated
  egg-info trees, and the named qualification container after preserving compact
  hashes and results. No release artifact was copied into the repository.
