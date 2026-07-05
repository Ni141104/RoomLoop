# RoomLoop Execution Roadmap

This document describes the implementation journey for the RoomLoop Booking Service from an empty project to final submission. It is a planning artifact only. It does not redesign the system, change requirements, or alter the TSD.

It uses `requirements.md` and `TSD.md` as the source of truth and is intended to guide backend implementation work in a stable, low-rework order.

## 1. Implementation Overview

The implementation should be built from the bottom up: configuration first, then persistence, then domain models, then repositories, then timezone behavior, then business services, then API endpoints, then tests, then documentation.

That order is chosen to minimize rework because each layer depends on the one below it. Configuration and database plumbing must exist before any service can own transactions. Models and repositories must exist before services can enforce business rules. Timezone helpers must be available before recurring booking logic is implemented, because recurrence generation and DST handling are foundational business logic used by the service layer. Services must exist before API routes and integration tests can be finalized. Testing should follow the stable contracts but should also be developed in parallel once schemas and service behavior are clear.

The architecture remains the finalized layered design in `TSD.md`: API → Service → Repository → MySQL. No new technology, no alternate interface, and no schema redesign are introduced.

## 2. Development Phases

### Phase 1: Project Setup

- Objective: establish the project skeleton, dependency list, environment template, and application entrypoints.
- Files: `requirements.txt`, `.env.example`, `.gitignore`, `run.py`, `app/__init__.py`, `app/main.py`, `README.md`.
- Dependencies: none.
- Deliverables: importable application package, documented local setup, committed example environment file.
- Completion Criteria: project can be opened and understood as a FastAPI-based service; environment keys are documented; `.env` remains uncommitted.
- Reference to TSD: Sections 2, 3, 6, 16.
- Reference to requirements: Sections 1, 2, 7, 10.

### Phase 2: Database

- Objective: define the MySQL schema, seed data, and session plumbing.
- Files: `database/schema.sql`, `database/seed.sql`, `app/database/session.py`, `app/core/config.py`.
- Dependencies: Phase 1.
- Deliverables: database initialization scripts and session factory for application use.
- Completion Criteria: schema supports rooms, recurring series, and bookings; seed data covers the required room listing, overlap, cancellation, and DST scenarios.
- Reference to TSD: Sections 7, 8, 9, 13, 14.
- Reference to requirements: Sections 4, 5, 6, 7, 9.

### Phase 3: Models

- Objective: represent the schema as SQLAlchemy models.
- Files: `app/models/room.py`, `app/models/booking.py`, `app/models/recurring_series.py`, `app/models/__init__.py`.
- Dependencies: Phase 2.
- Deliverables: ORM mappings aligned with the finalized schema.
- Completion Criteria: models reflect all required columns, foreign keys, status values, and room timezone storage.
- Reference to TSD: Section 7.
- Reference to requirements: Sections 5, 6, 7.

### Phase 4: Repositories

- Objective: implement query-only data access for rooms, bookings, and recurring series.
- Files: `app/repositories/room_repository.py`, `app/repositories/booking_repository.py`, `app/repositories/recurring_repository.py`, `app/repositories/__init__.py`.
- Dependencies: Phase 3.
- Deliverables: repository methods for lookups, inserts, updates, and conflict queries.
- Completion Criteria: repositories contain data access only and never own commit or rollback behavior.
- Reference to TSD: Sections 1, 9, 11, 14.
- Reference to requirements: Sections 4, 5, 7.

### Phase 5: Timezone

- Objective: implement room-local recurrence generation and DST-safe date handling.
- Files: `app/core/timezone.py`.
- Dependencies: Phase 2 and Phase 3.
- Deliverables: deterministic recurrence helpers that preserve local wall-clock time.
- Completion Criteria: recurring bookings stay at the intended local time across DST changes and respect `repeat_until`.
- Reference to TSD: Section 13.
- Reference to requirements: Sections 5.3, 5.4, 8.2, 8.3, 9.

### Phase 6: Services

- Objective: implement booking rules, conflict handling, recurrence generation, and transaction ownership.
- Files: `app/services/room_service.py`, `app/services/booking_service.py`, `app/services/recurring_service.py`, `app/services/__init__.py`.
- Dependencies: Phases 4 and 5.
- Deliverables: service methods that own transactions and enforce all business rules.
- Completion Criteria: single booking, recurring booking, cancellation, and room listing behave exactly as defined in `requirements.md` and `TSD.md`.
- Reference to TSD: Sections 1, 5, 9, 12, 14.
- Reference to requirements: Sections 4, 5, 7, 8, 9.

### Phase 7: Schemas

- Objective: define Pydantic request and response contracts.
- Files: `app/schemas/booking.py`, `app/schemas/room.py`, `app/schemas/common.py`, `app/schemas/__init__.py`.
- Dependencies: Phase 3 and Phase 6.
- Deliverables: validated request and response models for all endpoints.
- Completion Criteria: booking timestamp format remains naive; room listing output remains unchanged; invalid shapes are rejected before service logic runs.
- Reference to TSD: Sections 10, 11, 13.
- Reference to requirements: Sections 4.1 through 4.5, IC-1, IC-2.

### Phase 8: API

- Objective: expose the REST endpoints and map domain outcomes to HTTP responses.
- Files: `app/api/deps.py`, `app/api/rooms.py`, `app/api/bookings.py`, `app/api/__init__.py`, `app/main.py`.
- Dependencies: Phases 6 and 7.
- Deliverables: `GET /rooms`, `POST /bookings`, `POST /bookings/recurring`, `DELETE /bookings/{booking_id}`, and `DELETE /bookings/recurring/{series_id}`.
- Completion Criteria: response bodies, status codes, and legacy contracts match `TSD.md`; API handlers remain thin.
- Reference to TSD: Section 10.
- Reference to requirements: Sections 4 and 6.

### Phase 9: Testing

- Objective: verify behavior with unit and integration coverage.
- Files: `tests/conftest.py`, `tests/unit/`, `tests/integration/`, `tests/test_data/`.
- Dependencies: Phases 2 through 8, with tests able to begin as soon as the relevant contracts are stable.
- Deliverables: deterministic fixtures, unit coverage for business rules, and integration coverage for endpoints and compatibility.
- Completion Criteria: all functional requirements, edge cases, DST behavior, and backward-compatibility constraints are covered by tests.
- Reference to TSD: Section 15.
- Reference to requirements: Sections 4, 5, 6, 8, 9, 10.

### Phase 10: Documentation

- Objective: finalize setup instructions, implementation notes, and traceability artifacts.
- Files: `README.md`, `docs/DECISIONS.md`, `docs/execution_roadmap.md`.
- Dependencies: Phases 1 through 9.
- Deliverables: clear setup/run documentation, documented assumptions and decisions, and requirement coverage mapping.
- Completion Criteria: a reviewer can trace every requirement to code and tests without reading implementation details.
- Reference to TSD: Sections 4, 5, 16, 18.
- Reference to requirements: Sections 1 through 10.

## 3. Folder Structure

The final structure should stay clean and easy to navigate:

```text
roomloop/
├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── __init__.py
│   └── main.py
├── database/
│   ├── schema.sql
│   └── seed.sql
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── conftest.py
│   └── test_data/
├── scripts/
├── docs/
│   ├── requirements.md
│   ├── TSD.md
│   ├── implementation_plan.md
│   └── DECISIONS.md
├── .env.example
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── run.py
```

This layout is intentionally modest. It is modular enough for the assignment, but it avoids extra layers or enterprise-style abstractions.

## 4. Environment Setup

`.env.example` should define the expected configuration keys without secrets:

- `APP_NAME`
- `APP_ENV`
- `HOST`
- `PORT`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `TIMEZONE_DEFAULT`

`APP_NAME` identifies the application in logs or startup output. `APP_ENV` identifies the running mode, such as local or test. `HOST` and `PORT` define the local API bind address. The `DATABASE_*` variables define how the app connects to MySQL. `TIMEZONE_DEFAULT` provides the default application timezone value used for local development and any configuration fallback described in the TSD.

`.env` belongs to the local developer or reviewer environment and should contain actual values for the same keys, including database credentials and any machine-specific host or port settings. It must not be committed because it may contain secrets and because it is intentionally environment-specific. `.env.example` should be committed because it documents the expected configuration contract without exposing secrets.

## 5. Development Order

The recommended order is:

Configuration → Database → Models → Repositories → Timezone → Services → Schemas → API → Testing → Documentation

This order minimizes rework because each step reduces uncertainty for the next. Configuration and schema definitions prevent guesswork about runtime values and database shape. Models and repositories establish stable persistence contracts. Timezone utilities must exist before recurring behavior is finalized, because recurrence is one of the most sensitive business rules. Services should be implemented before API routes so transaction ownership and business logic are already stable. Schemas then lock the HTTP contract around those services. Testing should follow as soon as the stable contracts exist, because it validates the implementation without forcing later redesigns. Documentation is last so it reflects the actual implementation rather than an assumption.

## 6. Requirement Traceability

| Requirement | Phase | Implementation Area |
|---|---|---|
| 4.1 Create single booking | Phase 6, Phase 8, Phase 9 | Booking service, booking API, single-booking integration tests |
| 4.2 Create recurring booking | Phase 5, Phase 6, Phase 8, Phase 9 | Timezone helpers, recurring service, recurring API, recurring tests |
| 4.3 Cancel single booking | Phase 6, Phase 8, Phase 9 | Booking service, cancellation API, cancellation tests |
| 4.4 Cancel recurring booking | Phase 6, Phase 8, Phase 9 | Recurring service, recurring cancellation API, cancellation tests |
| 4.5 Room listing | Phase 6, Phase 8, Phase 9 | Room service, room API, room listing tests |
| BR-1 Booking conflict | Phase 6, Phase 8, Phase 9 | Conflict checking in services and API rejection tests |
| BR-2 Back-to-back bookings | Phase 6, Phase 8, Phase 9 | Conflict predicate, back-to-back behavior tests |
| BR-3 Recurring booking generation | Phase 5, Phase 6, Phase 8, Phase 9 | Recurrence helpers and recurring creation tests |
| BR-4 Recurring cancellation | Phase 6, Phase 8, Phase 9 | Future-only cancellation logic and tests |
| BR-5 Wall clock time | Phase 5, Phase 6, Phase 9 | Room-local recurrence helpers and DST tests |
| BR-6 DST | Phase 5, Phase 6, Phase 9 | zoneinfo behavior and DST regression tests |
| BR-7 Sequential room IDs | Phase 2, Phase 8, Phase 9 | Schema ordering assumptions, room listing logic, room sequence tests |
| IC-1 Timestamp format | Phase 7, Phase 8, Phase 9 | Schemas, API serialization, timestamp format tests |
| IC-2 Room API response | Phase 7, Phase 8, Phase 9 | Room schema, room API, room response tests |
| IC-3 Backward compatibility | Phase 1, Phase 7, Phase 8, Phase 9 | Project setup, schemas, API contract, compatibility tests |
| 8.1 Recurring booking clarification | Phase 6, Phase 8, Phase 10 | Recurring conflict behavior and decision documentation |
| 8.2 Timezone ownership | Phase 5, Phase 6, Phase 9 | Timezone helpers and recurrence tests |
| 8.3 Weekly repeat rule | Phase 5, Phase 6, Phase 9 | Weekly recurrence generation and repeat rule tests |
| 8.4 Booking updates | Phase 10 | Deferred as outside current scope |
| 8.5 Booking deletion | Phase 6, Phase 8, Phase 9 | Cancellation flows and tests |
| 8.6 Past bookings | Phase 7, Phase 8, Phase 9 | Validation rules and past-booking tests |
| 8.7 Maximum recurrence duration | Phase 5, Phase 6, Phase 9 | Recurrence generation behavior and no-cap tests |
| 8.8 Concurrent booking requests | Phase 5, Phase 6, Phase 9 | Transaction-owned conflict checks and concurrency tests |
| 9 Edge cases | Phase 8, Phase 9 | Booking validation, recurrence boundaries, cancellation cases |
| 10 Success checklist | Phase 9, Phase 10 | Test coverage and final documentation review |
