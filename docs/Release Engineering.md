# Release Engineering

This runbook captures the reusable controls proven by the AGF 0.6.0 release. Sprint logs retain command-by-command history; this page states the durable release discipline.

## Immutable release boundary

AGF publishes a wheel, `release-manifest.json`, and `SHA256SUMS.txt` from an annotated tag at the exact qualified source commit. AGF 0.6.0 intentionally publishes no sdist because only the wheel boundary was qualified.

Build twice from independent clean exports with pinned build tooling and one controlled `SOURCE_DATE_EPOCH`. Compare bytes, size, and SHA-256. A version match is not artifact identity: production consumers pin the exact wheel digest.

Post-publication reports may be committed after the tag. They record what happened without moving the immutable source commit that produced the wheel.

## Qualification layers

Source-tree tests are necessary but insufficient. Every release should separately prove:

1. packaged metadata and resource completeness;
2. installation outside the checkout;
3. both console entry points and runtime version alignment;
4. saved-package behavior without optional live dependencies;
5. AGF operation with SPC absent, followed by a separate exact-wheel AGF-to-SPC
   serialized-wire compatibility proof when the release claims that integration;
6. controlled live behavior for each claimed provider/platform/data profile;
7. repeated semantic fixture behavior under the documented timestamp boundary; and
8. fresh download, checksum verification, reinstall, and smoke after publication.

AGF 0.6.0's wheel-only pass found defects that source execution had hidden: Windows needed a declared `tzdata` dependency, and the Natal schema still required a removed nested `natal.semantic_graph` alias. Treat findings at this stage as successful QA, fix them with regressions, and restart from a clean environment.

## Independent downstream compatibility assets

GitHub returns HTTP 404 for unauthenticated release-asset requests to a private
repository even when the tag and filename are correct. Do not diagnose that
response as a missing artifact until repository visibility and authentication are
checked.

SPC is not an AGF package dependency as of the 0.8.0 candidate. A cross-system
qualification may still download an exact private SPC wheel, independently verify
its SHA-256, and install it beside AGF in a disposable integration environment.
Any workflow credential for that download is an integration-test secret, not an
AGF runtime credential. Provision it only for an approved run, never print it, and
delete it after compact evidence is retained.

## Live calculation and external data

Dependency availability is not provider qualification. Record requested and observed ephemeris modes, wrapper/library identity, platform/ABI, calculation flags, and external-data inventory. Do not choose or bundle external ephemeris files until a profile needs them; adding files later is a separately versioned and qualified calculation profile.

The Swiss Ephemeris licensing activation decision is project-owned and distinct from technical release success.

## Evidence and cleanup

Retain compact JSON summaries, hashes, manifest identities, run/release URLs, tag object and commit IDs, and human-readable slice results. Do not retain virtual environments, expanded source exports, duplicate wheels, caches, generated charts, or provider data in sprint documentation.

The latest published baseline and verification evidence are linked from
[release 0.7.0](releases/0.7.0.md); [release 0.6.0](releases/0.6.0.md) preserves the
previous identity/release baseline.
