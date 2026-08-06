# Calculation Provenance and Hashing

## Contract status

AGF 0.6.x emits `metadata.calculation_provenance` on newly built Natal packages.
The contract is `agf.calculation_provenance.v1.0.0` and is represented by the
packaged `calculation_provenance_v1.schema.json` resource.

The calculation profile, normalization policy, and canonical JSON policy are
independently versioned:

- `agf.calculation_profile.v1.1.0`
- `agf.normalization_policy.v1.0.0`
- `agf.canonical_json.v1.0.0`

The profile is descriptive provenance for implemented calculation behavior. It
does not turn every low-level option into a supported public override.

## Source-input identity

`source_input.sha256` covers the normalized geometry-affecting birth basis:

- local birth datetime;
- IANA timezone key;
- latitude; and
- longitude.

Coordinates are encoded as normalized base-10 strings before canonical JSON
hashing so numeric representation differences do not create type-only identities.
Local datetime uses `datetime.fromisoformat()` normalization; timezone uses the
resolved `zoneinfo` key. The hashed envelope also contains the normalization-policy
version, so a later change to normalization cannot silently reuse the old identity.

Display name, location label, and `source_chart_id` are explicitly excluded.
They remain important artifact/identity metadata, but none changes astronomical
geometry. Consequently, renaming a subject or changing stable chart identity does
not falsely claim a new calculation basis. Changing time, timezone, or coordinates
changes the input hash.

Live input reports `complete_live_input`. Cached historical input reports
`recovered_from_cached_chart` when all four fields can be recovered, otherwise
`legacy_source_unavailable` with a null hash. AGF does not manufacture certainty
for an old package.

`calculation_basis_status` separately distinguishes a complete live calculation
profile from a cached-replay profile that cannot prove the original astronomy
runtime and configuration. Cached replay provenance describes the current replay
operation; it never upgrades historical calculation assumptions by inference.

## Calculation profile and configuration hash

`calculation_profile` records:

- tropical zodiac policy and house system;
- core bodies, both node alternatives, angles, optional Chiron/asteroid/star
  configuration;
- aspect angles, major/minor inclusion, base orbs, and body-sensitive orb
  adjustments;
- declination orb policy;
- sect, Fortune, Spirit, dignity, antiscia, and harmonic policies;
- datetime, timezone, coordinate, and canonical JSON normalization policies;
- invocation options relevant to Natal calculation or optional transit climate;
  and
- provider mode, distribution/library version, calculation flags, and ephemeris
  data status.

Calculation profile 1.1 adds the requested ephemeris mode. Live provenance
records the requested mode and modes decoded from Swiss Ephemeris return flags.
Explicit `moshier` and `swiss` modes fail on a mismatch. Historical `auto`
behavior may record a fallback and is not the qualified AstroWoof profile.

`configuration_sha256` is SHA-256 over the profile serialized with UTF-8,
sorted object keys, compact separators, Unicode preserved, and non-finite numbers
rejected. A material configuration or provider change changes this hash.

Filesystem ephemeris paths are deliberately excluded: a machine path is neither
semantic identity nor reproducible data provenance. Live runtime provenance
inventories `*.se1`, `sefstars.txt`, and `seorbel.txt` nonrecursively by filename,
size, and SHA-256, then hashes the sorted inventory. It records no absolute path.
An empty inventory is explicit but, by itself, does not prove which calculation
path ran. Returned-flag evidence supplies that proof for profile 1.1. Production
qualification pairs the closed inventory with the requested and observed modes.

## Output artifact hash boundary

AGF does not emit its own final artifact hash. `output_artifact_hash` declares:

- owner: `orchestration`;
- algorithm: SHA-256; and
- boundary: the exact persisted UTF-8 artifact bytes returned by AGF before any
  downstream transformation.

This avoids a self-referential field and avoids pretending that a semantic hash
equals the bytes archived by the API. Packages contain operational `created_at`
metadata, so repeated calculations can have equal input/configuration identity
while their exact artifact-byte hashes differ. The persistence owner records the
byte hash, AGF/SPC/SBE wheel hashes, and generation manifest together.

## Identity separation

These values are not interchangeable:

| Value | Meaning |
|---|---|
| `source_chart_id` | Stable caller-owned canonical chart lineage |
| `source_input.sha256` | Normalized geometry-affecting birth facts |
| `configuration_sha256` | Calculation profile and provider assumptions |
| `sensor_instance_id` | One pipeline observation/technique instance |
| output artifact SHA-256 | Exact persisted bytes, calculated by orchestration |
| projection context | Downstream SPC/application interpretation context |

Cache and idempotency policies may combine these identities, but must not collapse
them into one field.

## Examples and verification

Golden mutation vectors are retained in the release sprint as
`calculation-provenance-vectors.json`. Tests prove descriptive renames preserve
the input/configuration hashes; geometry, house system, aspect inclusion, and
provider-version changes affect the appropriate hash. The emitted object is
validated against the packaged provenance schema.
