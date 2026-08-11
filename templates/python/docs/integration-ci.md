# Integration CI

Keep fast, deterministic checks in the normal pull-request workflow. Run
Docker/service integration only when files that can affect the runtime change.

The integration workflow should use path filters for:

- application and package code (`src/**`, `packages/**`)
- integration tests (`tests/**`)
- dependency and container definitions (`pyproject.toml`, `uv.lock`, `Dockerfile`, `docker-compose.yml`, `docker/**`)
- the integration workflow itself

It should also run on pushes to `main`/`master` and support `workflow_dispatch`.

Documentation-only, formatting-only, and unrelated UI changes should not pay the
cost of starting service containers.

Forgejo local runners execute jobs inside Docker containers. A job container's
`localhost` is not the runner host. For services started with Compose through the
runner's Docker socket, use the runner-provided host alias (currently
`forgejo-host`) or place the test process on the Compose network and use service
names. Do not assume the GitHub-specific `host.docker.internal` alias exists.

Use `scripts/ci/wait_for_http.sh` for bounded health checks, and always collect
service logs and tear down Compose services with `if: always()`.
