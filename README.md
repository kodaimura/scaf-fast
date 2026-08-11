# scaf-fast

FastAPI backend scaffold.

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
make smoke
make routes
make requirements_compile
make down_volumes
```

Host ports are bound to `127.0.0.1` by default. Set `API_BIND_HOST=0.0.0.0`
only when the API must be reachable from outside the host.

Use production compose settings with `ENV=prod`.

```sh
cp api/.env.example api/.env
# Edit production secrets and database settings in api/.env.
make build ENV=prod
make migrate ENV=prod
make up ENV=prod
```

The development database is stored in the Docker named volume
`scaf-fast_postgres_data`.
