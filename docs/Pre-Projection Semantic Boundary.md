# Pre-Projection Semantic Boundary

**Status:** Chunk 1 architecture and migration document.  
**Scope:** Define what the SDK may conclude before projection, what belongs inside an explicit projection profile, and how the current package format dual-writes those layers for one inspection cycle.

## 1. Executive summary

The SDK now distinguishes three layers that were previously mixed together:

```text
calculated astrology facts
        ↓
canonical_astrology_graph
        ↓
structural_evidence_graph
        ↓
projection_views
        └── orthodox_astrology.v1
```

The first two layers are deliberately pre-projection.

The third layer is explicit interpretation.

This boundary exists because semantic reasoning changes when the destination domain changes. A Mars–Venus square projected into cognitive architecture is not merely ordinary astrology prose with nouns replaced. If Mars maps to an execution mechanism and Venus maps to a valuation mechanism, the interaction must be reasoned about between those mapped primitives:

```text
execution mechanism
square
valuation mechanism
```

The projected result may be:

> action selection and value evaluation interfere with one another.

That claim is not safely derivable by first writing a conventional romance/personality interpretation and translating it afterward.

At the same time, projection cannot begin from raw longitude tables alone. Every projection needs a shared, auditable source substrate containing object identity, aspect geometry, derivation lineage, source operators, timing relationships, and provenance.

The new boundary therefore follows this rule:

> **Project before destination-domain interpretation, but after canonical astrology compilation and conservative structural aggregation.**

## 2. Why `orthodox_astrology` is an explicit projection

Conventional natal, relationship, and timing interpretation is now represented as:

```text
orthodox_astrology.v1
```

The term `orthodox` is used here to mean the familiar astrology-domain interpretive profile: conventional associations among planets, signs, houses, aspects, relationship themes, timing themes, and report vocabulary.

It is not implemented as a literal no-op.

It preserves the source ontology while adding:

- orthodox theme grouping;
- orthodox salience policy;
- conventional relationship/personality/timing language;
- preliminary report claim candidates;
- report-oriented section hints.

The source chart may look unchanged at a glance, but the interpretive layer is still a projection because it selects and organizes meaning according to one domain's conventions.

## 3. Canonical astrology graph

The `canonical_astrology_graph` is the shared pre-projection source graph.

It may contain:

- exact chart facts;
- planets, points, angles, houses, lots, antiscia, harmonics, and other source objects;
- source-domain operator primitives;
- aspect and relationship topology;
- stable IDs;
- source ownership;
- evidence tier;
- derivation family;
- independence group;
- projection-neutral structural strength;
- provenance and sensor identity.

It excludes:

- `romance_affection`;
- `emotional_safety`;
- `home_family`;
- `partnership_mirroring`;
- orthodox report claims;
- report section planning;
- projection-specific confidence;
- projection-specific relevance policy.

Those exclusions do not imply that the concepts are invalid. They imply that they are not universal source facts.

## 4. Structural evidence graph

The `structural_evidence_graph` performs only conservative aggregation before projection.

Allowed outputs include:

- evidence-tier counts;
- direct-versus-derived ratios;
- repeated source operator families;
- temporal activation groups;
- sensor identity;
- independence-group counts;
- structural strength;
- repeated target-family activation;
- source-level convergence and overlap.

An allowed pre-projection statement might be:

> Venus-family targets are repeatedly activated by three distinct transit families across the same time window.

A deferred projected statement might be:

> the relationship's affection contract is being renegotiated.

The first describes source structure. The second assigns destination-domain meaning.

## 5. Evidence lineage

Every canonical object and relationship now receives `evidence_metadata`.

Example:

```json
{
  "evidence_tier": "harmonic",
  "derivation_type": "derived",
  "derivation_family": "harmonic_derivation",
  "owner_object_ref": "natal:Venus",
  "source_sensor_id": "natal:kevin",
  "independence_group": "natal:kevin:object:natal:Venus"
}
```

This supports later synthesis rules that distinguish:

- direct chart objects from derived objects;
- one transit arc from many repeated daily observations;
- one source object from many harmonic/antiscia descendants;
- one sensor from multiple correlated records inside that sensor.

Without these groupings, a later reasoning engine could mistake correlated volume for independent confirmation.

## 6. Structural strength versus interpretive relevance

The SDK previously used `relevance_score` for ranking many observations. That score contains orthodox astrology assumptions, such as higher importance for luminaries, angles, personal planets, major aspects, and outer-planet transits.

Chunk 1 preserves that score under dual-write as:

```text
relevance_score
orthodox_astrology_relevance_score
```

It also adds:

```text
structural_strength_score
```

`structural_strength_score` uses only projection-neutral considerations available in the current package:

- exactness/orb;
- major versus minor aspect class;
- duration where relevant;
- direct versus derived status.

It does not claim to be the final universal importance score. It is a neutral baseline that later projection profiles may combine with their own salience policies.

## 7. Theme tags and claim candidates

Legacy `theme_tags`, `theme_metrics`, `evidence_graph`, and `report_materials` remain in place for one generated-output review cycle.

They are now explicitly dual-written as orthodox material:

```text
theme_tags
→ orthodox_astrology_theme_tags

relevance_score
→ orthodox_astrology_relevance_score

evidence_graph
→ projection_views["orthodox_astrology.v1"].claim_candidates

report_materials
→ projection_views["orthodox_astrology.v1"]
   .consumer_views["orthodox_astrology_report_v1"]
```

Legacy claim `confidence` is not carried into the new view as calibrated epistemic confidence. It becomes:

```text
legacy_confidence
weighted_support_score
```

with a note that the score represented theme density/relevance rather than a fully reasoned, independence-aware claim confidence.

## 8. Dual-write migration policy

Chunk 1 intentionally writes both old and new fields.

This is not for external backwards compatibility. No downstream consumer is currently considered stable enough to constrain the architecture.

The dual-write exists for inspection:

1. regenerate the full package fixture set;
2. verify that calculations and familiar orthodox outputs are unchanged;
3. inspect canonical graphs for projection readiness;
4. inspect evidence tiers and independence grouping;
5. compare package sizes;
6. identify fields that were incorrectly classified;
7. remove deprecated legacy duplication in a later chunk.

Every package includes:

```json
{
  "semantic_boundary": {
    "canonical_layer": "canonical_astrology_graph",
    "structural_layer": "structural_evidence_graph",
    "default_projection_view": "projection_views.orthodox_astrology.v1",
    "legacy_fields_dual_written": true,
    "legacy_removal_status": "pending_generated_output_review"
  }
}
```

## 9. Projection order

The long-term reasoning path is:

```text
1. astronomical calculation
2. canonical astrology source graph
3. conservative structural aggregation
4. primitive projection
5. projected single-source reasoning
6. projected multi-source synthesis
7. claims
8. concept units
9. narrative units
10. report/application planning
11. publishing
```

Projection is not categorically “before everything” or “after everything.”

What happens before projection is intentionally limited to source preservation and structural aggregation.

What happens after projection includes the meaning-bearing reasoning that depends on the destination ontology.

## 10. Risks of projecting first without a canonical layer

A projection-first architecture becomes unsafe if it begins directly from raw ephemeris data.

It can:

- lose shared source identity;
- discard polyvalent operator meaning too early;
- make projection quality the single bottleneck;
- create circular reasoning around the requested output;
- prevent cross-projection audit;
- make separate projected graphs incommensurable;
- force every downstream project to rebuild aspect and provenance logic.

The canonical graph prevents those failures.

## 11. Risks of interpreting before projection

A full orthodox interpretation before projection can:

- import romance/personality assumptions into cognitive, game, park, or workplace domains;
- preserve source-domain causal narratives that do not exist in the destination;
- encourage unreliable prose-level “translation” by an LLM;
- make operational Python/API implementations depend on conversational context that is not available at runtime;
- produce operator drift.

The explicit orthodox projection prevents familiar astrology from masquerading as universal meaning.

## 12. Chunk 1 implementation map

New code:

```text
common/semantic_layers.py
```

New schemas:

```text
canonical_astrology_graph_v1.schema.json
structural_evidence_graph_v1.schema.json
orthodox_astrology_projection_view_v1.schema.json
evidence_provenance_v1.schema.json
semantic_boundary_bundle_v1.schema.json
```

Updated output families include:

- Natal;
- Composite;
- Davison;
- Synastry;
- Transit;
- Solar Return;
- Lunar Return;
- Eclipse/Lunation;
- Annual Profections.

Analysis and streaming views receive compact boundary summaries and the namespaced orthodox projection view.

## 13. What Chunk 1 does not do

Chunk 1 does not implement:

- generic projection-profile execution;
- cognitive or game projection;
- projected reasoning;
- claim graphs;
- concept units;
- narrative units;
- report-provider compilation;
- calibrated claim confidence;
- cross-pipeline synthesis.

Those are later chunks.

## 14. Success criteria for generated-output review

The next full output batch should demonstrate:

1. no astronomical calculation drift;
2. no semantic loss in legacy orthodox fields;
3. canonical graphs contain no orthodox theme tags;
4. source operator primitives remain available;
5. direct/derived evidence is identifiable;
6. stable independence groups are present;
7. structural strength and orthodox relevance are distinct;
8. legacy claim confidence is clearly demoted in the namespaced view;
9. compact views expose boundary summaries;
10. schemas validate the new layers.

## 15. Inspection utility

After regenerating package fixtures, run:

```bat
python scripts\inspect_semantic_boundary.py scripts\outputs
```

The utility reports:

- which packages expose the new boundary;
- canonical object/relationship counts;
- accidental orthodox theme leakage into canonical graphs;
- missing evidence-provenance metadata;
- missing structural-strength values;
- independence-group counts;
- orthodox theme/claim-candidate counts;
- file sizes during the temporary dual-write cycle.

## 16. Chunk 1.1 evidence-lineage corrections

The first generated-output inspection cycle demonstrated that the high-level boundary was correct but that evidence lineage needed more precise treatment.

### 16.1 Relationship tier inheritance

A directly calculated aspect is not automatically core evidence when one or both endpoints are derived objects.

Chunk 1.1 therefore distinguishes:

```text
direct relation
direct relation between derived objects
derived relation
supplemental relation
```

For example:

```text
Mars harmonic-5 square Venus
```

is still a directly measured square, but its evidence lineage is harmonic because one endpoint is a harmonic projection.

Canonical relationship metadata now records:

- endpoint evidence tiers;
- source and target root-owner references;
- evidence tier inherited from the most-derived endpoint/relation;
- `direct_relation_between_derived_objects` where appropriate.

### 16.2 Record independence versus evidence-family independence

Chunk 1 used one `independence_group` field. Generated outputs showed that this was too coarse.

Chunk 1.1 now records:

```text
record_independence_group
evidence_family_group
independence_group
```

`record_independence_group` identifies one serialized observation.

`evidence_family_group` collapses related observations to root owners and relation family for anti-double-counting.

The compatibility `independence_group` now aliases the family grouping.

This lets a future synthesis engine distinguish:

- two genuinely separate records;
- two records derived from the same source family;
- two independent sensors.

### 16.3 Synastry registry resolution

Compact Synastry packages store operator semantics in registries.

The canonical Synastry graph now:

- namespaces person A and person B object IDs;
- resolves `operator_key` through the operator registry;
- preserves source operator hints;
- preserves derived-object owner lineage;
- excludes orthodox theme-registry values from the canonical graph;
- maps house overlays to explicit target-house nodes.

This restores projection-ready semantics without reintroducing orthodox interpretation.

### 16.4 Nested Lunar Return graphs

The range-level Lunar Return canonical graph remains an event/index graph.

Each nested return chart now also receives a canonical source graph under:

```text
canonical_astrology_graph
  .nested_canonical_graph_registry
```

This preserves both useful levels:

- sequence/event structure;
- chart-level structure for each monthly return.

### 16.5 Package-specific orthodox adapters

The orthodox view now recognizes package-specific metric sources where the mapping is direct.

For Synastry:

```text
relationship_metrics
→ projection_views["orthodox_astrology.v1"].theme_metrics
```

The view records `metric_source_field` so consumers can audit the adapter.

### 16.6 Inspector semantics

The inspection utility now distinguishes:

```text
full
summary
absent
```

canonical materialization.

Compact analysis and streaming views are no longer reported as zero-object full graphs. Their summary counts are used instead, and validation booleans are separated for materialized graphs and compact views.

### 16.7 Versioning

Chunk 1.1 uses:

```text
canonical_astrology_graph 1.1.0
structural_evidence_graph 1.1.0
semantic_boundary_version chunk1.1.v1
```

The version change reflects corrected lineage semantics, not astronomical calculation changes.

## 17. Chunk 1.2 semantic sensor identity

Chunk 1.2 separates chart identity from observation identity.

```text
source_chart_id
source_chart_ids
sensor_instance_id
```

`source_chart_id` identifies the chart being observed. `sensor_instance_id` identifies one concrete pipeline observation of that chart, including technique and time window where applicable.

Examples:

```text
natal:kevin
transit:natal:kevin:2026-01-01:2027-07-01
solar_return:natal:kevin:2026:denver_colorado:america_denver:39.7392:-104.9903
synastry:natal:kevin:natal:bre
```

Evidence rows now carry both sensor-instance groups and `source_chart_family_group`, allowing synthesis to avoid collisions between people while still recognizing evidence derived from the same chart across multiple techniques.

The inspector recursively audits nested canonical graphs, verifies identity fields, reports sensor collisions, and preserves `metric_source_field` in compact projection summaries.

## 18. Chunk 1.3 synthetic-graph identity completion

Chunk 1.3 completes source-chart identity propagation for synthetic canonical graphs. Synastry, annual profections, eclipse/lunation packages, and the top-level Lunar Return sequence graph now write the package's `source_chart_ids` and real `source_chart_family_group` values onto every canonical object and relationship.

The legacy internal Transit analysis type `transit_period_dataset` is normalized to the same public sensor identity as `transit_range_dataset`:

```text
transit:<source-chart-id>:<start-date>:<end-date>
```

Canonical and structural graph versions are now `1.3.0`; package boundary metadata is `chunk1.3.v1`.

## 18. Chunk 1.4 final materialization policy

Chunk 1.4 ends the temporary dual-write inspection cycle.

Full packages now serialize:

```text
pipeline-specific calculated data
canonical_astrology_graph
structural_evidence_graph
projection_views
semantic_boundary
```

They no longer serialize redundant top-level aliases for:

```text
semantic_graph
theme_metrics
relationship_metrics
evidence_graph
report_materials
```

Orthodox interpretation material now lives only under:

```text
projection_views["orthodox_astrology.v1"]
```

The canonical graph is the sole serialized source-graph layer. Analysis views keep compact canonical/structural summaries plus selected orthodox projection material. Streaming views retain registries, references, and projection summaries without full graph or report duplication.

Materialization policies are named:

```text
full_canonical_projection_v1
analysis_projection_summary_v1
streaming_registry_summary_v1
```

This change is intentionally not backward-compatible. No stable downstream consumer was allowed to constrain the pre-projection boundary during the inspection phase.

## 18. Chunk 1.5 materialization corrections

Chunk 1.5 closes two seams found in the first post-dual-write fixture set.

Solar Return now promotes the already-compiled return-chart canonical graph before nested legacy graph removal. A full Solar Return package therefore retains:

```text
canonical_astrology_graph
structural_evidence_graph
projection_views
return_chart calculated facts
```

Canonical rows remain projection-neutral. Report-facing Natal, Transit, and Synastry views now use a contained `orthodox_row_annotation` adapter to reconstruct orthodox theme annotations without mutating or contaminating canonical graphs.

Analysis views use:

```text
canonical summary
structural summary
projection summaries
orthodox_projection_extract
```

and no longer duplicate the complete projection view.

The inspector now treats theme metrics and report materials inside explicit projection namespaces as valid modern material rather than legacy aliases.
