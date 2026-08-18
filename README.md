# scaf-fast

FastAPI backend scaffold.

## Create a project

This scaffold supports direct cloning, GitHub's **Use this template**, and
generation through webscaf.

For a direct clone or a repository created from the GitHub template, clone it
using the intended project directory and initialize it once:

```sh
git clone <repository-url> my-app
cd my-app
make init
```

`make init` uses the current directory name. Override it when needed with
`make init PROJECT_NAME=another-name`. webscaf runs the same initialization
automatically. Skip initialization only when developing this scaffold itself.

After pushing a new repository to GitHub, complete the one-time
[`docs/GITHUB_SETTINGS.md`](docs/GITHUB_SETTINGS.md) checklist.

## Development

This template is intended to run through Docker. Local Python and Node are not
required for normal development.

```sh
make build
make up
make migrate
```

Useful commands:

```sh
make logs
make exec
make check
make lint
make test
make test_e2e
make audit
make build_prod
make smoke
make routes
make requirements_compile
make down_volumes
```

API E2E tests are organized by domain so new endpoints can add coverage at the
same level. See [`test/e2e/README.md`](test/e2e/README.md).

Pull requests run the same checks in GitHub Actions. See
[`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) before contributing and report
suspected vulnerabilities according to [`docs/SECURITY.md`](docs/SECURITY.md).

Host ports are bound to `127.0.0.1` by default. Set `API_BIND_HOST=0.0.0.0`
only when the API must be reachable from outside the host.

Use production compose settings with `ENV=prod`.

```sh
cp .env.example .env
# Edit production secrets and database settings in .env.
make build ENV=prod
make migrate ENV=prod
make up ENV=prod
```

The development database is stored in the Docker named volume
`scaf-fast_postgres_data`.
