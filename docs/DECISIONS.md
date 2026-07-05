# RoomLoop Engineering Decisions

## Purpose

This document records the engineering decisions made during the implementation of RoomLoop.

The assignment intentionally leaves several implementation details unspecified. Rather than introducing undocumented behaviour, every ambiguity was resolved through explicit design decisions while preserving the existing API contracts described in the Technical Solution Document (TSD) and the project requirements.

---

# Guiding Principles

This document complements the Technical Solution Document (TSD) and the Requirements specification. Every engineering decision recorded here was evaluated against the following principles:

- Preserve all documented functional requirements.
- Preserve backward compatibility unless explicitly permitted.
- Resolve ambiguities without introducing undocumented behaviour.
- Keep business logic deterministic and testable.
- Separate concerns across architectural layers.
- Prefer maintainability and correctness over premature optimization.

When the requirements or TSD did not explicitly prescribe an implementation, the chosen approach is documented here together with the rationale.

---

# Ambiguities Identified

The assignment intentionally leaves several implementation details open to interpretation. The following table summarizes the major ambiguities encountered during implementation and the corresponding engineering decisions.

| Requirement Area     | Ambiguity                                            | Selected Decision                                 |
|---------------------|------------------------------------------------------|---------------------------------------------------|
| Booking overlap     | Overlap predicate not formally defined               | Standard interval-overlap algorithm               |
| Recurring conflicts | Partial success behaviour unspecified                | R1 (All-or-Nothing)                               |
| Transaction ownership | Layer responsible for commit/rollback unspecified  | Service layer owns transactions                   |
| Timezone ownership  | User timezone vs Room timezone                       | Room owns scheduling timezone                     |
| DST handling        | Behaviour across DST transitions unspecified         | Preserve room wall-clock time                     |
| Timestamp representation | Public API timezone representation unspecified  | Naive ISO timestamps for backward compatibility   |
| API routes          | Whether to version or prefix new routes              | Preserve existing route naming convention         |
| Cancellation        | Behaviour for historical recurring bookings unspecified | Cancel future occurrences only                 |

---

This document complements the Technical Solution Document (TSD) and the Requirements specification. Every engineering decision recorded here was evaluated against the following principles:

- Preserve all documented functional requirements.
- Preserve backward compatibility unless explicitly permitted.
- Resolve ambiguities without introducing undocumented behaviour.
- Keep business logic deterministic and testable.
- Separate concerns across architectural layers.
- Prefer maintainability and correctness over premature optimization.

When the requirements or TSD did not explicitly prescribe an implementation, the chosen approach is documented here together with the rationale.

---

# Decision 1 — Architecture

## Problem

The assignment does not prescribe an application architecture.

## Decision

A layered architecture was selected:

```
API
    ↓
Services
    ↓
Repositories
    ↓
Database
```

Supporting layers:

```
Schemas
Core
Database
Models
```

## Reasoning

This separation provides:

- Single Responsibility Principle
- Easier testing
- Better maintainability
- Clear ownership of business logic
- No SQL inside API routes
- No HTTP concerns inside repositories

Business rules exist only inside the Service layer.

### Implementation Outcome

The final implementation follows a strict separation of concerns:

- API layer handles HTTP requests and responses.
- Service layer contains all business rules.
- Repository layer performs persistence operations only.
- Models represent database entities.
- Schemas define external API contracts.
- Core contains configuration, shared utilities and exception definitions.

---

---

# Decision 2 — Repository Responsibilities

## Problem

Repositories often become mixed with business logic.

## Decision

Repositories only perform persistence operations.

Repositories:

- query data
- insert rows
- update rows
- return models

Repositories never:

- commit transactions
- rollback transactions
- raise HTTP exceptions
- perform validation
- implement booking rules

## Reasoning

Keeping repositories persistence-only makes them reusable and prevents duplication of business rules.

---

---

# Decision 3 — Dependency Injection Strategy

## Problem

Database session lifecycle should remain consistent across every request while avoiding tight coupling between API routes and persistence.

## Decision

FastAPI dependency injection is used to inject a database session into every request through `Depends(get_db)`.

## Reasoning

This provides:

- consistent session lifecycle
- simplified testing
- loose coupling
- easier mocking during unit tests
- centralized session management

---

# Decision 4 — Transaction Ownership

## Problem

The assignment does not define transaction ownership.

## Decision

The Service layer owns every transaction.

Service responsibilities:

- validation
- business rules
- commit
- rollback

Repository responsibilities:

- execute queries only

## Reasoning

A single transaction may involve multiple repositories.

Keeping transactions in services guarantees atomic operations.

---

---

# Decision 5 — Booking Conflict Rule

## Ambiguity

The assignment specifies that overlapping bookings must be rejected but does not formally define overlap.

### Requirement Alignment

This decision implements the conflict detection behaviour required by the booking requirements while formalizing the overlap predicate that was left unspecified in the assignment.

## Decision

Bookings conflict only when:

```
existing.start < new.end
AND
existing.end > new.start
```

Back-to-back bookings are allowed.

Example:

```
09:00–10:00
10:00–11:00
```

No conflict.

Example:

```
09:00–10:00
09:30–10:30
```

Conflict.

## Reasoning

This is the standard interval-overlap algorithm and matches common calendar systems.

---

---

# Decision 6 — Recurring Booking Strategy

## Ambiguity

The assignment does not specify whether recurring bookings should be generated lazily or stored immediately.

## Decision

All recurring occurrences are generated during creation.

Every occurrence is inserted into the database immediately.

## Reasoning

Advantages:

- conflict detection becomes deterministic
- cancellation becomes straightforward
- reporting requires no runtime expansion
- database remains the single source of truth

---

---

# Decision 7 — Recurring Conflict Behaviour (R1)

## Ambiguity

The assignment does not define behaviour when one occurrence conflicts.

### Requirement Alignment

The requirements specify that conflicting recurring bookings must not be accepted but do not define partial-success behaviour. The implementation therefore adopts an all-or-nothing transactional strategy.

## Decision

R1 (All-or-Nothing) was selected.

If any generated occurrence conflicts:

- the request fails
- no recurring series is created
- no bookings are stored

## Reasoning

Partial recurring bookings are difficult for users to reason about.

Atomic creation keeps behaviour predictable and simplifies rollback.

---

---

# Decision 8 — Cancellation Behaviour

## Ambiguity

The assignment specifies recurring cancellation but does not define historical behaviour.

## Decision

Cancelling a recurring booking only affects future active occurrences.

Past occurrences remain unchanged.

Already-cancelled bookings remain cancelled.

Cancellation is idempotent.

## Reasoning

Historical bookings represent completed events and should never be modified.

---

---

# Decision 9 — Timezone Ownership

## Ambiguity

The assignment mentions timezones but does not specify ownership.

### Requirement Alignment

This decision follows the timezone and daylight-saving requirements described in the TSD by ensuring that room-local scheduling semantics are preserved.

## Decision

Every room owns its timezone.

Users do not own booking timezones.

Recurring generation always uses:

```
Room Timezone
```

instead of

```
User Timezone
```

## Reasoning

Meeting rooms represent physical locations.

A room's wall-clock time should remain stable regardless of where users create bookings.

---

---

# Decision 10 — Daylight Saving Time (DST)

## Ambiguity

The assignment requires DST support but does not describe implementation.

## Decision

Recurring occurrences preserve wall-clock time.

Example:

```
09:00 Europe/Berlin
```

remains

```
09:00 Europe/Berlin
```

before and after DST transitions.

The UTC offset changes automatically.

## Reasoning

Users schedule meetings using local time rather than UTC offsets.

---

---

# Decision 11 — Timestamp Storage

## Ambiguity

Existing integrations expect naive timestamps.

## Decision

The public API continues returning naive ISO timestamps.

Format:

```
YYYY-MM-DDTHH:MM:SS
```

Timezone offsets are never exposed.

## Reasoning

Changing timestamp formats would break backward compatibility.

Timezone conversion remains an internal implementation detail.

---

---

# Decision 12 — API Compatibility

## Problem

Existing consumers already depend on the current API.

## Decision

Existing endpoints remain unchanged.

```
GET    /rooms

POST   /bookings

POST   /bookings/recurring

DELETE /bookings/{id}

DELETE /bookings/recurring/{series_id}
```

No `/api` prefix was introduced.

## Reasoning

Backward compatibility is preserved.

---

---

# Decision 13 — API Route Naming Convention

## Ambiguity

The assignment extends an existing system and explicitly requires backward compatibility, but it does not prescribe whether new routes should be versioned or prefixed.

## Decision

The existing route naming convention is preserved.

The implementation intentionally keeps the original endpoints:

```
GET    /rooms
POST   /bookings
POST   /bookings/recurring
DELETE /bookings/{id}
DELETE /bookings/recurring/{series_id}
```

The API does not introduce:

- an `/api` prefix
- versioned routes such as `/v1`
- renamed resources
- modified request or response contracts

The response contract is also preserved. Existing endpoints continue returning the same public fields and timestamp format expected by existing clients. Internal database attributes, room timezone information and implementation-specific details are intentionally not exposed.

## Reasoning

The TSD identifies backward compatibility as a non-functional requirement. Existing clients should continue working without any changes after the recurring-booking functionality is introduced. Preserving the route naming convention minimizes integration risk and avoids unnecessary breaking changes.

---

---

# Decision 14 — Validation Strategy

## Decision

Validation occurs in multiple layers.

### Pydantic

- request validation
- datatype validation
- response validation

### Services

- business validation
- booking rules
- conflict detection

### Database

- foreign keys
- indexes
- integrity constraints

## Reasoning

Each layer validates only what it owns.

---

# Decision 15 — API Schema Separation

## Problem

Database models should not be exposed directly through the API.

## Decision

SQLAlchemy models and Pydantic schemas are intentionally separated.

SQLAlchemy models represent persistence.

Pydantic schemas represent API contracts.

## Reasoning

This separation:

- protects internal implementation details
- enables independent API evolution
- performs request and response validation
- prevents accidental exposure of database fields

---

---

# Decision 16 — Database Design

## Decision

Three primary tables were implemented.

```
rooms

bookings

recurring_series
```

Recurring bookings reference their owning series.

Bookings remain individual rows.

## Reasoning

This enables:

- efficient conflict detection
- simple cancellation
- reporting
- indexing

---

---

# Decision 17 — Error Handling

## Decision

Domain exceptions are separated from HTTP concerns.

Services raise domain-specific exceptions.

The API layer maps them to HTTP responses.

## Reasoning

Business logic remains framework independent.

---

# Decision 18 — Domain Exception Strategy

## Decision

Business logic raises domain-specific exceptions rather than framework-specific exceptions.

Examples include:

- RoomNotFoundError
- BookingConflictError
- InvalidTimeRangeError
- RecurringSeriesNotFoundError

The API layer is responsible for translating domain exceptions into HTTP responses.

## Reasoning

This keeps business logic framework independent, reusable and easier to test.

---

---

# Decision 19 — Testing Strategy

## Decision

Testing follows the project architecture.

```
Configuration

↓

Database

↓

Models

↓

Repositories

↓

Schemas

↓

Services

↓

API

↓

Documentation

↓

Integration
```

Each layer is tested independently.

Business rules are verified primarily in the Service layer.

Repository tests verify persistence behaviour.

API tests verify routing, dependency injection, validation and serialization.

Integration tests verify complete end-to-end workflows without duplicating lower-level business rule tests.

## Reasoning

Avoids duplicated tests while maintaining high coverage.

---

---

# Decision 20 — Development Workflow

## Decision

A Makefile was introduced to standardize development.

Supported commands include:

```
make setup

make db-init

make run

make test

make clean
```

## Reasoning

Developers can bootstrap the project consistently with a single command.

The Makefile provides a single, consistent developer workflow for environment setup, database initialization, application execution and automated testing, reducing onboarding effort and ensuring repeatable execution across development environments.

---

# Summary

The implementation prioritizes:

- Clear separation of concerns
- Deterministic business behaviour
- Backward compatibility
- Maintainable architecture
- Atomic recurring operations
- Room-local timezone correctness
- Comprehensive automated testing

All implementation decisions were made by cross-referencing the assignment requirements, the Technical Solution Document (TSD), and the identified ambiguities. Whenever the specification did not prescribe an exact implementation, the selected approach prioritizes correctness, deterministic behaviour, maintainability, and backward compatibility while remaining consistent with the documented system design.