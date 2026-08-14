# Contributing

Use Python 3.12 and create a local environment with `make setup` or
`.\scripts\dev.ps1 setup`. Before a pull request, run `make ci` (PowerShell:
`.\scripts\dev.ps1 ci`). Use Conventional Commit subjects such as `feat:`, `fix:`, `test:`, `docs:`,
`security:`, or `infra:`.

Changes to model ID, trust boundaries, idempotency, retry policy, schemas, or critical/degraded state
classification require an ADR update. New food-safety vocabulary needs positive, negative, and
prompt-injection tests. Do not commit real order data, addresses, tokens, execution histories, or AWS
account identifiers.

Pull requests should be small enough to review, explain operational/rollback impact, and distinguish
local results from real AWS integration evidence.

