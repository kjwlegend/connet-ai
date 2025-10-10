# AI Module Migration TODO

## Guiding Principles
- Organize all AI-related domains under `app/modules/ai/` with focused slices (agents, memory, knowledge bases, RAG, tools, workflows).
- Each slice follows the vertical pattern (`models`, `repository(.py)`, `repository_impl.py`, `service.py`, optional `router.py`/`schemas.py`).
- Legacy services under `app/services/` now act only as shims; new code lives in modules.
- Update `alembic/env.py`, seed scripts, and compatibility imports whenever models move.
- Keep documentation (`docs/backend/system-directory-architecture.md`) aligned with the current structure before merging.

## Completed
- `memory/` slice created with models, repositories, and service; shim `app/services/ai_memory_service.py` updated.
- Knowledge bases and RAG logic migrated into `app/modules/ai/knowledge_bases/` and `app/modules/ai/rag/` with protocol-based repositories and shims.
- Tools stack refactored into `app/modules/ai/tools/`; legacy models, repositories, and service now delegate to the slice.
- Storage metadata moved into `app/modules/storage/files/` including schemas, repositories, service, and compatibility exports.
- LangGraph workflows relocated to `app/modules/ai/workflows/` with engine, services, tracking, and tools now exposed through the slice.

## Outstanding Tasks
1. **Documentation & Tests**
   - Update `docs/backend/system-directory-architecture.md` and any other references after each migration.
   - Rework tests to import from new module paths as slices are moved.

## Notes
- Keep Supabase auth logic under the `auth` module (no migration required).
- Rename or refine labels (e.g. `knowledge_bases`) if better naming emerges during implementation.
