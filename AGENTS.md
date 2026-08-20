# Repository Instructions

## Project Context

- This repository is a FastAPI backend scaffold.
- Read `README.md` and the `Makefile` before changing setup or development workflows.
- Preserve the existing project structure and naming unless the task requires an architectural change.

## Architecture

- This project follows HUMQ v1.1.0.
- Before designing, reviewing, or changing application code under `app/`, read and follow `docs/ARCHITECTURE.md`.
- Treat `docs/ARCHITECTURE.md` as the local source of truth for responsibility boundaries, dependency direction, code placement, transactions, and architecture tests.
- When a requested change intentionally alters or departs from the architecture, update the implementation and `docs/ARCHITECTURE.md` together and make the exception explicit.

## Working Agreements

- Keep changes focused and preserve unrelated work.
- Do not commit secrets, local environment files, or generated runtime data.
- Add or update tests when behavior changes.

## Verification

- Run `make check` for lint and unit tests.
- Run `make test_e2e` when API behavior or database integration changes.
- Run `make smoke_prod` when production dependencies or container configuration changes.

## Operations

- Before changing production configuration, deployment behavior, database migration procedures, health checks, or rollback behavior, read `docs/RUNBOOK.md`.
- Read `docs/RUNBOOK.md` before assisting with a deployment, release, rollback, recovery, or production incident.
- Follow the runbook's authorization, verification, and stop conditions. Do not treat an implementation or commit request as deployment authorization.
