# Foundry 0.6.0 Identity and Release Retrospective

AGF 0.6.0 turned a development checkout with implicit identity and source-oriented packaging assumptions into an explicit, installed, reproducible production dependency. The identity and release sprints are the detailed evidence; this retrospective preserves the lessons that remain useful beyond those sprints.

## What surprised us

Explicit identity was both closer and deeper than expected. Saved-package and downstream structures already carried `source_chart_id`, so opening the ordinary live boundary was direct. Complete migration was not direct: identity-derived provenance-family tokens, multiple identity carriers, structural graphs, indexes, registries, and nested exact references all needed synchronized refresh. A graph whose visible endpoints look correct can still retain stale lineage.

Relationship charts could not inherit one generic rule. Synastry is directional and preserves participant order; Composite and Davison describe order-independent relationship entities. Making that distinction explicit prevented display names, calculation geometry, or projection context from becoming accidental relationship identity.

Installed-wheel QA found two real defects that the source tree had tolerated: Windows lacked an IANA timezone database without `tzdata`, and a packaged Natal schema still required a removed nested semantic-graph alias. Packaging was therefore part of contract testing, not clerical release work.

An unauthenticated private GitHub release download returned 404 despite a correct SPC tag and asset name. Authentication, visibility, and asset existence are separate checks. The eventual workflow used temporary encrypted access plus an independent digest check, then removed the credential.

## What was hardest

The hardest design work was keeping identity dimensions separate while still making them useful together. Subject lineage, normalized birth geometry, calculation configuration, sensor instance, exact artifact bytes, and projection context all need stable names and hashes, but none can safely replace another.

Live provenance also required observing what the astronomy library actually returned. Requesting Moshier or pointing at an empty data directory was not enough; returned flags became the evidence that the qualified path really ran.

Most execution friction was environmental rather than architectural: Python was not consistently on `PATH`, test discovery depended on working directory, clean environments exposed missing dependencies, and Windows permissions differed between sandboxed and elevated processes. The durable response is explicit runtimes, outside-checkout installed tests, exact directories, and compact evidence—not assumptions based on one developer shell.

## What was easier than expected

The pure-Python AGF wheel became byte-reproducible with clean `git archive` exports, pinned build tools, and `SOURCE_DATE_EPOCH`; both final builds matched exactly. Choosing the published CPython 3.11 manylinux pyswisseph wheel also avoided an unnecessary native source-build qualification program.

SPC compatibility was stable once tested against its exact released wheel. AGF did not need to embed Woofmapping preparation or reinterpret projection context; preserving canonical source identity and registries was enough for the AGF-to-SPC boundary. The later AstroWoof-wide audit found that this result must not be generalized to the full released tuple: SBE 0.1.0 still requires `source_chart_id == natal:<subject_id>`, a narrower convention than AGF's opaque identity contract. Resolving that composition seam belongs downstream; AGF should not weaken its identity boundary to make the historical authoring convention fit.

## Durable conclusions

- Production identity must be caller-owned, opaque to AGF, conflict-safe, and separate from display metadata.
- Whole-package rescoping is a lineage migration, not a string replacement.
- Relationship identity rules depend on whether participant roles are directional.
- Calculation provenance must record both requested policy and observed runtime behavior.
- Exact artifact hashes and installed-resource manifests are release contracts, not optional bookkeeping.
- Source tests, installed pure-mode tests, controlled live tests, and publication-download tests catch different classes of defects.
- Exact component releases do not prove their unrestricted composition; qualify the complete tuple at every cross-component identity boundary.
- Do not solve hypothetical external-data packaging before a real profile requires it.
- Keep temporary credentials and bulky environments out of durable evidence.

These conclusions are promoted into the [ADRs](../../decisions/README.md), [Release Engineering](../../Release%20Engineering.md), identity, provenance, compatibility, and live-profile reference pages. The sprint logs remain authoritative for chronology and individual defects.
