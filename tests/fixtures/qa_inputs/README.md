# QA fixture inputs

This directory holds the stable, externally generated inputs used by the repository-level QA runners:

- `transit.full.json` — required by streaming-profile QA. Regenerate it from the canonical Natal fixture with the Foundry Transit CLI when its schema changes.
- `transit.standard.json` — required by downstream-integration QA and retained as an established cross-system regression input.
- `natal.full.json` — required by downstream-integration QA.
- `natal.ashley.full.json` — optional second Natal package used to verify cross-chart identity isolation.
- `solar_return.full.json` — optional Solar Return input used by streaming-profile QA when present.

The large JSON packages are intentionally ignored by Git. They are local test inputs rather than source files. Generated QA artifacts and logs belong in `outputs/fixture_outputs/`.
