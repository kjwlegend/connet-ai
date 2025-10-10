# Repository Guidelines

## Project Structure & Module Organization
- `frontend/`: Next.js 15 App Router; routes in `src/app`, shared UI in `src/components`, state helpers in `src/lib` and `src/store`, tests colocated or under `tests/`.
- `bff/`: FastAPI service with domain modules in `app/`, LangGraph workflows in `app/workflows`, migrations in `alembic/`.
- `agents/`: JSON personas for AI contacts—modify only through reviewed PRs.
- `docs/`, `design/`, `planning/`: living specs and trackers; consult them before starting work.

## Architecture Snapshot
- Frontend state uses the documented Zustand slices (`auth`, `ui`, `chat`, `settings`) in `docs/2025-08-01_data-flow-state-management.md`; extend existing slices instead of creating new stores.
- Backend is mid Phase 2 of the contact-instance roadmap (`docs/backend/progress-tracker.md`), focusing on Contact repositories, LangGraph workflow engine, and pending schema updates.

## Build, Test, and Development Commands
- Frontend: `cd frontend && pnpm install && pnpm dev`; build with `pnpm build`, preview via `pnpm start`, lint with `pnpm lint`.
- Backend: `cd bff && pip install -r requirements.txt` or `make install`; run `make dev`, or `make docker-start` for API + Postgres + Redis; stop with `make docker-stop`.
- Shared: `make debug-start` spins up Postgres/Redis only—follow with `make debug-stop`.

## Coding Style & Naming Conventions
- TypeScript: 2-space indent, PascalCase components, camelCase hooks/utilities, Tailwind classes inline. `pnpm lint` (ESLint 9) must pass.
- Python: `make format` (Black + isort) and `make lint` (flake8 + mypy) are required; keep modules snake_case and async endpoints under `app/api`.

## Testing Guidelines
- Frontend: write `*.test.ts(x)` beside features or in `frontend/tests/`; run `pnpm test`, and add `pnpm test:coverage` when touching shared state or network flows.
- Backend: add Pytest coverage in `tests/` or root-level `test_*.py`; run `make test`, and `make test-cov` for persistence, workflow, or API changes to meet the 80% goal in backend trackers.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`feat`, `refactor`, `chore`) and squash WIP.
- PRs include objective, bullet summary, test results, linked task, and UI snapshots or API diffs. Request cross-area reviewers when touching both `frontend/` and `bff/`, and merge only after green CI plus doc updates.

## Environment & Configuration
- Copy env templates (`frontend/env.example` → `.env.local`, `bff/.env.example` → `.env`).
- Feature flags live in `frontend/src/lib/config/features.ts` and `bff/app/core/config.py`; edit both when adding or renaming a flag.

## Documentation & Planning
- Review `docs/frontend/frontend-progress-tracker.md` and `docs/backend/progress-tracker.md` before scoping work.
- Record architecture or workflow decisions in the matching doc tree so downstream agents stay in sync.

## Backend Module Standards
- Backend code lives under vertical slices in `bff/app/modules/<domain>/` (e.g., `users`, `contacts`, `conversations`). Each module owns its `models.py`, `repository.py` (ABC/Protocol), `repository_impl.py`, `service.py`, `router.py`, optional `policies.py` and `tasks.py`, plus an `__init__.py` that only re-exports public APIs.
- When a domain needs additional sub-boundaries (e.g., `conversations/messages/`), keep the subpackage inside the same module so the slice still ships as a cohesive unit.
- Modules must never import each other’s internals. Cross-module usage happens via explicit service interfaces, domain events in `app/core/events`, or shared abstractions promoted into `app/core`/`app/infrastructure`.
- Domain events: producers declare payloads in `modules/<slice>/events.py`, and handlers live in `modules/<slice>/event_handlers.py`. Register handlers during startup via `app/api/lifespan.py` so they subscribe once to the singleton event bus (`app/infrastructure/messaging/event_bus.py`).
- Allowable module imports: shared configuration and utilities in `app/core/*`, infrastructure adapters in `app/infrastructure/*`, and standard library / third-party packages. `router.py` files only interact with FastAPI dependencies and their own module’s service layer.
- Transactions are managed by the API layer using dependencies from `app/api/deps/db.py`. Repositories must not call `commit()`/`rollback()`; they may `flush()` when the new entity’s identity is required.
- Authentication and RBAC dependencies live in `app/api/deps/auth.py` and `app/api/deps/rbac.py`, which build on helpers from `app/core/security.py`. Module-level ABAC or visibility rules should live in that module’s `policies.py`.
- Top-level router aggregation happens in `app/api/routers.py` (exporting `api`). Individual module routers are included there with their prefix and tags; routers must not include other routers directly.
- FastAPI dependencies are split under `app/api/deps/` (`db.py`, `auth.py`, `cache.py`, `services.py`, `pagination.py`, `rbac.py`). Legacy imports from `app.api.dependencies` must be treated as compatibility shims only.
- Configuration is centralized in `app/core/config.py` (Pydantic settings). No module should read environment variables directly.
- Alembic migration filenames use `YYYY_MM_DD_<module>_<change>.py`, and `alembic/env.py` must include metadata from every `app/modules/*/models.py`.
- Review `docs/backend/event-bus-architecture.md` before introducing new event types or handlers to ensure publishing/handler patterns stay consistent.
