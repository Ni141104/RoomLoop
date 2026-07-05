# Backend Agent Checklist

This checklist contains backend implementation tasks only. It follows `requirements.md`, `TSD.md`, and `docs/execution_roadmap.md` as the source of truth.

## Configuration

### Task 1: Create application configuration and environment loading
- Objective: define the runtime configuration contract for application name, host, port, database connection, and default timezone.
- Files to Create: `app/core/config.py`, `.env.example`, `.gitignore`, `run.py`.
- Files to Modify: `README.md`, `app/main.py`.
- Dependencies: none.
- Acceptance Criteria: configuration values are loaded from environment variables; `.env.example` documents the expected keys; `.env` is ignored; the application can start from the configured entrypoint.
- Related Requirement: IC-1, IC-3, requirements 8.2, 8.6, 8.8.
- Related TSD Section: Sections 2, 10, 13, 16.

### Task 2: Define app package bootstrap
- Objective: create the minimal application package structure required to wire FastAPI startup and imports.
- Files to Create: `app/__init__.py`, `app/main.py`.
- Files to Modify: `run.py`.
- Dependencies: Task 1.
- Acceptance Criteria: the app package is importable and the main application object is defined in the expected module.
- Related Requirement: requirements 1, 2, 10.
- Related TSD Section: Sections 6, 10, 16.

## Database

### Task 3: Create schema initialization scripts
- Objective: define the MySQL schema for rooms, recurring series, and bookings.
- Files to Create: `database/schema.sql`.
- Files to Modify: `README.md`.
- Dependencies: Task 1.
- Acceptance Criteria: schema script defines the required tables, foreign keys, indexes, and constraints described in the TSD.
- Related Requirement: requirements 4.1 through 4.5, BR-1 through BR-7.
- Related TSD Section: Sections 7, 8.

### Task 4: Create seed data script
- Objective: seed representative room, booking, and recurring-series data for local development.
- Files to Create: `database/seed.sql`.
- Files to Modify: `README.md`.
- Dependencies: Task 3.
- Acceptance Criteria: seed data includes room listing entries, back-to-back bookings, overlapping bookings, cancellation scenarios, and DST-related samples.
- Related Requirement: requirements 4.1 through 4.5, 5.1 through 5.4, 9.
- Related TSD Section: Sections 8, 13, 15.

### Task 5: Implement database session plumbing
- Objective: provide SQLAlchemy engine and session factory access for the application.
- Files to Create: `app/database/session.py`.
- Files to Modify: `app/core/config.py`, `app/main.py`.
- Dependencies: Task 1, Task 3.
- Acceptance Criteria: services can obtain an active session from the database layer and the session factory is configured from environment variables.
- Related Requirement: requirements 7, 8.8.
- Related TSD Section: Sections 1, 9, 10.

## Models

### Task 6: Implement room ORM model
- Objective: represent rooms as a SQLAlchemy model with sequential identifiers, room name, capacity, and timezone.
- Files to Create: `app/models/room.py`, `app/models/__init__.py`.
- Files to Modify: `database/schema.sql`.
- Dependencies: Task 3.
- Acceptance Criteria: the room model matches the schema and exposes the room timezone required for recurrence behavior.
- Related Requirement: requirements BR-7, 4.5, 8.2.
- Related TSD Section: Sections 7, 10, 13.

### Task 7: Implement booking ORM model
- Objective: represent bookings with room linkage, recurring-series linkage, timestamps, and status.
- Files to Create: `app/models/booking.py`.
- Files to Modify: `database/schema.sql`.
- Dependencies: Task 6.
- Acceptance Criteria: booking model supports single bookings, recurring bookings, and cancellation state while preserving naive timestamp storage.
- Related Requirement: requirements 4.1 through 4.4, IC-1, IC-3.
- Related TSD Section: Sections 7, 10, 12, 13.

### Task 8: Implement recurring series ORM model
- Objective: represent logical recurring booking series for future cancellation and booking grouping.
- Files to Create: `app/models/recurring_series.py`.
- Files to Modify: `database/schema.sql`.
- Dependencies: Task 6, Task 7.
- Acceptance Criteria: recurring series model captures room, user, weekday, repeat-until, and wall-clock time data as specified in the TSD.
- Related Requirement: requirements 4.2, 4.4, BR-3, BR-4.
- Related TSD Section: Sections 7, 9, 12.

## Repositories

### Task 9: Implement room repository
- Objective: provide room lookup and room listing access through SQLAlchemy queries only.
- Files to Create: `app/repositories/room_repository.py`, `app/repositories/__init__.py`.
- Files to Modify: `app/models/room.py`.
- Dependencies: Task 6.
- Acceptance Criteria: repository methods query rooms without business rules and return results in the shape required by the service layer.
- Related Requirement: requirements 4.5, BR-7.
- Related TSD Section: Sections 1, 10, 12.5.

### Task 10: Implement booking repository
- Objective: provide booking insert, lookup, update, and conflict-query access.
- Files to Create: `app/repositories/booking_repository.py`.
- Files to Modify: `app/models/booking.py`.
- Dependencies: Task 7.
- Acceptance Criteria: repository can retrieve active bookings, insert bookings, and update cancellation state without owning commits or rollbacks.
- Related Requirement: requirements 4.1, 4.3, BR-1, BR-2, BR-4.
- Related TSD Section: Sections 1, 9, 11, 14.

### Task 11: Implement recurring repository
- Objective: provide recurring-series persistence and cancellation support.
- Files to Create: `app/repositories/recurring_repository.py`.
- Files to Modify: `app/models/recurring_series.py`.
- Dependencies: Task 8.
- Acceptance Criteria: repository can create recurring series and locate series-linked bookings for cancellation flows.
- Related Requirement: requirements 4.2, 4.4, BR-3, BR-4.
- Related TSD Section: Sections 1, 9, 12.

## Services

### Task 12: Implement room service
- Objective: expose room listing behavior through a service boundary.
- Files to Create: `app/services/room_service.py`, `app/services/__init__.py`.
- Files to Modify: `app/repositories/room_repository.py`.
- Dependencies: Task 9.
- Acceptance Criteria: service returns only `id`, `name`, and `capacity` for room listing and does not expose internal room fields.
- Related Requirement: requirements 4.5, IC-2.
- Related TSD Section: Sections 10.1, 12.5.

### Task 13: Implement single booking service
- Objective: create single bookings, validate room existence, validate time range, and enforce conflict rules.
- Files to Create: `app/services/booking_service.py`.
- Files to Modify: `app/repositories/booking_repository.py`, `app/core/exceptions.py`.
- Dependencies: Task 10, Task 5.
- Acceptance Criteria: service rejects invalid ranges, blocks overlapping active bookings in the same room, allows back-to-back bookings, and owns the transaction.
- Related Requirement: requirements 4.1, BR-1, BR-2, 8.6.
- Related TSD Section: Sections 9, 11, 12.1, 14.

### Task 14: Implement recurring booking service
- Objective: generate all weekly occurrences, detect conflicts for every occurrence, and create the full recurring series atomically.
- Files to Create: `app/services/recurring_service.py`.
- Files to Modify: `app/repositories/booking_repository.py`, `app/repositories/recurring_repository.py`, `app/core/timezone.py`, `app/core/exceptions.py`.
- Dependencies: Task 11, Task 13, Task 18.
- Acceptance Criteria: service follows the selected R1 behavior, generates occurrences until `repeat_until`, stores every occurrence individually, and rolls back on any conflict.
- Related Requirement: requirements 4.2, 8.1, BR-3, BR-5, BR-6, 8.7.
- Related TSD Section: Sections 5, 9, 12.2, 13, 14.

### Task 15: Implement cancellation service behavior
- Objective: cancel a single booking or future occurrences of a recurring series while preserving historical rows.
- Files to Create: none.
- Files to Modify: `app/services/booking_service.py`, `app/services/recurring_service.py`, `app/repositories/booking_repository.py`, `app/repositories/recurring_repository.py`.
- Dependencies: Task 13, Task 14.
- Acceptance Criteria: cancelling an already-cancelled booking is idempotent; future recurring bookings are cancelled only when `start_time` is in the future; past occurrences remain unchanged.
- Related Requirement: requirements 4.3, 4.4, 8.5.
- Related TSD Section: Sections 9, 10.4, 10.5, 12.3, 12.4.

## Schemas

### Task 16: Implement room schemas
- Objective: define room response schemas for the legacy room listing contract.
- Files to Create: `app/schemas/room.py`.
- Files to Modify: `app/services/room_service.py`.
- Dependencies: Task 12.
- Acceptance Criteria: schema returns only the room fields required by the integration contract.
- Related Requirement: requirements 4.5, IC-2.
- Related TSD Section: Sections 10.1, 12.5.

### Task 17: Implement booking schemas
- Objective: define request and response payloads for single booking and cancellation endpoints.
- Files to Create: `app/schemas/booking.py`, `app/schemas/common.py`, `app/schemas/__init__.py`.
- Files to Modify: `app/services/booking_service.py`.
- Dependencies: Task 13, Task 15.
- Acceptance Criteria: schemas validate naive timestamp strings, booking identifiers, status values, and response shapes for booking creation and cancellation.
- Related Requirement: requirements 4.1, 4.3, IC-1.
- Related TSD Section: Sections 10.2, 10.4, 11, 13.

### Task 18: Implement recurring booking schemas
- Objective: define request and response payloads for recurring booking creation and recurring cancellation endpoints.
- Files to Create: `app/schemas/booking.py`, `app/schemas/common.py` if shared models are needed.
- Files to Modify: `app/services/recurring_service.py`.
- Dependencies: Task 14, Task 15.
- Acceptance Criteria: schemas support first-occurrence booking data, repeat-until input, series response fields, and recurring cancellation response fields.
- Related Requirement: requirements 4.2, 4.4, BR-3, BR-4, IC-1.
- Related TSD Section: Sections 10.3, 10.5, 12.2, 12.4, 13.

## API Routes

### Task 19: Implement room API route
- Objective: expose `GET /rooms` with the legacy response shape.
- Files to Create: `app/api/rooms.py`, `app/api/deps.py`, `app/api/__init__.py`.
- Files to Modify: `app/main.py`.
- Dependencies: Task 12, Task 16.
- Acceptance Criteria: endpoint returns the exact array shape required by existing integrations and does not expose timezone information.
- Related Requirement: requirements 4.5, IC-2, IC-3.
- Related TSD Section: Sections 10.1, 12.5.

### Task 20: Implement single booking API routes
- Objective: expose `POST /bookings` and `DELETE /bookings/{booking_id}`.
- Files to Create: `app/api/bookings.py`.
- Files to Modify: `app/main.py`, `app/core/exceptions.py`.
- Dependencies: Task 13, Task 17.
- Acceptance Criteria: endpoint returns the status codes and response bodies defined in the TSD; validation and domain errors are mapped to the correct HTTP outcomes.
- Related Requirement: requirements 4.1, 4.3, BR-1, BR-2, 8.6.
- Related TSD Section: Sections 10.2, 10.4, 11, 12.1, 12.3.

### Task 21: Implement recurring booking API routes
- Objective: expose `POST /bookings/recurring` and `DELETE /bookings/recurring/{series_id}`.
- Files to Create: `app/api/bookings.py`.
- Files to Modify: `app/main.py`, `app/core/exceptions.py`.
- Dependencies: Task 14, Task 18.
- Acceptance Criteria: endpoint follows the selected R1 behavior, returns the defined response shapes, and preserves the required timestamp format.
- Related Requirement: requirements 4.2, 4.4, 8.1, 8.2, 8.3, 8.7, 8.8.
- Related TSD Section: Sections 10.3, 10.5, 5, 12.2, 12.4, 13, 14.

## Utilities

### Task 22: Implement shared helper utilities
- Objective: create only small reusable helpers needed by multiple backend modules.
- Files to Create: `app/utils/__init__.py`.
- Files to Modify: any service or API module that needs a shared helper extracted for clarity.
- Dependencies: Tasks 12 through 21.
- Acceptance Criteria: utility code is minimal, reused only where it removes duplication, and does not become a hidden business-logic layer.
- Related Requirement: requirements 7, 10.
- Related TSD Section: Sections 1, 16.

## Error Handling

### Task 23: Implement domain exception types and HTTP mapping
- Objective: map business failures to the HTTP outcomes defined in the TSD without leaking repository details.
- Files to Create: `app/core/exceptions.py`.
- Files to Modify: `app/api/bookings.py`, `app/api/rooms.py`, `app/main.py`.
- Dependencies: Task 13, Task 14, Task 19, Task 20, Task 21.
- Acceptance Criteria: not-found, validation, conflict, and unexpected errors are mapped consistently; API layers stay thin.
- Related Requirement: requirements 4.1 through 4.5, IC-1, IC-3, 9.
- Related TSD Section: Sections 10, 11, 12, 16.

## Timezone

### Task 24: Implement room-local timezone helpers
- Objective: convert recurring booking inputs into deterministic room-local dates and preserve wall-clock time across DST.
- Files to Create: `app/core/timezone.py`.
- Files to Modify: `app/services/recurring_service.py`, `app/services/booking_service.py`.
- Dependencies: Task 6, Task 8.
- Acceptance Criteria: recurrence generation uses the room timezone, produces weekly occurrences, respects `repeat_until`, and keeps the intended local time unchanged across DST transitions.
- Related Requirement: requirements 8.2, 8.3, BR-5, BR-6.
- Related TSD Section: Section 13.

## Documentation

### Task 25: Document runtime and setup behavior
- Objective: provide the backend implementation setup instructions and operational notes required for final submission.
- Files to Create: none.
- Files to Modify: `README.md`, `docs/DECISIONS.md`.
- Dependencies: Tasks 1 through 24.
- Acceptance Criteria: setup instructions match the actual implementation; the recurring-conflict decision is documented consistently; no extra architecture or new assumptions are introduced.
- Related Requirement: requirements 1, 2, 8, 10.
- Related TSD Section: Sections 4, 5, 16, 18.

## Coding Standards

- Use type hints on public functions, service methods, repository methods, and data-transfer boundaries.
- Keep code clean and direct; prefer small functions with a single responsibility.
- Follow SOLID principles where they apply without adding unnecessary abstraction.
- Keep business logic in services only.
- Keep SQL and query concerns inside repositories only.
- Keep HTTP concerns inside API route modules only.
- Avoid duplicated business logic across services, repositories, and routes.
- Keep timezone handling isolated in timezone utilities and service coordination code.

## Validation Checklist

Before marking any backend task complete, verify all of the following:

- The requirement is implemented.
- The TSD behavior is followed.
- The architecture is unchanged.
- No duplicated logic was introduced.
- No unnecessary files were added.

