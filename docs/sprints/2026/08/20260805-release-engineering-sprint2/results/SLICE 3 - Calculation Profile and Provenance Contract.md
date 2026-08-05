# Slice 3 - Calculation Profile and Provenance Contract

## Outcome

New Natal packages now carry a versioned calculation provenance object that
separates normalized source-input identity, configuration identity, canonical
chart identity, and orchestration-owned artifact bytes. The contract records
implemented calculation choices and provider/data evidence without claiming that
an unqualified Swiss Ephemeris runtime is production-reproducible.

## Contract versions

- Provenance: `agf.calculation_provenance.v1.0.0`
- Calculation profile: `agf.calculation_profile.v1.0.0`
- Input normalization: `agf.normalization_policy.v1.0.0`
- Canonical JSON: `agf.canonical_json.v1.0.0`
- Packaged schema: `calculation_provenance_v1.schema.json`

The Natal dataset schema remains 1.1.0 because provenance is an additive metadata
property and historical packages remain valid. Newly generated 0.6.x Natal
packages always emit it.

## Source-input normalization

The normalized hash envelope contains the normalization-policy version and:

- local birth datetime normalized through `datetime.fromisoformat()`;
- resolved `zoneinfo` key;
- latitude as normalized base-10 text; and
- longitude as normalized base-10 text.

Display name, location label, and `source_chart_id` are excluded. Tests prove a
rename and identity rescope preserve calculation identity while time or coordinate
changes alter the source hash. The baseline golden source hash is
`81fb2c383274d18c48d057009362312274cdb0a72c200425aebbe7e4f07aa0db`.

Live source input is `complete_live_input`. Cached input is either recovered from
the four retained chart fields or explicitly unavailable. No missing historical
basis is synthesized.

## Calculation configuration

The profile records:

- tropical zodiac and house/angle policy;
- Sun through Pluto, both node alternatives, angles, optional Chiron, asteroid,
  and fixed-star settings;
- aspect angles, major/minor set, base orbs, body-sensitive adjustments, and
  declination orb;
- sect, Fortune, Spirit, dignity, antiscia, and harmonic policies;
- datetime/timezone/coordinate normalization;
- invocation options, including optional transit-climate dimensions; and
- provider mode, distribution/library version, flags, and ephemeris-data
  inventory.

The profile is hashed with deterministic UTF-8 JSON using sorted keys, compact
separators, preserved Unicode, and rejection of non-finite numbers. House-system,
aspect-set, and provider-version mutations change the configuration hash.

`calculation_basis_status` prevents cached replay from masquerading as original
calculation provenance. A live calculation reports `complete_live_profile`;
cached legacy material reports `cached_replay_profile_not_original_calculation`.

## Swiss Ephemeris data evidence

The live provider now inventories configured external `*.se1`, `sefstars.txt`,
and `seorbel.txt` resources nonrecursively. It records filename, byte size,
SHA-256, count, and a hash of the sorted inventory, but never records the machine
path.

An empty inventory is reported as `no_external_data_files_detected`. That state
does not prove which internal fallback produced a result. Slice 6 must combine a
closed nonempty inventory, exact provider artifact, and controlled numerical
output evidence before making a live support claim.

Primary ecliptic flags and equatorial-declination flags are recorded separately.
This corrects the risk of documenting `FLG_SWIEPH | FLG_SPEED` while omitting the
additional `FLG_EQUATORIAL` used for declinations.

## Artifact hash boundary

AGF does not emit a self-referential or approximate final artifact hash. The
provenance contract assigns SHA-256 of the exact persisted UTF-8 artifact bytes to
orchestration, after AGF returns the package and before downstream transformation.

This is deliberate: `metadata.created_at` is operational and exact serialized
bytes are chosen by the persistence owner. The API must record that byte hash
beside AGF/SPC artifacts and the generation manifest. AGF supplies stable input
and configuration hashes, not a substitute for archived-byte identity.

## Schema and package integration

`metadata.calculation_provenance` is emitted before semantic-boundary finalization
and survives finalization, serialization, identity handling, and projection
adaptation as package metadata. The Natal schema references the new standalone
schema without making it required for historical packages.

The runtime resource inventory increases from 33 to 34 schemas. Slice 2's retained
33-resource manifest remains valid historical evidence for its exact committed
tree; the next release-candidate manifest must contain 34.

## Evidence

- `calculation-provenance-vectors.json` contains golden hashes and mutation
  sensitivity expectations.
- `calculation-provenance-examples.json` contains a synthetic live-contract
  example and cached-legacy example. The live example is explicitly not evidence
  of live astronomical execution.
- Unit tests validate canonical hashing, exclusions, mutations, cached recovery,
  basis status, schema compliance, provider/library reporting, data inventory,
  and machine-path exclusion.
- The live-Natal boundary test proves provenance is attached while explicit chart
  identity remains separate and absent from provenance hashes/profile content.

## Gate verification

- Focused provenance/identity/resource suite: 40 passed before the final broad
  gate.
- Final full suite: 172 passed.
- Targeted Ruff passed with the repository's pre-existing naive `created_at`
  behavior explicitly excluded; changing timestamp semantics is not part of this
  slice.
- Final schema, JSON, hash-vector, whitespace, full-suite, and diff checks are
  recorded in the log/handoff.

## Deferred

- A production-qualified pyswisseph Python 3.12 artifact and licensing decision.
- Controlled live calculation against the final ephemeris inventory.
- API-side exact artifact-byte hashing and persistence.
- Cross-component compatibility and worker handoff documentation in Slice 4.
- Installed deterministic replay in Slice 5 and release publication in Slice 7.
