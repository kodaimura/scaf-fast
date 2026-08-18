# Contributing

Keep changes focused, reviewable, and covered by tests. Never commit credentials,
tokens, personal data, or a production `.env` file.

## Before opening a pull request

Run the same checks used by CI:

```sh
make check
make test_e2e
make build_prod
```

Run `make audit` when runtime dependencies change and before a release. An audit
finding is reviewed according to its exploitability, available fixes, and
upgrade cost; it does not automatically block unrelated pull requests.

When behavior changes, add or update tests at the same level as the change.
Update `.env.example` and the documentation when configuration changes. Include
an Alembic migration for database schema changes, and verify both upgrade and
application behavior.

## Pull requests

- Explain the reason for the change, not only the implementation.
- Keep unrelated changes in separate pull requests.
- Describe API, database, configuration, and deployment impact.
- Resolve review comments and make sure CI passes before merging.
- Complete the relevant items in the pull request template.

Report vulnerabilities privately by following [SECURITY.md](SECURITY.md), not
through a public issue or pull request.
