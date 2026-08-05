# Slice 2 - Installable Package Boundary

## Outcome

AGF now has one version source, installed-safe schema access, a deterministic
runtime resource manifest, stable version reporting on both console scripts, and
concise optional-live-dependency failures. A clean wheel-only environment outside
the source checkout proved package metadata, resources, both entry points, doctor,
SPC compatibility, and operation without Swiss Ephemeris.

## Package boundary changes

### Version and build metadata

- Moved the sole version literal to `astrology_graph_foundry._version`.
- Changed project metadata to derive its version from that module through
  setuptools dynamic metadata.
- Pinned the build backend to `setuptools==83.0.0` and `wheel==0.47.0`; the
  separately invoked frontend remains `build==1.5.0` for release qualification.
- Added explicit MIT SPDX metadata, license-file declaration, author, repository
  URL, and Python 3.10-3.12 classifiers.
- Bounded library compatibility to `semantic-projection-core>=0.10.0,<0.11`.
  Production still pins the exact 0.10.0 wheel/hash.
- Bounded the optional live extra to `pyswisseph>=2.10,<2.11`. The production
  handoff will additionally pin one exact qualified artifact.

### Installed resources

`astrology_graph_foundry.resources` now exposes:

- `schema_names()`;
- `read_schema_bytes(name)`;
- `read_schema(name)`; and
- `build_runtime_package_manifest()`.

These APIs use `importlib.resources` and never assume `src/` or a checkout path.
Unknown schema names fail closed. The manifest deterministically sorts all 33
packaged JSON Schemas and records path, byte size, SHA-256, schema ID, title, and
any statically declared schema/graph/contract/interface/pipeline versions.

The installed manifest captured at the gate is retained as
`runtime-package-manifest.json`. It contains no generation timestamp or machine
path, so identical wheel resources yield identical manifest content.

### CLI behavior

Both installed console scripts now support stable version output:

```text
astro-package 0.6.0
generate-daily-ephemeris 0.6.0
```

`astro-package runtime-manifest` prints the resource manifest or writes it with
`--out`. Console wrappers turn a missing optional live dependency into a concise
`ERROR: ... requires pyswisseph` exit instead of exposing an implementation
traceback. Required SPC import failures remain dependency-installation failures,
not optional-mode behavior.

## Installed qualification

The final smoke performed the following from
`C:\tmp\agf-sprint2-slice2-final`, outside the repository:

1. built the candidate wheel using the pinned backend;
2. re-downloaded exact SPC 0.10.0;
3. created a clean CPython 3.12 virtual environment;
4. installed SPC and its declared dependency closure;
5. installed AGF non-editably from the wheel;
6. ran both `--version` and `--help` surfaces;
7. ran `doctor --json` and `runtime-manifest`;
8. asserted AGF and SPC imported from the temporary `site-packages` tree;
9. verified AGF runtime/distribution 0.6.0 and SPC runtime/distribution 0.10.0;
10. verified `jsonschema==4.26.0`, no `swisseph`, and `pip check` success;
11. exercised both live entry paths and confirmed concise expected failure; and
12. removed the environment and both wheels.

The nonrelease audit wheel was
`astrology_graph_foundry-0.6.0-py3-none-any.whl`, SHA-256
`87f8df63ce0ff6ce1f35830c846a36e5f8c32a6e51984573fc5123b94a342de6`.
This hash is evidence for this exact uncommitted Slice 2 tree only and must not be
used as the final release pin.

## QA finding

The first clean smoke installed both top-level wheels with `--no-deps`. SPC then
failed to import because `jsonschema` was absent. Inspection confirmed SPC 0.10.0
correctly declares `jsonschema>=4,<5`; this was a qualification-harness defect,
not an SPC packaging defect. The final smoke installed SPC's declared closure and
passed. This proves a production lock must cover transitive runtime dependencies,
not merely AGF and SPC top-level wheels.

## Gate evidence

- Focused resource/version/CLI tests: 8 passed.
- Full AGF suite: 164 passed.
- Targeted Ruff: passed.
- Clean non-editable installed smoke: passed.
- Both installed CLIs: version/help passed.
- Doctor: AGF 0.6.0/0.6.0, SPC 0.10.0/0.10.0, Swiss unavailable as intended.
- Runtime resource manifest: 33 resources, all read from installed package data.
- Missing-live failure: both console paths exited nonzero with concise provider
  guidance.
- `pip check`: no broken requirements.
- Temporary environments, wheels, and downloads removed.
- Machine-readable evidence: `installed-smoke.json` and
  `runtime-package-manifest.json`.

## Deferred

- Calculation-profile and provenance hashing belong to Slice 3.
- Complete compatibility and API handoff documentation belongs to Slice 4.
- Meaningful deterministic fixture replay across two installed environments
  belongs to Slice 5.
- Live provider installation and ephemeris data qualification remain Slice 6 and
  retain the Python 3.12 artifact/licensing gates from Slice 1.
- The recorded wheel is not reproducibility or publication evidence; Slice 7
  creates the release candidate from a clean committed export.
