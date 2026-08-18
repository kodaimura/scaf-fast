# Repository Instructions

## Project Context

- This repository is a FastAPI backend scaffold.
- Read `README.md` and the `Makefile` before changing setup or development workflows.
- Preserve the existing project structure and naming unless the task requires an architectural change.

## Working Agreements

- Keep changes focused and preserve unrelated work.
- Do not commit secrets, local environment files, or generated runtime data.
- Add or update tests when behavior changes.
- Add project-specific architecture and coding rules here when they are established.

## Verification

- Run `make check` for lint and unit tests.
- Run `make test_e2e` when API behavior or database integration changes.
- Run `make build_prod` when production dependencies or container configuration changes.

## Operations

- Before changing production configuration, deployment behavior, database migration procedures, health checks, or rollback behavior, read `docs/RUNBOOK.md`.
- Read `docs/RUNBOOK.md` before assisting with a deployment, release, rollback, recovery, or production incident.
- Follow the runbook's authorization, verification, and stop conditions. Do not treat an implementation or commit request as deployment authorization.
