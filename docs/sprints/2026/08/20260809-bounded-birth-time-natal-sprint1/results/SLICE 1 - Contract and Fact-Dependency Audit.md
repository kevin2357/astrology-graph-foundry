# Slice 1 - Contract and Fact-Dependency Audit

**Status:** Approved 2026-08-10; no production implementation

**Starting boundary:** `7d071d2a17b3bf91fd5244f2adefc64439d9ca24`

## Outcome

The bounded-birth-time feature is confirmed as a new source-contract and capability
boundary, not a filtering option on the exact Natal compiler. The audit identifies
which current facts can become interval assertions, which must be unavailable or
deferred initially, which package families must reject bounded input, and which
contract decisions should bind Slice 2.

## Current exact-time path

`BirthData`, `birth_data_v1`, the main CLI, daily ephemeris CLI, helper tools, Natal,
Synastry, Composite, and Davison live input paths all carry one `birth_local` string.
`build_live_natal_chart` attaches one timezone, converts one instant to UT/Julian
day, and calculates houses before every body. It then attaches house placement to
every body and derives angles, sect, Fortune, Spirit, dignities, antiscia, harmonics,
declinations, and exact aspect rows.

`build_chart_graph` turns each longitude into exact sign/degree fields and generates
additional longitude relationships. The canonical graph schema is permissive about
object properties but the chart semantic schema enumerates current exact object and
relationship types. `TransitableChart` unconditionally advertises longitude-aspect
support and infers timing capabilities from the presence of exact bodies and event
timestamps.

Therefore generating a noon or midpoint chart and deleting visibly unstable rows
would leave exact derived facts, graph objects, relationships, capabilities,
summaries, evidence, and downstream activation paths that were never audited for the
interval.

## Proposed binding input decisions

### Public model

Introduce a tagged `birth_time_basis` rather than adding nullable bounds alongside
the current required exact field:

- `exact`: one local datetime;
- `bounded`: `earliest_local` and `latest_local` under one IANA timezone; and
- `unknown_time`: one known local calendar date with no known time, explicitly
  distinct from caller-supplied bounds and legacy policy-derived noon.

CLI spelling should use `--birth-local-earliest` and
`--birth-local-latest`. The existing `--birth-local` remains the exact-mode
compatibility surface. Mutually exclusive mode carriers fail closed.

### Bound semantics

- Caller-supplied bounded endpoints are inclusive.
- `unknown_time` means every valid civil instant belonging to the named local date;
  its normalized computational range is local midnight inclusive to the next local
  midnight exclusive.
- Reject empty/inverted bounded intervals. A zero-width bounded request must use
  `exact`; it is not silently retyped.
- Initial maximum bounded duration candidate: 48 elapsed UTC hours. This covers
  known-day, DST-short/long-day, and common approximate/cross-midnight cases while
  bounding proof cost. Longer historical uncertainty is deferred pending profiling.
- Preserve supplied mode and bounds separately from normalized UTC evaluation
  bounds so whole-day and caller-bounded semantics never collapse.

The 48-hour maximum is the one policy choice most appropriate for human review at
this gate; it is a conservative implementation limit, not an astronomical law.

### Civil-time responsibility

The reusable AGF boundary must reject invalid IANA zones, malformed local values,
nonexistent boundary wall times, and unresolved ambiguous folds. A caller such as
the AstroWoof API may resolve civil-time eligibility, but AGF must validate the
resolved local/UTC pair rather than trust one silently. Direct CLI use should accept
only unique local endpoints until an explicit fold/offset input is designed.

AGF owns conversion into the normalized calculation interval and records it in
native provenance. Product policy, user acknowledgement, immutable birth versions,
and whether a supplied range is acceptable remain outside AGF.

## Fact-dependency decisions

The machine-readable companion
[`fact-dependency-matrix.json`](fact-dependency-matrix.json) records the complete
initial classification.

### Canonical in bounded v1 when proven invariant

- body identity;
- zodiac sign;
- direct/retrograde state;
- sign-only dignity components; and
- body-to-body aspect type that remains within the selected aspect's allowed orb
  throughout the interval.

Exact longitude and exact orb remain bounded evidence, not canonical scalar values.
An invariant aspect may carry an orb range in uncertainty evidence. Strength and
applying/separating classification are deferred until their interval semantics are
reviewed.

The current dignity record mixes sign-only dignity with sect-dependent triplicity.
It must be split before bounded promotion; copying the whole record when sign is
stable would falsely assert a sect branch.

### Initially unavailable

- houses and house placement;
- ASC, DSC, MC, IC, and Vertex;
- sect;
- Fortune, Spirit, and angle/sect-dependent lots; and
- angle/house aspects.

### Initially deferred

- declination ranges and parallels;
- antiscia and harmonic interval objects;
- fixed-star contacts;
- exact aspect strength/application semantics; and
- non-canonical representative-position views.

Deferred configured features must still be reported as profile-disabled/deferred;
they may not vanish as if AGF never considered them.

## Graph and identity consequences

Current `planet_or_point` objects can technically omit longitude under the permissive
canonical schema, but their accepted semantics and SPC mappings assume exact natal
placements. Reusing that type would be structurally valid and semantically unsafe.
Bounded categorical placements need explicit vocabulary and a graph version that an
exact-only consumer cannot mistake for graph 1.3.0.

Body and invariant-aspect IDs should remain scoped beneath the same
`source_chart_id`; narrowing or correcting bounds changes calculation/provenance and
artifact identity, not automatically chart lineage. Evidence and graph versions
distinguish exact from bounded assertions.

## Package-family compatibility matrix

| Family | Initial bounded policy | Reason |
| --- | --- | --- |
| Natal | Implement bounded v1 | Owning source package |
| SPC projection adapter | New explicit compatibility | SPC currently lists graph 1.3.0 only |
| Transit / Transit Period | Reject initially | Exact target longitude and houses are used |
| Synastry | Reject initially | Exact aspects and house overlays are assumed |
| Composite | Reject initially | Midpoints require exact participant longitudes/houses |
| Davison | Reject initially | Requires exact participant event datetimes |
| Solar/Lunar Return | Reject initially | Solves return to exact natal Sun/Moon longitude |
| Annual Profections | Reject initially | Uses reference event and house cusp/sign |
| Temporal activation | Reject initially | Current activation relations assume exact targets |

“Reject initially” is a capability boundary, not a conclusion that bounded forms of
these techniques are impossible. Later support requires its own semantics.

## Version-impact decision

Exact output remains on the existing Birth Data v1, Natal Dataset 1.1.0, canonical
graph 1.3.0, and current `TransitableChart` semantics. Bounded output receives a
separate `bounded_birth_data_v1`, `bounded_natal_dataset_v1`, bounded canonical graph
contract, and reduced-capability descriptor. This deliberately prevents current SPC
or any other exact-only consumer from accepting a bounded artifact by schema
coincidence.

AGF 0.7.0 remains the package-version candidate because it adds a substantial new
public package family while preserving exact behavior. SPC needs a separate sprint
and compatibility release for the bounded graph; its existing understanding of
exact graph 1.3.0 need not change.

## Required Slice 2 tests

- exact legacy arguments remain accepted;
- exact and bounded carriers conflict rather than silently taking precedence;
- bounded and unknown-day normalization across ordinary, 23-hour, and 25-hour days;
- cross-midnight bounds;
- malformed, inverted, empty, too-long, ambiguous, and nonexistent boundaries;
- supplied versus normalized values survive serialization;
- source hash changes with mode, bounds, timezone, boundary policy, or normalization
  version;
- display name/location label and `source_chart_id` retain their existing hash
  exclusions;
- legacy warned noon is not equal to bounded or unknown-day input; and
- repeated normalization is deterministic.

## Gate evidence

- Clean start at AGF `7d071d2`; API project boundary `143d80d`.
- Source/schema/CLI/provider/graph/package-family audit completed.
- SPC 0.10.0 compatibility declaration inspected read-only.
- Bundled test environment initially lacked pytest and project dependencies. Pytest,
  jsonschema, and local editable SPC 0.10.0/AGF 0.6.0 were installed outside the
  repository.
- Full baseline suite: **181 passed in 6.15 seconds**.
- No production code or schema changed in Slice 1.

## Gate questions for approval

1. Approved with mode spelling changed to `unknown_time`.
2. Approved: inclusive caller bounds, whole-local-day calendar semantics, and
   zero-width input routed through exact mode.
3. Approved: 48 elapsed hours is the bounded-v1 maximum.
4. Approved: conservative initial facts and exact-only package-family rejections.
5. Resolved: existing exact schemas remain unchanged; bounded output receives a
   distinct package/graph family and a later SPC compatibility sprint.
