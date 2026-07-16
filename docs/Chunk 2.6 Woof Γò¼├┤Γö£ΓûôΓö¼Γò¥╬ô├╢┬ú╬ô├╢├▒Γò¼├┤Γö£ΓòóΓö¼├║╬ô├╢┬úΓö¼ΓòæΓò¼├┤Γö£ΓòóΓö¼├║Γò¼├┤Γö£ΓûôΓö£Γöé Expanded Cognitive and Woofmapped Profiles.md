# Chunk 2.6.woof — Expanded Cognitive and Woofmapped Profiles

## Purpose

Chunk 2.6.woof is a deliberately playful but architecturally serious detour.

It tests whether one canonical Natal graph can support three substantially different target ontologies:

```text
canonical Natal graph
├── orthodox_astrology.v1
├── cognitive_architecture_demo.v0
└── woofmapped_astrology.v0
```

The same generic engine, deterministic IDs, provenance contracts, audit structure, and diagnostics are used for all three.

The pass also extends projection beyond operator and relationship renaming. It explicitly tests:

```text
operator
+ sign-derived mode
+ house-derived domain
+ angle-derived interface
+ aspect-derived relation
```

## Are signs projected?

Yes. In richer projection profiles, signs are operating modes rather than independent subsystems.

Before this pass:

- orthodox projection retained sign and house facts but did not systematically project them into target-domain modes/domains;
- cognitive v0.1 mapped core operators and five major aspects only.

Chunk 2.6.woof is the first reference implementation to attach explicit projected modes and domains to Natal operators.

Because canonical Natal graphs currently represent signs and house placements as facts on source objects rather than as independent sign-membership nodes, mode and domain mappings are retained under the projected object's attributes:

```json
{
  "source_sign": "Scorpio",
  "projected_mode": "deep_search_guarded_transformation_mode",
  "source_house": 8,
  "projected_domain": "shared_risk_deep_integration"
}
```

Explicit canonical house-cusp objects can also project into target-domain objects.

This result should inform the generic projected-graph contract review in Chunk 2.7: modes and domains may deserve formal first-class contracts later, but no engine redesign was required to test them now.

---

# Part I — Cognitive Architecture Demo v0.2

## Status

```text
profile_id: cognitive_architecture_demo.v0
profile_version: 0.2.0
```

This remains:

- experimental;
- non-clinical;
- not empirically validated;
- non-diagnostic;
- an architecture and mapping test.

## Expanded source scope

The profile now supports:

- Sun through Pluto;
- North/South Node concepts where present;
- Part of Fortune;
- Vertex;
- ASC, DSC, IC, and MC;
- all twelve signs as cognitive operating modes;
- all twelve houses as cognitive domains;
- all seven aspect types implemented by the SDK:
  - conjunction;
  - semisextile;
  - sextile;
  - square;
  - trine;
  - quincunx;
  - opposition.

## Operator examples

```text
Sun      → identity_organization
Moon     → emotional_regulation
Mercury  → communication_processing
Venus    → valuation_preference
Mars     → action_selection
Saturn   → constraint_management
ASC      → active_interface
DSC      → counterpart_model
IC       → internal_foundation
MC       → executive_output_direction
```

## Sign modes

Examples:

```text
Aries       → initiation_mode
Virgo       → error_correction_refinement_mode
Libra       → comparative_balancing_mode
Scorpio     → deep_search_guarded_transformation_mode
Aquarius    → system_revision_differentiation_mode
Pisces      → associative_permeable_integration_mode
```

A sign mode modifies the projected operator rather than replacing it.

```text
Mercury in Scorpio
→ communication_processing
   operating in deep_search_guarded_transformation_mode
```

## House domains

Examples:

```text
House 1  → self_interface_response_initiation
House 3  → local_information_exchange
House 6  → maintenance_routine_error_correction
House 8  → shared_risk_deep_integration
House 10 → executive_direction_public_output
House 12 → latent_processing_hidden_state_integration
```

## Relationship expansion

The original five major relationship mappings remain, and the two SDK minor aspects now map as:

```text
quincunx
→ mismatches_and_requires_recalibration
→ recurrent_recalibration

semisextile
→ adjacent_low_bandwidth_coordination
→ low_bandwidth_adjacency
```

Projected relationships preserve endpoint modes and domains, permitting later reasoning inside the projected architecture.

---

# Part II — Woofmapped Astrology v0.1

## Status

```text
profile_id: woofmapped_astrology.v0
profile_version: 0.1.0
context_id: woofmapped.doghouse.general.v0
```

This profile is:

- a playful structural projection;
- not veterinary advice;
- not a behavioral diagnosis;
- not empirically validated.

Its purpose is to stress-test operator, mode, domain, interface, and relationship preservation across a species-oriented target domain.

## Methodological source

The profile is based on the supplied Woofmapping materials:

- Canine Projection Mapping v0.2;
- Canine Projection Mapping v0.3 — Doghouses, Transits, and Synastry;
- Woofmapped Synastry Framework v0.1;
- Woofmapped Transit Framework v0.3;
- Operator Preservation Rules — Woofmapping application.

Only Natal projection is implemented in this pass. Transit, Synastry, pack, and horoscope formats are documented as future extensions.

## Operator preservation

Woofmapping is not ordinary astrology with dog nouns substituted into finished prose.

It preserves the source operator while changing the species-specific medium and life architecture.

Examples:

```text
Mercury
ordinary source role:
interpretation / signaling

Woofmapped:
scent_signal_interpretation
decode cues
interpret scent
predict routine
signal
```

```text
Mars
ordinary source role:
action / assertion / pursuit

Woofmapped:
chase_play_defense_drive
chase
play attack
assert
defend
execute
```

## Woofmapped operators and interfaces

Examples:

```text
Sun      → pack_role_identity
Moon     → comfort_safety_regulation
Mercury  → scent_signal_interpretation
Venus    → bonding_preference
Mars     → chase_play_defense_drive
Jupiter  → adventure_optimism
Saturn   → training_rule_structure
Uranus   → novelty_zoomie_response
Neptune  → atmosphere_dream_permeability
Pluto    → primal_trust_intensity

ASC → behavioral_doorway
DSC → primary_companion_interface
IC  → safe_den_baseline
MC  → visible_pack_function
```

## Sign modes

Examples:

```text
Aries       → immediate_chase_mode
Taurus      → nap_spot_loyalty_mode
Gemini      → information_sniffing_mode
Cancer      → pack_security_focus_mode
Leo         → attention_seeking_display_mode
Scorpio     → obsessive_investigation_mode
Sagittarius → adventure_dog_mode
Aquarius    → pattern_breaking_oddball_mode
Pisces      → emotional_sponge_dream_dog_mode
```

## The superior Doghouse policy

Chunk 2.6.woof uses Doghouses rather than direct-translated human houses.

```text
Doghouse 1  → body, temperament, presence
Doghouse 2  → food, toys, bones, valued resources
Doghouse 3  → smells, barks, posture, cues, local data
Doghouse 4  → den, bed, crate, safe home base
Doghouse 5  → play, zoomies, tricks, chase games
Doghouse 6  → training, routine, care, grooming, health
Doghouse 7  → favorite human / primary one-to-one bond
Doghouse 8  → deep trust, vulnerability, handling tolerance
Doghouse 9  → adventure, territory, trails, new parks
Doghouse 10 → visible pack role and household function
Doghouse 11 → social pack and network
Doghouse 12 → deep instinct, hidden fear, dreams, solitude
```

Every projected object preserves:

```text
source_house
doghouse_number
projected_domain
house_mapping_policy = doghouse
```

## Aspect mappings

```text
conjunction
→ subsystems_run_together
→ inseparable_dog_impulse

opposition
→ drives_face_off
→ bond_freedom_axis_tension

square
→ drive_conflict_requires_outlet
→ behavioral_friction

trine
→ natural_behavioral_channel
→ easy_habit_or_talent

sextile
→ trainable_usable_channel
→ developable_coordination

quincunx
→ awkward_system_recalibration
→ odd_behavior_needing_adjustment

semisextile
→ subtle_adjacent_nudge
→ minor_behavioral_nudge
```

The canonical geometry remains unchanged.

## Example

```text
Mars in Leo, Doghouse 6
→ chase_play_defense_drive
→ attention_seeking_display_mode
→ doghouse_6_training_routine_care
```

A square from that Mars to Venus becomes:

```text
chase_play_defense_drive
→ drive_conflict_requires_outlet
→ bonding_preference
```

The profile records the mapped endpoints, modes, Doghouses, source references, and mapping rules without producing a final handler-facing horoscope.

---

# Part III — Cross-profile proof

The repository example:

```bat
python examples\projection_cross_profile_chunk26.py
```

projects one source graph into:

```text
orthodox
cognitive
woofmapped
```

Acceptance conditions include:

- identical source identity;
- identical source graph hash;
- three distinct target ontologies;
- no canonical mutation;
- no orthodox romance vocabulary leaked into cognitive output;
- no cognitive interaction vocabulary leaked into Woofmapped output;
- sign and house mappings survive relationship projection;
- every SDK aspect type maps in cognitive and Woofmapped profiles;
- deterministic output.

---

# Part IV — Architectural learnings for Chunk 2.7

## Unsupported is not unmapped

A profile that intentionally declines to model harmonics has not failed to map them.

Chunk 2.7 should distinguish:

```text
outside_declared_profile_scope
eligible_but_unmapped
mapped
```

This is more informative than one total `unmapped_source_count`.

## Coverage denominators

Useful coverage should include:

```text
total canonical coverage
declared-scope coverage
eligible object coverage
eligible relationship coverage
supported-endpoint coverage
required-family coverage
```

## Modes and domains

Chunk 2.6.woof proves modes and domains can be represented without changing the engine, but extraction planning should consider whether they deserve explicit contract fields or object categories.

## House mapping policy

Woofmapping demonstrates two plausible policies:

```text
direct translated houses
Doghouses
```

The implementation uses Doghouses. Future profile contracts may represent house policy as a context/profile parameter.

## Playfulness and rigor

A profile can be funny without becoming structurally sloppy.

The Woofmapped vocabulary is playful, but the output remains deterministic, typed, auditable, source-referenced, and operator-preserving.
