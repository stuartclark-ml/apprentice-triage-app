# Apprentice Triage App

A backend service for triaging apprenticeship and job-access vacancies, built as part of a career transition into regulated AI and safety-critical machine learning engineering.

![CI](https://github.com/stuartclark-ml/apprentice-triage-app/actions/workflows/ci.yml/badge.svg)

## Status

Early-stage. The FastAPI service scaffold, configuration, containerisation, and CI pipeline are complete and tested. The core agentic pipeline (multi-agent orchestration with LangGraph, external vacancy/transport data sources, human-in-the-loop review) is in active development — see the roadmap below.

## Stack

- **Python 3.12**, managed with [uv](https://docs.astral.sh/uv/)
- **FastAPI** for the API layer
- **Pydantic** / **pydantic-settings** for typed configuration
- **Docker** + Compose for local and reproducible runs
- **pytest**, **mypy**, **ruff** enforced via pre-commit and GitHub Actions

## Running locally

Without Docker:
```bash
uv sync
cp .env.example .env   # then fill in your own values
uv run fastapi run src/apprenticeship_navigator/api/main.py --port 8000
```

With Docker:
```bash
docker compose up
```

Either way, check it's alive:
```bash
curl http://localhost:8000/health
```

## Configuration

Copy `.env.example` to `.env` and set:

| Variable | Purpose |
|---|---|
| `APPRENTICESHIP_API_KEY` | Required. Authenticates API requests. |
| `APP_ENV` | `development` or `production`. |
| `LOG_LEVEL` | e.g. `debug`, `info`. |

## Testing

```bash
uv run pytest
uv run mypy .
uv run ruff check .
```

## Roadmap

- [ ] External data service layer (vacancy search, postcode-to-area lookup)
- [ ] LangGraph agent orchestration with tool-calling and observability
- [ ] Conditional routing on transport feasibility
- [ ] Multi-agent supervisor with parallel dispatch
- [ ] Human-in-the-loop interrupt with persisted state
- [ ] Streaming responses to a thin frontend
- [ ] Deployment to Google Cloud Run