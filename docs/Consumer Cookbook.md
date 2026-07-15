# Consumer Cookbook

**Status:** Pass 2 companion doc.  
**Purpose:** Concrete examples of how downstream consumers should combine SDK packages.

## 1. Integrated yearly report

Inputs: natal analysis/full; annual profection; solar return; transit analysis over the year; eclipse/lunation over the same period; optional lunar returns.

Assembly logic:

1. Use natal as baseline.
2. Use profection to identify foregrounded subsystem.
3. Use solar return to describe year chart.
4. Use transit analysis for active arcs.
5. Use eclipse/lunation for narrative punctuation.
6. Use convergence to rank themes.

Output target: `yearly_integrated.report_view.json`, final prose report, annual dashboard.

## 2. Integrated monthly report

Inputs: natal; lunar return near target date; transit analysis for month; annual profection/solar return as context; eclipse/lunation windows.

Assembly logic: lunar return gives subjective container; transits give active pressure/weather; annual context explains why this month belongs to a larger chapter; lunations identify peak windows.

## 3. Full relationship report

Inputs: natal A; natal B; synastry analysis; composite; Davison.

Assembly logic: natal A/B set baselines; synastry describes activation/interactions; composite describes midpoint relationship entity; Davison describes relationship-as-event entity; synthesis compares convergence/divergence.

## 4. Professional relationship projection

Inputs: natal A/B; synastry; optional composite/Davison; context object `relationship_type=professional`.

Projection: Mercury -> communication/workflow; Venus -> morale/values alignment; Mars -> initiative/conflict style; Saturn -> responsibility/deadlines; Jupiter -> growth/mentorship; Moon -> emotional climate/regulation.

## 5. Mythos Star Game relationship mechanics

Inputs: player natal packages; pairwise synastry; optional composite/Davison.

Projected outputs: affinity score, conflict pressure, cooperation bonus, communication modifier, rivalry risk, alliance durability, AI behavior weights.

## 6. Human Operating System publication

Inputs: natal analysis; report blueprint; projection context; publisher style.

Architecture:

```text
natal semantic package
↓
report view
↓
Human OS projection
↓
layout engine
↓
PDF/book/web artifact
```

## 7. NCS/MPAS terrain projection

Inputs: natal package; projection mapping to terrain/trails/ecosystem.

Outputs: regions, trails, difficulty, weather systems, vistas, bottlenecks, symbolic GIS-like geometry.

## 8. Research dashboard

Inputs: full packages, analysis packages, logs, future evidence objects.

Use: inspect claims, compare pipelines, audit provenance, test convergence/divergence.
