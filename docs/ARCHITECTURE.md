# Application Architecture

## Status and source

This project adopts [HUMQ v1.2.0](https://github.com/kodaimura/humq/tree/v1.2.0) for
application-layer responsibility boundaries.

This document is the local implementation contract for this repository. HUMQ
provides the complete rationale and design background; this document fixes the
rules that contributors and coding agents must apply to this codebase. A later
HUMQ release does not change this project automatically. Upgrade the reference
version and this document together after reviewing the upstream changes.

## Scope

HUMQ determines where code belongs in request-driven business processing:

- Handler connects an external caller to the application.
- Usecase owns a business flow and its transaction boundaries.
- Module owns reads and writes for one table by default.
- Query owns read-only, use-specific reads that cross tables.

Usecase may delegate business decisions and consistency processing to named
internal files. External clients isolate communication details.

HUMQ does not prescribe the placement of configuration, database setup,
logging, migrations, framework bootstrap, or other infrastructure. In this
project those concerns can remain under `app/core/`, `app/alembic/`, and other
clearly named infrastructure packages. `core` is not a business layer and must
not become a place for business rules.

The singular directory names used by this scaffold (`handler`, `usecase`,
`module`, and `query`) are project naming choices. They have the same
responsibilities as HUMQ's Handler, Usecase, Module, and Query.

## Dependency direction

The normal dependency flow is:

```text
Caller
  -> Handler
       -> Usecase
            -> Module -> ORM / database
            -> Query  -> ORM / database
            -> Internal business processing -> Module / Query
            -> External client -> external system
```

Apply these rules:

- Handler calls public Usecase. It does not call Module, Query, Usecase
  internals, or external clients directly.
- Usecase may call Module, Query, named internal business processing, and
  external clients.
- Usecase may pass a SQLAlchemy `Session` and ORM models, but it does not issue
  ORM queries or modify and persist ORM state directly.
- Internal business processing may read through Module or Query and write
  through Module using the calling Usecase's session.
- Module does not call another Module, Query, Usecase, Handler, or external
  client.
- Query reads through the ORM or SQL directly. It does not call Module and does
  not depend on Handler or Usecase.
- An external client does not call application layers or access the database.
- Framework and infrastructure utilities must not hide business flow or
  reverse these dependencies.

Avoid generic `service`, `manager`, `helper`, or `utils` abstractions that make
the owner of a business decision unclear. Name code after its responsibility
and business meaning.

## Handler

Handler translates between an external interface and a Usecase. HTTP handlers
live under `app/handler/`; request and response DTOs live under
`app/handler/dto/`.

Handler may:

- Define routes, status codes, headers, and response shapes.
- Parse and validate the form and types of caller input.
- Obtain a request-scoped database session through FastAPI dependencies and
  pass it to a Usecase.
- Extract authenticated identity and request context and pass them to a
  Usecase.
- Convert a request DTO to Usecase input and a Usecase result to a response DTO.
- Convert application errors through the common response and error boundary.

Handler must not:

- Contain business conditions, authorization decisions, or state transitions.
- Query or mutate ORM models.
- Call Module, Query, Usecase internals, or external clients directly.
- Start, commit, or roll back a transaction.
- Perform joins, aggregation, or other persistence work.

Authentication at the protocol boundary may identify the caller. Whether that
caller is allowed to perform a business action is a Usecase decision.

## Usecase

A Usecase represents one explainable business action. Public Usecases called by
Handler live in `app/usecase/<domain>/` and normally expose an `execute()`
method. Usecase input and result types may live beside that Usecase.

Usecase owns:

- The meaningful order of business steps.
- Business validation, authorization, branching, and state transitions.
- Coordination of Module and Query calls.
- Transaction boundaries and cross-table consistency.
- Decisions about whether and when to call external systems.
- Retry, compensation, idempotency, and failure policy at the business level.
- Necessary exceptions and special cases in the business flow.

Usecase must not:

- Depend on FastAPI request or response objects.
- Execute ORM queries or SQL directly.
- Change mapped attributes on persistent ORM models or persist a model
  directly with `add`, `delete`, `flush`, or similar session operations.
- Hide the main flow in generic services or chains of helpers.
- Call another public Usecase as a reuse mechanism.
- Combine unrelated business actions merely to reduce file count.

The purpose, main sequence, significant branches, transaction boundaries,
external I/O, and failure policy must remain readable from the Usecase. A Usecase
may be long when the business flow is inherently complex. Split it when it
contains an independently explainable action.

A separate Usecase is appropriate when the behavior has its own trigger,
authorization decision, success or failure outcome, transaction boundary,
retry or compensation unit, or independently explainable business purpose.

## Internal business processing

Small decisions can stay in the Usecase. A decision, calculation, or consistency
process may move to a named internal file when it has a business purpose worth
explaining, verifying, or changing independently, even with a single caller.
Keep the reason for calling it and the primary branch on its result visible
in the Usecase. Make its validation, locking, and state changes traceable in
the referenced file.

Start in the owning domain's `app/usecase/<domain>/` directory. Use
`_policies.py` as a starting filename for extracted business rules or pick a
name that identifies the responsibility, such as `_login_id.py`. A rule under
`_policies.py` can use the database. For rules used across domains, prefer an
obvious business owner or use a cohesive shared package. Mark internal files
with a leading `_` and keep them out of public package re-exports. Choose a
function or class according to the processing it represents.

Pure decisions and calculations take their required values as inputs. Internal
processing that needs database access uses Module or Query for reads and the
owning Module for writes. It uses the calling Usecase's Session. The Usecase
owns `begin`, `commit`, `rollback`, external-system calls, and failure policy.

## Module

A Module owns persistence behavior for one table by default. Place its model
and persistence implementation under `app/module/<singular_table>/`.

Module owns:

- Create, update, and delete operations for its table.
- Primary-key lookup, existence checks, standard lists, and basic reusable
  searches for its table.
- Constraints and state changes that protect the table's state or updates.
  Decisions about when to perform those updates belong in Usecase.
- Conditional updates, row locks, or optimistic locking for concurrent writes.
- ORM and SQL implementation details.

Module rules:

- Write to only the table the Module owns.
- Do not call another Module.
- Do not contain Usecase-specific business flow.
- Do not call an external system.
- `flush` is allowed. The calling Usecase owns `commit` and `rollback`.
- Keep writes from ORM cascades, hooks, and callbacks within the same table.
- Prefer database constraints for rules expressible with `UNIQUE`, `NOT NULL`,
  `CHECK`, and foreign keys.

A write to the owned table may read another table when that read is required to
construct or condition the write. It must not modify the other table or expand
the Module into a general cross-table reader.

Express multi-table writes through the owning Modules, called by the Usecase
directly or through named internal processing in the same transaction. If an
unavoidable single statement or stored procedure writes multiple tables, treat
it as an explicit architecture exception: record the tables and reason in a
project-specific decision record and cover the behavior with integration tests.
Do not turn the exception into a generic Service.

A Repository is not a HUMQ layer. Introduce one only as a private Module
implementation detail when persistence complexity requires it. Usecase never
calls Repository directly, and the one-table Module boundary remains intact.

## Query

Query builds a read-only model for a particular observation or use. Place it
under `app/query/` and name it after the business view, report, search, or
observation rather than a table.

Use Query for:

- Reads that join or aggregate multiple tables.
- Screens, reports, exports, dashboards, and analysis read models.
- A specialized single-table read whose complex search, window function, JSON
  processing, or output model does not fit standard Module operations.

Query must not:

- Insert, update, or delete data.
- Mutate ORM model state.
- Own `commit`, `rollback`, or an application transaction boundary.
- Contain business flow or state transitions.
- Duplicate standard CRUD or basic lookups that belong to Module.

Handler still calls a read-only Usecase when the Usecase only delegates to a
Query. A thin Usecase preserves the external-interface boundary and is not a
reason for Handler to call Query directly.

## External clients and infrastructure

An external client isolates communication with another system. It owns HTTP,
SDK, SMTP, storage, queue, or similar protocol details, including request
construction, credentials, response parsing, timeouts, and translation of
transport failures.

An external client must not own business branching, call Module or Query,
manage database transactions, or decide the business response to a failure.
Usecase owns those decisions.

Small infrastructure adapters may remain under `app/core/` in this scaffold.
When integrations grow, move them to a clearly named `app/client/` or
`app/integration/` package without changing the application dependency rules.

## Transactions and consistency

The Handler-called Usecase owns each application transaction boundary. Module
may flush work. Query is read-only, and any database-using internal processing
participates in the Usecase's transaction.

`SessionLocal` uses `expire_on_commit=False` so ORM objects returned by a
committed Usecase remain loaded while the Handler maps them to response DTOs.
This avoids an implicit post-commit SELECT from the Handler boundary. Explicitly
refresh an entity when a flow needs database-generated or concurrently updated
state after its last flush.

HUMQ does not structurally guarantee multi-table consistency. A Usecase can
still omit a required Module call or business rule while respecting every
dependency boundary. Use database constraints and Usecase rollback tests to
reduce that risk. When a domain cannot accept implementation-level protection,
use an aggregate-centered or otherwise structurally protective design there.

Apply these rules:

- Group changes that must succeed or fail together in the same transaction.
- Let exceptions roll the transaction back; do not leave partial business
  state committed.
- Use database constraints as the final guard for representable invariants.
- Put row locks, conditional updates, and optimistic-lock mechanics in the
  relevant Module; keep the business decision about their result in Usecase.
- Test business branches, failures, and rollback behavior explicitly.

HUMQ does not require one transaction for every Usecase. A read-only Usecase
may not need an explicit transaction. A workflow spanning requests or external
systems may use multiple transactions, but the state committed by each step and
the failure policy must be visible in the Usecase.

Database transactions cannot make external I/O atomic:

- Perform best-effort notifications after commit when their failure is
  acceptable.
- Use an outbox written in the same transaction when a delivery request must not
  be lost.
- Use idempotency, retry, and compensation for external state changes such as
  payments.

## Code-placement procedure

Use this order when adding behavior:

1. External input or output shape, routing, or protocol mapping → Handler.
2. Business sequence, branch, authorization, or transaction → Usecase.
3. Business decision, calculation, or consistency processing → Usecase, with
   optional extraction into a named internal file when independently meaningful.
4. Basic read or any write for one table → that table's Module.
5. Cross-table or use-specific complex read → Query.
6. External protocol and data-format details → external client.
7. Framework bootstrap or technical infrastructure → a clearly named
   infrastructure location such as `core`, never a hidden business layer.

If code does not fit, reconsider the responsibility before adding a new generic
layer. Necessary business complexity belongs visibly in Usecase.

## Testing expectations

Tests protect both behavior and responsibility boundaries:

- Test Usecase business branches, authorization, state changes, external-I/O
  decisions, transaction success, and rollback.
- Test pure decisions with inputs and expected outputs.
- Test database-using internal processing for consistency and failure with a
  real database, including rollback by the calling Usecase.
- Test Module and Query SQL, constraints, joins, locking, and transaction
  behavior against a real database when those details matter.
- Test Handler request validation, authentication context, status codes,
  response contracts, and complete flows through API E2E tests.
- Add a regression test whenever an architecture exception or production defect
  exposes a missing boundary check.

Run `make check` for lint and unit tests. Run `make test_e2e` when API behavior,
database integration, transaction behavior, Module, Query, migration, or an
end-to-end flow changes.

## Evolution and exceptions

Prefer business meaning and traceability over reuse. Review the design when
internal files lose a clear owner, collect unrelated rules, introduce nested
or cyclic dependencies, or obscure the primary flow.

If a domain's shared invariants become too complex for these boundaries, that
domain may deliberately adopt an aggregate-centered or other architecture while
the Handler-to-Usecase interface remains stable. Document the scope, reason,
dependency changes, migration plan, and tests. Do not silently mix different
placement rules inside the same domain.

Any deliberate exception must be narrow, documented with the implementation,
and tested at the level where its risk appears. If an exception becomes a
repeated pattern, update this architecture contract or redesign the affected
domain instead of accumulating undocumented precedent.

## Upstream references

- [HUMQ v1.2.0 repository](https://github.com/kodaimura/humq/tree/v1.2.0)
- [Layer and responsibility rules](https://github.com/kodaimura/humq/blob/v1.2.0/docs/02-layer-rules.md)
- [Design principles](https://github.com/kodaimura/humq/blob/v1.2.0/docs/03-design-principles.md)
- [Consistency and transactions](https://github.com/kodaimura/humq/blob/v1.2.0/docs/04-consistency-and-transactions.md)
- [FastAPI example](https://github.com/kodaimura/humq/blob/v1.2.0/docs/06-fastapi-example.md)
- [Adoption limits and evolution](https://github.com/kodaimura/humq/blob/v1.2.0/docs/07-adoption-limits-and-evolution.md)
