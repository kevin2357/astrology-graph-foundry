# Slice 5 - Downstream and Package-Family Compatibility

**Status:** Gate-ready for review; uncommitted

**Starting boundary:** `930a3cc`

## Outcome

AGF now fails clearly whenever the bounded Natal family is passed to a consumer that
requires exact chart geometry. Exact AGF-to-SPC projection remains qualified and
unchanged. Bounded projection remains a deliberate future SPC contract rather than
an accidental attempt to feed graph version 1.0.0 through mappings designed for
canonical graph 1.3.0.

## Implemented boundary

`BoundedNatalCompatibilityError` and one package classifier now protect:

- AGF's static SPC projection adapter;
- `TransitableChart`, covering transit, transit-period, solar return, lunar return,
  eclipse/lunation target activation, and annual profections;
- Synastry and Composite pair loading; and
- Davison participant loading.

The guard checks both package `analysis_type` and canonical `graph_type`, preventing
metadata relabeling from bypassing the capability boundary. Saved and reloaded
packages reject identically. Errors explain that bounded artifacts lack exact
longitudes, houses, angles, and exact `TransitableChart` capabilities and direct the
caller toward an exact package or a future bounded-compatible consumer.

## SPC reconciliation

SPC 0.10.0 declares only static canonical graph version 1.3.0. Its bundled Woofmap
profile declares current Natal and Synastry source types, but its source mappings
expect exact canonical object/relationship vocabulary. AGF therefore rejects the
bounded family before constructing an SPC request. This produces a clearer boundary
than allowing SPC to report only an unsupported graph-version error.

A later SPC sprint must review `bounded_natal_body`,
`BOUNDED_INVARIANT_ASPECT`, uncertainty evidence, reduced capabilities, and
projection output semantics. It must issue a distinct compatibility declaration;
AGF does not reinterpret the bounded source into current exact vocabulary.

## SBE audit

SBE's AstroWoof authoring path consumes projected artifacts and records their
`source_graph_ref` graph type/version/hash. It does not currently consume AGF's
canonical package directly. Consequently SBE is not eligible for bounded input until
SPC defines and emits a bounded projection contract. This is a downstream design
obligation, not a missing AGF adapter.

## Exact installed proof

The existing qualified `astrowoof-domain-worker:acceptance` image contains Python
3.11.15, AGF 0.6.0, and SPC 0.10.0. Its installed runtime smoke and AGF doctor passed.
An installed live Moshier Natal chart then projected through
`woofmapped_astrology.v0` 0.1.0 with:

- canonical source graph 1.3.0;
- 17 projected objects and 61 projected relationships;
- 100% eligible object and relationship coverage; and
- `gate:exact` source identity preserved.

The first inspection expected an obsolete `projected_graph` wrapper. SPC 0.10.0
returns the projected graph at the result root; reading the actual contract closed
the check without implementation change.

## Gate evidence

- Focused compatibility and projection regressions: **16 passed in 0.40 seconds**.
- Full AGF suite: **214 passed in 17.33 seconds**.
- Exact installed SPC runtime manifest:
  `74ba2450c20e4b8c636ba2ffcb0a8b6db8ae3e0964f552cfdfbf78bde1145afd`.
- Compact evidence:
  [`cross-repository-compatibility.json`](cross-repository-compatibility.json).

## Gate assessment

The exact AGF-to-SPC boundary remains healthy, while every currently unsupported
bounded route is explicit and testable. No SPC, SBE, API, or product code changed.
Slice 6 must convert these facts into migration and API handoff documentation and
perform final installed qualification/version review.
