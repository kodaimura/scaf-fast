# Application Architecture

## Status and source

This project adopts [HUMQ](https://github.com/kodaimura/humq) v1.1.0 for
application-layer responsibility boundaries, reviewed against upstream commit
[`d3c9150`](https://github.com/kodaimura/humq/commit/d3c9150a2b824e6197fbc87230a1dc6940631313).

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

Policy and Operation are internal ways to share limited logic without hiding
the main business flow. External clients isolate communication details.

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
            -> Policy
            -> Operation -> Module / Query / Policy
            -> External client -> external system
```

Apply these rules:

- Handler calls Usecase. It does not call Module, Query, Operation, or an
  external client directly.
- Usecase may call Module, Query, Policy, Operation, and external clients.
- Usecase may pass a SQLAlchemy `Session` and ORM models, but it does not issue
  ORM queries or persist ORM state directly.
- Policy depends only on the values needed for its calculation or decision.
- Operation may call Module, Query, and Policy using the caller's session. It
  does not call another Operation or own a transaction boundary.
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
- Call Module, Query, Operation, or external clients directly.
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
- Persist an ORM model directly with `add`, `delete`, `flush`, or similar
  session operations.
- Hide the main flow in generic services or chains of helpers.
- Call another public Usecase as a reuse mechanism.
- Combine unrelated business actions merely to reduce file count.

The main sequence, significant branches, state changes, external I/O, and
transaction outcome must remain readable from the Usecase. A Usecase may be
long when the business flow is inherently complex. Split it because it contains
an independently explainable action, not only because of line count.

A separate Usecase is appropriate when the behavior has its own trigger,
authorization decision, success or failure outcome, transaction boundary,
retry or compensation unit, or independently explainable business purpose.

## Policy

Policy is a deterministic business decision or calculation that does not use
the database or an external system. Prefer a function unless a class provides a
clear benefit.

Policy must:

- Receive all values required for its decision.
- Return the same result for the same input.
- Avoid `Session`, Module, Query, Operation, external clients, and mutable
  process state.
- Leave its invocation and the resulting major branch visible in the Usecase.

Place a Policy by the narrowest real scope:

1. Keep logic used by one Usecase in that Usecase file.
2. Put logic shared in one domain in `app/usecase/<domain>/_policies.py`.
3. Put only truly domain-independent business calculations in
   `app/usecase/_policies.py`.

Internal Policy files start with `_` and are not re-exported from package
`__init__.py` files.

## Operation

Operation is an exceptional database-dependent internal process for preserving
the same invariant across multiple Usecases when divergent implementations
would cause a concrete inconsistency. It is not an additional HUMQ layer and
must not replace the visible Usecase flow.

Operation may:

- Use the caller's SQLAlchemy session.
- Call Module, Query, and Policy.
- Perform shared validation, authorization, numbering, locking, duplicate
  detection, and limited multi-table coordination.
- Call `flush` when required by its work.

Operation must:

- Be called only from Usecase.
- Write each table through its owning Module.
- Leave the main call and the branch based on its result visible in Usecase.
- Avoid `begin`, `commit`, and `rollback`.
- Avoid calling external clients or another Operation.

Create an Operation only after multiple Usecases must preserve the same
invariant and cannot safely allow their validation, errors, locks, or update
order to diverge. The invariant and the concrete inconsistency caused by
divergence must be explainable. Reuse, similar code, or a long Usecase alone is
not sufficient reason.

Start with `app/usecase/<domain>/_operations.py`. If it becomes difficult to
read, split by owned business capability, for example
`_authorization_operations.py`. Do not create root-level generic Operations,
an `operations/` layer, or names such as `_common_operations.py` and
`_database_operations.py`. Internal Operation files are not re-exported.

## Module

A Module owns persistence behavior for one table by default. Place its model
and persistence implementation under `app/module/<singular_table>/`.

Module owns:

- Create, update, and delete operations for its table.
- Primary-key lookup, existence checks, standard lists, and basic reusable
  searches for its table.
- Constraints and state changes determined only by that table's values.
- Conditional updates, row locks, or optimistic locking for concurrent writes.
- ORM and SQL implementation details.

Module rules:

- Write to only the table the Module owns.
- Do not call another Module.
- Do not contain Usecase-specific business flow.
- Do not call an external system.
- Do not call `commit` or `rollback`; `flush` is allowed.
- Prefer database constraints for rules expressible with `UNIQUE`, `NOT NULL`,
  `CHECK`, and foreign keys.

A write to the owned table may read another table when that read is required to
construct or condition the write. It must not modify the other table or expand
the Module into a general cross-table reader.

Express multi-table writes by having a Usecase call the relevant Modules. If an
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
and Operation may flush work but do not decide whether the business transaction
succeeds. Query is read-only and owns no transaction boundary.

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

1. External input or output shape, routing, or protocol mapping: Handler.
2. Business sequence, branch, authorization, or transaction: Usecase.
3. Pure decision or calculation: local Usecase function, then Policy only when
   genuinely shared.
4. Shared database-dependent internal behavior: Operation only when the same
   invariant and concrete inconsistency criteria are met.
5. Basic read or any write for one table: that table's Module.
6. Cross-table or use-specific complex read: Query.
7. External protocol and data-format details: external client.
8. Framework bootstrap or technical infrastructure: a clearly named
   infrastructure location such as `core`, never a hidden business layer.

If code does not fit, reconsider the responsibility before adding a new generic
layer. Necessary business complexity belongs visibly in Usecase.

## Testing expectations

Tests protect both behavior and responsibility boundaries:

- Test Usecase business branches, authorization, state changes, external-I/O
  decisions, transaction success, and rollback.
- Test Policy as pure input/output behavior.
- Test Operation success, failure, and caller-owned rollback using the same
  session and realistic Module or Query behavior.
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

Prefer traceability over reuse. Do not move business steps out of Usecase merely
to shorten it. Operation is an exception, not the normal growth path. Review
the design when Operations multiply, lose a clear owning domain, call one
another, become generic Services, or hide most of the main flow.

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

- [Reviewed HUMQ revision](https://github.com/kodaimura/humq/tree/d3c9150a2b824e6197fbc87230a1dc6940631313)
- [Layer and responsibility rules](https://github.com/kodaimura/humq/blob/d3c9150a2b824e6197fbc87230a1dc6940631313/docs/02-layer-rules.md)
- [Design principles](https://github.com/kodaimura/humq/blob/d3c9150a2b824e6197fbc87230a1dc6940631313/docs/03-design-principles.md)
- [Consistency and transactions](https://github.com/kodaimura/humq/blob/d3c9150a2b824e6197fbc87230a1dc6940631313/docs/04-consistency-and-transactions.md)
- [FastAPI example](https://github.com/kodaimura/humq/blob/d3c9150a2b824e6197fbc87230a1dc6940631313/docs/06-fastapi-example.md)
- [Adoption limits and evolution](https://github.com/kodaimura/humq/blob/d3c9150a2b824e6197fbc87230a1dc6940631313/docs/07-adoption-limits-and-evolution.md)
