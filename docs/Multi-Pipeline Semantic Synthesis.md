# Multi-Pipeline Semantic Synthesis

**Status:** Pass 2 living research/design document.  
**Purpose:** Document the long-term idea that the SDK can integrate evidence from multiple independently constructed semantic models into auditable higher-order interpretations.

## 1. Executive summary

The SDK began as infrastructure for standardized astrology package generation. During development, a stronger architecture emerged:

```text
Astrological model
↓
Semantic graph
↓
Evidence object
↓
Evidence integration
↓
Meta Semantic Graph
↓
Consumer
```

The key shift is from **pipeline as data producer** to **pipeline as evidence sensor**.

A pipeline does not merely emit a file. It observes the same underlying person, relationship, time period, or system from a particular angle. Natal, transit, synastry, composite, Davison, returns, profections, lunations, progressions, and solar arc all ask different questions. Their agreement and disagreement can be meaningful.

## 2. Origin of the idea

The immediate trigger was the Kevin/Bre relationship test suite. The SDK generated synastry, composite, and Davison outputs. Reports written from those outputs found that composite and Davison, despite being mathematically different constructions, dovetailed strongly.

Composite constructs a midpoint entity. Davison casts a real chart for the midpoint in time and space. Synastry compares two real natal charts directly. These are not the same technique, yet they repeatedly pointed toward similar relationship-entity themes: sensitivity, relational calibration, daily-life practice, attraction/activation, emotional permeability, and the need to operationalize the dream through specific behavior.

That observation changed the architectural question.

Instead of asking:

> Which relationship chart is correct?

we can ask:

> What claims remain stable across independently constructed relationship models?

## 3. The full-circle research moment

The larger project originally began from interest in comparing models of mind/personality/thinking: where they agree, where they diverge, and how detailed their descriptions are. Astrology became one rich model family among others.

After implementing enough pipelines, the project returned to its original question from inside astrology itself.

```text
Original question:
How do different semantic models agree/disagree?

Implementation path:
Build astrology semantic packages.

Emergent result:
Multiple astrology pipelines become comparable semantic observers.

Full circle:
The SDK becomes a framework for comparing model outputs.
```

This is not feature creep. It is structural emergence.

## 4. Semantic graph vs Meta Semantic Graph

A semantic graph answers:

> What does this pipeline say?

A Meta Semantic Graph answers:

> What do multiple pipelines collectively say?

Example:

```text
Synastry: communication activation
Composite: relationship entity has analytic/repair language
Davison: relationship grows through partner mirroring and practical calibration
Transits: Mercury/Venus activations
↓
Meta claim: communication/translation/relational calibration is a high-confidence theme
```

The Meta Semantic Graph should not erase differences. It should preserve supporting evidence, conflicting evidence, source pipeline, source object IDs, confidence/weight, scope, and interpretation notes.

## 5. Evidence object

A future evidence object might look like:

```json
{
  "concept_id": "relationship.communication_calibration",
  "claim": "The relationship depends heavily on explicit communication and practical relational repair.",
  "scope": "relationship",
  "supporting_evidence": [
    {"pipeline": "synastry", "ref": "synastry.theme.communication_activation", "weight": 0.82},
    {"pipeline": "composite", "ref": "composite.virgo_6th_house_cluster", "weight": 0.78},
    {"pipeline": "davison", "ref": "davison.virgo_moon_7th_house", "weight": 0.80}
  ],
  "conflicting_evidence": [],
  "confidence": 0.88
}
```

This is not final prose. It is structured interpretation with provenance.

## 6. Convergence

Convergence occurs when independent pipelines point toward the same concept.

### 6.1 Relationship convergence

The Kevin/Bre relationship reports demonstrate the pattern:

- Synastry describes high activation and axis-level relationship contact.
- Composite describes a delicate, service-oriented, practical relational entity.
- Davison describes a relationship that enters through Pisces/Neptune atmosphere but stabilizes through Virgo/Saturn/6th-7th-house behavioral evidence.

The exact placements differ, but the themes converge: relational intensity, calibration, practical repair, communication, tenderness, and behavioral proof.

### 6.2 Timing convergence

The integrated yearly report demonstrates timing convergence:

- Annual profection foregrounds the 9th house.
- Solar return luminaries emphasize the 9th house.
- Transits pressure Mercury/Venus/Sun themes.
- Lunations add narrative punctuation.

The report can therefore move from "many events" to "a year of worldview/language/relation reframing under pressure."

### 6.3 Monthly convergence

The integrated monthly report demonstrates scale layering:

- Lunar return describes the subjective container.
- Transits describe active arcs.
- Annual context explains why the month matters inside a larger chapter.

This is not merely stacking files. It is assigning each model a role.

## 7. Divergence

Divergence is not failure.

Example:

```text
Composite: gentle/practical relational entity
Synastry: hot, activating, friction-heavy mechanics
Davison: magical entrance, practical stabilization
```

These can all be true at different layers.

A synthesis layer must preserve divergence rather than averaging it away.

## 8. Pipeline roles

| Pipeline | Evidence role |
|---|---|
| Natal | baseline identity / source graph |
| Transit | active weather / activation |
| Synastry | interaction mechanics |
| Composite | midpoint relationship entity |
| Davison | event-style relationship entity |
| Solar Return | annual chapter chart |
| Annual Profections | yearly foregrounded subsystem |
| Lunar Return | monthly emotional container |
| Eclipse/Lunation | timing punctuation / activation windows |
| Progressions | symbolic developmental evolution |
| Solar Arc | long-term directional pressure |

The synthesis layer should not weight these identically in every report. It should weight them according to report type and claim scope.

## 9. Relationship Synthesis package

A future `relationship-synthesis` pipeline could consume natal A/B, synastry, composite, Davison, relevant transits, and later returns/progressions/lunations.

Output:

- consensus themes;
- divergence notes;
- evidence graph;
- confidence weighting;
- report materials;
- story materials;
- timeline materials;
- domain-neutral relationship trait vectors.

## 10. Timing Synthesis package

A future timing synthesis package could consume natal, annual profection, solar return, lunar return(s), transit range, eclipse/lunation range, future progressions, and solar arc.

Output:

- annual chapter;
- monthly chapters;
- key windows;
- repeated themes;
- active contradictions;
- confidence by time scale;
- timeline-ready report materials.

## 11. Report View as synthesis boundary

`report_view.json` is a likely boundary between synthesis and final report.

Synthesis should produce structured report materials: headline claims, evidence bundles, contradictions, section candidates, timeline highlights, source refs, confidence notes, and projection hints.

## 12. Compatibility with non-astrological models

The long-term abstraction should not depend on astrology.

If a future model emits semantic graphs and evidence objects, the integration layer can compare it.

Potential future sources include Big Five, attachment style, narrative analysis, OMTA outputs, projected chart generation outputs, biographical evidence, game behavior logs, and archaeology notes.

## 13. Risks

- False convergence: compiler maps too many things to the same theme.
- Overconfidence: multiple weak signals masquerade as one strong signal.
- Premature flattening: disagreement is averaged away.
- Domain leakage: romance assumptions leak into professional/family/game contexts.

## 14. Near-term implementation path

1. Standardize evidence claim shapes in existing packages.
2. Add report-view prototypes for yearly and relationship reports.
3. Define stable concept IDs for recurring themes.
4. Expand long-window eclipse/lunation support.
5. Add relationship and timing blueprint examples.
6. Build a toy Relationship Synthesis compiler.
7. Build a toy Timing Synthesis compiler.
8. Compare outputs against hand-written reports.
9. Refine confidence and weighting.
10. Only then consider a general Meta Semantic Graph package.

## 15. Working thesis

The SDK's most important long-term role may be integrating evidence from multiple independently constructed semantic models into a coherent, auditable, provenance-preserving Meta Semantic Graph.

That thesis is not proven. But the current generated reports show that even informal/manual synthesis already produces richer, more powerful interpretations than isolated package reads. The architecture is worth preserving and exploring deliberately.
