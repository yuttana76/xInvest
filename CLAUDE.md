# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

xInvest is a multi-service investment/fund-analysis platform: a Django backend (core business logic, AI, data), a Go service for trading data/execution, a Next.js web frontend, and a Flutter mobile app, sharing one PostgreSQL database. See `README.md` for the feature-level pitch.

## Repository layout

- `backend/` — Django 5.2 monolith: auth, fund analysis, AI/LangChain pipelines, workflow/approval engine, FundConnext ETL. Has its own subagent (`backend-django`).
- `go-trading/` — Go (Gin) service for trading signals/execution, reachable at `/api/v1/...` via its own router (not proxied through the Django backend). Subagent: `trading-go`.
- `frontend/` — Next.js 16 (App Router) + TypeScript web app. Subagent: `frontend-web`.
- `x_mobile_v2/` — Flutter mobile app. Subagent: `mobile-flutter`.
- `nginx/`, `docker-compose*.yml`, `postgrest.conf`, `scripts/` — deployment/local-env plumbing. Subagent: `infra-devops`.
- `docs/` — living documentation: `docs/features/` (per-feature notes), `docs/system/` (ops like backup/restore), `docs/business-logic/` (current business rules, one file per domain, overwritten as rules change), `docs/adr/` (one-time decision records, numbered `NNNN-title.md`, never edited after the fact). Only create/update `business-logic`/`adr` docs when explicitly asked to.
- There is no `.github/workflows/` — no CI/CD is configured yet in this repo.

When work is scoped to one of the four app directories above, prefer delegating to its dedicated subagent rather than working across the whole repo.

## Running the stack

```bash
# Local development (hot reload, exposes db/redis ports, includes flower + cloudflare tunnel + backup cron)
docker compose -f docker-compose.dev.yml up -d --build

# Run Django migrations after first boot / after model changes
docker compose exec backend python manage.py migrate

# Production compose (no direct db port exposure, nginx fronts frontend+backend)
docker compose -f docker-compose.yml up -d --build
```

- Investor web app: http://localhost:3000 — Admin portal: http://localhost:3000/admin-portal
- API docs (drf-spectacular): http://localhost:8000/api/schema/swagger-ui/
- GraphQL (Graphene), graphiql enabled: http://localhost:8000/graphql
- Celery Flower (dev only): http://localhost:5555

`docker-compose.dev-trade.yml` is a separate compose file for running `go-trading` in isolation.

## Backend (Django) — `backend/`

- Entrypoint: `manage.py`; settings/celery/schema/urls live in `core/`.
- Apps: `users` (auth, OTP, profiles, activity log), `invest` (investor accounts, transactions, ETL, statement reports), `fundDecision` (fund analysis, AI insights, news, factsheets, vector search), `stt_fundconnext` (FundConnext data ingestion: profiles, performance, allocations, holdings), `workflow` (generic request/approval engine with configurable steps and approval logs).
- API surface is mounted per-app under `/api/v1/<app>/` in `core/urls.py`; GraphQL schema is assembled in `core/schema.py` from per-app `schema.py` files (currently `stt_fundconnext`).
- AI pipeline lives in `fundDecision/ai_service.py` and `fundDecision/graph_service.py` (LangGraph-based), invoked from `fundDecision/tasks.py` for news sentiment and factsheet analysis; Gemini access is via `langchain-google-genai`.
- Async work runs through Celery (`core/celery.py`, autodiscovers `tasks.py` per app) against Redis; each app owns its own `tasks.py` (news/AI analysis, FundConnext ETL, email notifications, OTP/password-reset emails, investment ETL/reporting).
- Tests are plain Django tests (`tests.py` / `tests/` per app, e.g. `invest/tests_etl.py`), no pytest config present:
  ```bash
  python manage.py test                      # all apps
  python manage.py test fundDecision         # one app
  python manage.py test invest.tests_etl.SomeTestCase.test_something   # single test
  ```
- Local run outside Docker: `python manage.py runserver 0.0.0.0:8000` (needs `.env.dev`-equivalent env vars — see `.env.example`).

## Go trading service — `go-trading/`

- Module `xinvest/go-trading`, Gin router built in `cmd/api/main.go`; `internal/middleware/auth.go` validates JWTs (issued by the Django backend — shared `JWT_SECRET_KEY`/algorithm).
- `internal/repository/db.go` reads the **same Postgres database** as Django directly via `lib/pq` (e.g. `invest_investor`, `invest_investoraccount`, `fundDecision_fundanalysis` tables) — schema changes in Django models can break this service silently since there's no shared ORM layer.
- `internal/repository/redis.go` is used for response caching (see the fire-and-forget cache-warm goroutine in `internal/api/handlers/invest.go`).
- Currently only one route group is implemented (`/api/v1/invesInfo` → portfolio/investment info); despite the service name, no signal-generation or order-execution endpoints exist yet.
- Config via Viper (`internal/config/config.go`).
- Tests: `go test ./...` (see `internal/middleware/auth_test.go`, `internal/api/handlers/invest_test.go`).

## Frontend — `frontend/`

- Next.js 16 App Router under `frontend/src/app/`; route groups `(admin)` and `(investor)` split admin-portal vs investor dashboard, plus standalone top-level routes (`login`, `register`, `discovery`, `fund`, `workflow`, `operator`, `marketing`, `agent`, password reset flow).
- Path alias `@/*` → `frontend/src/*` (see `tsconfig.json`, `strict: true`).
- No shadcn/ui is actually installed despite being mentioned in `README.md` — components under `frontend/src/components/` are hand-rolled. Charting is split between Recharts and Tremor (`@tremor/react`) depending on the page — check the specific page before assuming which library to use.
- Data fetching: Apollo Client (GraphQL, talks to the Django `/graphql` endpoint) + `@tanstack/react-query` + `axios` for REST; `zustand` for client state.
- Commands: `npm run dev`, `npm run build`, `npm run start`, `npm run lint` (ESLint flat config).

## Mobile — `x_mobile_v2/`

- Flutter, Dart SDK `^3.11.3`. Screens in `lib/screens/`, single `lib/models/portfolio.dart`, networking in `lib/services/` (`auth_service.dart`, `portfolio_service.dart`) using the raw `http` package — no Dio/Retrofit.
- **API base URL is hardcoded to `http://localhost:8000`** in the service files — update this when pointing the app at a non-local backend.
- State management is plain `StatefulWidget`/`setState` throughout; no Provider/Riverpod/Bloc dependency exists yet, so don't assume one when adding features.
- Charts via `fl_chart`.

## Cross-service notes

- The Go service and Django backend both read/write the same Postgres instance directly — when changing a Django model that `go-trading` also queries, check `go-trading/internal/repository/db.go` and its callers for the corresponding raw SQL/column expectations.
- JWTs are minted by Django (`djangorestframework-simplejwt`) and independently verified by Go (`golang-jwt/jwt/v5`) — keep the shared secret/algorithm in sync across `.env.dev` / `.env.production`.
- `docker-compose.yml` (prod) intentionally does not expose the Postgres port to the host; `docker-compose.dev.yml` does, for local DB client access.
