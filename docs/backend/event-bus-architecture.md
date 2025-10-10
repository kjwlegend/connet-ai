# Event Bus Architecture

## Goals
- Enable domain modules to react to cross-cutting events without hard imports between slices.
- Provide a lightweight in-process bus that supports async handlers, batching, and future upgrades to external queues (Redis/NSQ/etc.).
- Guarantee that publishing occurs after the current transaction succeeds, preventing handlers from seeing uncommitted state.

## Components
- `app/infrastructure/messaging/event_bus.py`: singleton in-memory bus (`get_event_bus`) with `start/stop`, `subscribe`, and `publish`. Handlers can be async or sync (wrapped via `asyncio.to_thread`).
- `app/core/events.py` (planned): shared event definitions or dispatcher helpers. Each module should declare its own event dataclasses/enums in `modules/<slice>/events.py` and expose helper functions there.
- Module handlers live beside the slice (e.g., `modules/users/event_handlers.py`) and are registered at startup.
- FastAPI lifespan (`app/api/lifespan.py`) is responsible for starting/stopping the bus and registering all handlers exactly once.

## Publishing Workflow
1. Inside a service or repository, collect domain events but avoid immediate publication.
2. Attach the events to the Unit of Work/session context (e.g., `session.info.setdefault("events", []).append(event)`).
3. In the request dependency wrapper (`app/api/deps/db.py`), after a successful commit, iterate collected events and call `event_bus.publish(event.type, event)`.
4. On rollback, drop the buffered events.

## Handler Registration
- Each slice exposes `register_handlers(event_bus)` in `modules/<slice>/event_handlers.py`.
- `app/api/lifespan.py` imports each slice’s registration function and invokes it with the singleton bus during startup.
- Handlers should be short, idempotent and able to run concurrently. For blocking operations (email, HTTP calls) push work to background tasks/celery/arq.

## Naming & Conventions
- Event type string: `<module>.<aggregate>.<past-tense>` (e.g., `users.account.created`).
- Event payloads use Pydantic models or simple dataclasses to enforce shape.
- Document each event contract in the owning module’s README or `events.py` docstring.
- Keep handlers in the consuming module; do not mutate producer state.

## Future Extensions
- Swap the in-memory bus with Redis streams or Kafka by changing `EventBus` implementation (interface stays consistent).
- Add middleware for retries, dead-letter queues, or tracing (integrate with OpenTelemetry spans via handler wrappers).

## Checklist for Contributors
- [ ] Declare events in the producing module’s `events.py`.
- [ ] Publish events only after transaction commit.
- [ ] Register new handlers in `<module>/event_handlers.py` and wire them in `app/api/lifespan.py`.
- [ ] Add tests that trigger the event and assert handler side-effects.
- [ ] Update documentation when introducing new event types.
