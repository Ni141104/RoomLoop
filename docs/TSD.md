# Technical Specification Document

**Project:** RoomLoop Booking Service  
**Version:** 1.0  
**Primary Requirements Source:** `requirements.md`  
**Additional Context:** `homeassignment.md`

This document describes **how this project will be implemented**. It does not restate business requirements from `requirements.md`. Where the assignment is ambiguous, decisions are listed explicitly under **Implementation Assumptions** — nothing is decided silently.

---

## 1. Architecture Overview

RoomLoop is a small REST API that replaces the existing booking prototype. Internal tools already consume the current API, so externally visible behaviour (timestamp format, room listing shape) must remain compatible.

### Layered Architecture

```text
Client (Facilities Dashboard, Reporting, Internal Tools)
                    │
                    ▼ HTTP
            ┌───────────────┐
            │   API Layer   │  Routes, Pydantic validation, HTTP status codes
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │ Service Layer │  Business rules, conflict checks, recurrence generation
            │               │  **Owns transactions (BEGIN / COMMIT / ROLLBACK)**
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │  Repository   │  SQLAlchemy queries only — no business logic
            │     Layer     │  Never commits or rolls back
            └───────┬───────┘
                    │
                    ▼
            ┌───────────────┐
            │     MySQL     │  schema.sql + seed.sql
            └───────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Must NOT do |
|---|---|---|
| **API** | Parse HTTP requests, validate schema, call services, return responses | Business logic, direct DB access, transactions |
| **Service** | Validate business rules, orchestrate operations, open/commit/rollback transactions | HTTP concerns |
| **Repository** | Read/write data via SQLAlchemy | Business decisions, commit/rollback |

### Transaction Ownership

- The **Service Layer** opens a database session scope and owns `commit()` and `rollback()`.
- Repositories receive an active session and execute queries within that scope.
- Repositories never call `commit()` or `rollback()`.

This keeps booking creation, recurring generation, and cancellation atomic where required by the requirements.

---

## 2. Technology Stack

| Component | Choice | Source |
|---|---|---|
| Language | Python 3.11+ | Assignment ground rules |
| Web framework | FastAPI | Implementation decision (AD-001) |
| Database | MySQL Community Server 8.x | Implementation decision (AD-002) |
| ORM | SQLAlchemy | Implementation decision (AD-004) |
| Validation | Pydantic | FastAPI standard pairing |
| Timezone | Python `zoneinfo` (stdlib) | Required for BR-5, BR-6 |
| Testing | pytest | Assignment expectation |
| DB tooling | MySQL Workbench | Local development |
| DB init | `schema.sql`, `seed.sql` | Implementation decision |

**Not used in this project:** PostgreSQL, Alembic, Docker, Redis, Kubernetes, message queues.

---

## 3. Architecture Decisions

| ID | Decision | Reason |
|---|---|---|
| **AD-001** | FastAPI | Simple REST framework with automatic request validation and OpenAPI docs. Fits a small internal service. |
| **AD-002** | MySQL Community Server 8.x | Free, straightforward local setup, easy for a reviewer to reproduce with MySQL Workbench. |
| **AD-003** | Layered architecture (API → Service → Repository) | Clear separation of concerns; business logic stays testable without HTTP. |
| **AD-004** | SQLAlchemy | Keeps SQL out of business logic; works well with MySQL and pytest. |
| **AD-005** | Naive timestamp storage | Required by IC-1 — reporting parses `2026-07-02T09:00:00` with no offset. |
| **AD-006** | Room timezone on `rooms` table | Supports wall-clock recurrence and DST correctness (BR-5, BR-6). See IA-001. |
| **AD-007** | REST API over CLI | Although the assignment allows either REST or CLI, REST is selected because the existing system already exposes APIs consumed by internal tools. This aligns naturally with the provided integration constraints. |

---

## 4. Implementation Assumptions

These areas are **not fully defined** in `requirements.md` or the assignment. Each assumption is documented before coding. All should be validated with Product before production deployment.

### IA-001 — Timezone ownership

**Assumption:** Booking times are interpreted in the **room's office timezone** (stored on the room record).

**Reason:** `requirements.md` §8.2 notes this is a room booking system, not a user calendar. Physical rooms belong to an office (Berlin or Denver per the assignment).

**Impact:** Recurrence generation and "future vs past" cancellation use the room timezone internally via `zoneinfo`, then store naive local timestamps.

---

### IA-002 — Weekly repeat rule

**Assumption:** A recurring booking repeats on the **same weekday as the `start_time` of the first occurrence**, once per week. Multiple weekdays (e.g. Monday and Wednesday) are **not** supported.

**Reason:** Assignment mentions a weekly repeat rule and examples like "every Monday". `requirements.md` §8.3 flags multi-weekday support as undefined.

**Impact:** `POST /bookings/recurring` does not accept a separate weekday list; weekday is derived from `start_time`.

#### Weekly repeat rule interpretation

The assignment lists "weekly repeat rule" as an input.

This implementation interprets that rule as:

"Repeat every week on the weekday of the first occurrence."

No additional request field is introduced.

If Product later supports multiple weekdays or RFC recurrence rules, the request contract can be extended without changing the core architecture.

---

### IA-003 — Past bookings

**Status**

The assignment does not specify whether bookings in the past should be accepted or rejected (`requirements.md` §8.6).

**Implementation**

The current implementation does not perform validation that a booking must be in the future.

**Reason**

No such validation is defined in the assignment.

**PM Question**

Should bookings for past dates be rejected before production release?

---

### IA-004 — Maximum recurrence length

**Status**

The assignment does not define a maximum recurrence length (`requirements.md` §8.7).

**Implementation**

Recurring bookings are generated until the provided `repeat_until` date.

No application-level recurrence limit is introduced.

**Reason**

`repeat_until` already provides a natural boundary for recurrence generation.

**Future consideration**

If Product later identifies performance concerns for extremely large recurring series, a configurable limit may be introduced. Such a limit is intentionally not part of this implementation because it is not defined by the assignment.

---

### IA-005 — Concurrent booking requests

**Status**

Behaviour for simultaneous booking requests is not defined by the assignment (`requirements.md` §8.8).

**Implementation**

The service performs conflict checking and booking creation within a single database transaction.

No additional locking strategy is introduced.

**Reason**

This provides sufficient consistency for the assignment scope (~200 employees) while keeping the implementation simple.

**Future consideration**

If concurrent booking behaviour becomes a product requirement, explicit locking strategies can be introduced without changing the overall architecture.

---

### IA-006 — Cancellation of already-cancelled booking

**Assumption:** Cancelling an already-cancelled booking returns **success** (idempotent), not an error.

**Reason:** `requirements.md` §9 — "Should not fail unexpectedly."

**Impact:** `DELETE /bookings/{id}` returns `200` if booking exists, even if already cancelled.

---

### IA-007 — REST API paths (except rooms)

**Assumption:** Booking endpoints use the paths documented in Section 10 (REST API Design). Only `GET /rooms` is explicitly named in the assignment (C2).

**Reason:** Assignment requires REST or CLI; this implementation chooses REST. Exact booking URLs are not specified in the assignment.

**Impact:** Paths listed in Section 10 are implementation choices, not legacy contract requirements (unlike room listing shape and timestamps).

---

## 5. R1 vs R2 — Recurring Booking Conflicts

The assignment defines two conflicting PM requirements (`requirements.md` §8.1):

| Rule | Behaviour |
|---|---|
| **R1** | All-or-nothing: if the full recurring series cannot be created, nothing is saved. |
| **R2** | Skip conflicting occurrences; create the rest. |

The assignment contains two contradictory requirements. These cannot both be true. **This implementation follows R1.**

**Reason:** R1 gives deterministic transactional behaviour — the database never holds a partially created series.

**Tradeoff:** Users cannot book "most" of a series when one slot conflicts; they must resolve conflicts first or choose different times.

**R2 is also a valid interpretation.** It would improve user experience by allowing partial success.

**If Product confirms R2:** Only `RecurringBookingService` (and its tests) need to change — skip conflicting occurrences during generation, insert the rest, return a response listing skipped dates. Schema, cancellation flow, and single booking flow would remain unchanged. Recurring logic is intentionally isolated for this reason.

This question should appear in `DECISIONS.md` as the primary PM clarification.

---

## 6. Project Structure

```text
roomloop/
├── app/
│   ├── main.py                 # FastAPI app, route registration
│   ├── api/
│   │   ├── deps.py             # DB session dependency
│   │   ├── bookings.py         # Booking routes
│   │   └── rooms.py            # GET /rooms
│   ├── core/
│   │   ├── config.py           # DB URL, max recurrence cap
│   │   ├── exceptions.py       # Domain errors → HTTP mapping
│   │   └── timezone.py         # zoneinfo recurrence helpers
│   ├── database/
│   │   └── session.py          # Engine, session factory
│   ├── models/                 # SQLAlchemy models
│   │   ├── room.py
│   │   ├── booking.py
│   │   └── recurring_series.py
│   ├── schemas/                # Pydantic request/response models
│   ├── repositories/
│   │   ├── room_repository.py
│   │   ├── booking_repository.py
│   │   └── recurring_repository.py
│   └── services/
│       ├── booking_service.py
│       ├── recurring_service.py
│       └── room_service.py
├── database/
│   ├── schema.sql              # Table definitions
│   └── seed.sql                # Sample data
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── README.md
└── DECISIONS.md
```

---

## 7. Database Design

### Design philosophy

Only tables and columns needed for the assignment functionality. No separate audit/history tables. No soft-delete metadata beyond a `status` column required for cancellation.

### Why SQL

Bookings reference rooms, overlap must be queried per room, recurring cancellation updates many related rows, and reporting reads persisted timestamps. Relational storage fits these requirements directly.

### Entity Relationship Diagram

```text
┌─────────────────┐       ┌─────────────────────┐
│     rooms       │       │  recurring_series   │
├─────────────────┤       ├─────────────────────┤
│ id          PK  │◄──┐   │ id              PK  │
│ name            │   │   │ room_id         FK  │──┐
│ capacity        │   │   │ user                │  │
│ timezone        │   │   │ repeat_weekday      │  │
└─────────────────┘   │   │ repeat_until (DATE) │  │
        ▲             │   │ start_time (TIME)   │  │
        │             │   │ end_time (TIME)     │  │
        │             │   └──────────┬──────────┘  │
        │             │              │ 1          │
        │             │              ▼ *         │
        │             │   ┌─────────────────────┐│
        └─────────────┼───│     bookings        │◄┘
                      │   ├─────────────────────┤
                      └───│ id              PK  │
                          │ room_id         FK  │
                          │ recurring_series_id │  (NULL = single booking)
                          │ user                │
                          │ start_time (DATETIME)│  naive local
                          │ end_time (DATETIME)  │  naive local
                          │ status              │  active | cancelled
                          └─────────────────────┘
```

### Table: `rooms`

| Column | Type | Notes |
|---|---|---|
| `id` | INT, PK | Sequential IDs (BR-7) |
| `name` | VARCHAR(100), NOT NULL | e.g. "Aurora" |
| `capacity` | INT, NOT NULL | Matches IC-2 response |
| `timezone` | VARCHAR(50), NOT NULL | IANA name, e.g. `Europe/Berlin`, `America/Denver` |

### Table: `recurring_series`

| Column | Type | Notes |
|---|---|---|
| `id` | INT, PK, AUTO_INCREMENT | Series identifier |
| `room_id` | INT, FK → rooms.id | |
| `user` | VARCHAR(255), NOT NULL | |
| `repeat_weekday` | TINYINT, NOT NULL | 0=Monday … 6=Sunday (ISO) |
| `repeat_until` | DATE, NOT NULL | Last calendar date (inclusive) |
| `start_time` | TIME, NOT NULL | Wall-clock start (BR-5) |
| `end_time` | TIME, NOT NULL | Wall-clock end |

Supports `requirements.md` §7: logical series grouping for future cancellation.

### Table: `bookings`

| Column | Type | Notes |
|---|---|---|
| `id` | INT, PK, AUTO_INCREMENT | |
| `room_id` | INT, FK → rooms.id | |
| `recurring_series_id` | INT, NULL, FK → recurring_series.id | NULL for single bookings |
| `user` | VARCHAR(255), NOT NULL | |
| `start_time` | DATETIME, NOT NULL | Naive local (IC-1) |
| `end_time` | DATETIME, NOT NULL | Naive local (IC-1) |
| `status` | VARCHAR(20), NOT NULL, DEFAULT 'active' | `active` or `cancelled` |

**Constraints:**

- `start_time < end_time` (CHECK or enforced in service — MySQL 8 CHECK supported)
- `status IN ('active', 'cancelled')`

**Indexes:**

- `(room_id, start_time, end_time)` — conflict queries
- `(recurring_series_id)` — series cancellation lookup

---

## 8. Database Setup

Database is initialized with SQL scripts, not migration tooling.

### `database/schema.sql`

Creates:

- Database (if not exists)
- `rooms`, `recurring_series`, `bookings`
- Foreign keys, indexes, and check constraints listed in Section 7

### `database/seed.sql`

Inserts realistic sample data to exercise risky behaviour:

| Data | Purpose |
|---|---|
| Berlin room (`Europe/Berlin`) | DST / CET-CEST testing |
| Denver room (`America/Denver`) | DST / MST-MDT testing (Office Manager complaint) |
| Additional rooms | Match IC-2 sample shape (`id`, `name`, `capacity`) |
| Back-to-back bookings | BR-2 — adjacent slots, same room |
| Overlapping pair | Conflict detection demo |
| Single booking | Baseline |
| Recurring series | Multiple generated occurrences |
| Past + future instances in one series | BR-4 cancellation test |
| Occurrences spanning DST boundary | BR-5, BR-6 |

README will document: create database → run `schema.sql` → run `seed.sql` → start API.

---

## 9. Transaction Strategy

| Operation | Transaction | Behaviour |
|---|---|---|
| Create single booking | One transaction | Validate room → check conflicts → insert → commit. Conflict → rollback, 409. |
| Create recurring booking (R1) | One transaction | Generate all occurrences → check every conflict → insert series + all bookings → commit. Any conflict → rollback entire request, 409. |
| Cancel single booking | One transaction | Load booking → set `status = cancelled` → commit. |
| Cancel recurring (future) | One transaction | Load series → cancel active bookings where `start_time >= now` (room local) → commit. Past rows unchanged (BR-4). |

Repositories execute queries inside the session provided by the service. The service calls `session.commit()` on success and `session.rollback()` on failure.

---

## 10. REST API Design

No API versioning prefix. Endpoints are plain REST paths.

### 10.1 `GET /rooms`

**Source:** Assignment C2 / IC-2 — existing integration contract.

Only the following API behaviours are constrained by existing integrations:

- `GET /rooms` response structure (IC-2)
- Booking timestamp format (IC-1)

All booking creation and cancellation endpoints are part of this rebuild.

Their response bodies are implementation decisions and are intentionally designed to support recurring booking management.

**Response `200`:**

```json
[
  {"id": 3, "name": "Aurora", "capacity": 8},
  {"id": 4, "name": "Basalt", "capacity": 4}
]
```

- Root JSON **array** (not wrapped).
- Fields exactly: `id`, `name`, `capacity`.
- `timezone` is **not** exposed (not in IC-2).
- Ordered by `id` ascending.

---

### 10.2 `POST /bookings`

**Purpose:** Create single booking (`requirements.md` §4.1).

**Request:**

| Field | Type | Required |
|---|---|---|
| `room_id` | integer | yes |
| `user` | string | yes |
| `start_time` | string | yes — `YYYY-MM-DDTHH:MM:SS`, no offset |
| `end_time` | string | yes — same format |

**Response `201`:** Booking object with `id`, `room_id`, `user`, `start_time`, `end_time`, `status`, `recurring_series_id` (null).

| Status | Condition |
|---|---|
| 201 | Created |
| 400 | Invalid time range |
| 404 | Room not found |
| 409 | Conflict (BR-1) |
| 422 | Invalid request shape/format |

---

### 10.3 `POST /bookings/recurring`

**Purpose:** Create recurring booking (`requirements.md` §4.2). Path is an implementation choice (IA-007).

**Request:**

| Field | Type | Required |
|---|---|---|
| `room_id` | integer | yes |
| `user` | string | yes |
| `start_time` | string | yes — first occurrence; defines weekday and wall-clock time |
| `end_time` | string | yes |
| `repeat_until` | string | yes — `YYYY-MM-DD` |

**Response `201`:** Series id, count of occurrences created, list of booking objects.

| Status | Condition |
|---|---|
| 201 | Full series created (R1) |
| 400 | Invalid range or `repeat_until` before first occurrence |
| 404 | Room not found |
| 409 | Any occurrence conflicts — nothing saved (R1) |
| 422 | Invalid request |

---

### 10.4 `DELETE /bookings/{booking_id}`

**Purpose:** Cancel single booking (`requirements.md` §4.3).

**Response `200`:** `{ "id", "status": "cancelled" }`

| Status | Condition |
|---|---|
| 200 | Cancelled (or already cancelled — IA-006) |
| 404 | Booking not found |

---

### 10.5 `DELETE /bookings/recurring/{series_id}`

**Purpose:** Cancel future occurrences of a series (`requirements.md` §4.4).

**Response `200`:** `{ "recurring_series_id", "cancelled_count", "preserved_count" }`

- **Future:** `start_time >= current datetime in room timezone` (as naive local).
- **Preserved:** past active occurrences unchanged.

| Status | Condition |
|---|---|
| 200 | Success |
| 404 | Series not found |

---

### Error response format

```json
{
  "error": {
    "code": "BOOKING_CONFLICT",
    "message": "Human-readable description"
  }
}
```

| HTTP | Code | When |
|---|---|---|
| 400 | `BAD_REQUEST` | Business validation failure |
| 404 | `NOT_FOUND` | Room, booking, or series missing |
| 409 | `BOOKING_CONFLICT` | Overlapping active booking |
| 422 | `VALIDATION_ERROR` | Pydantic / format errors |
| 500 | `INTERNAL_ERROR` | Unexpected failure |

---

## 11. Validation Rules

| Rule | Source | HTTP |
|---|---|---|
| Room exists | §4.1 | 404 |
| `start_time < end_time` (strict) | §4.1, §9 | 400 |
| `start_time >= end_time` | §4.1, §9 | 400 |
| Overlap in same room by active booking | BR-1 | 409 |
| Back-to-back allowed | BR-2 | Allowed |
| Timestamp format without offset | IC-1 | 422 |
| `repeat_until` not before first occurrence date | §9 | 400 |
| Conflict on any recurring occurrence | §4.2 + R1 | 409, rollback all |
| Cancelled bookings do not block conflicts | §4.3, §4.4 | Allowed |

**Overlap predicate** (active bookings, same room):

```text
existing.start_time < new.end_time AND new.start_time < existing.end_time
```

Strict inequality ensures back-to-back bookings do not conflict (BR-2).
Only bookings with `status = active` participate in conflict detection. Cancelled bookings never block future bookings.

---

## 12. Business Logic

### 12.1 Create single booking

1. Validate request (Pydantic + IC-1 format).
2. Load room; 404 if missing.
3. Validate `start_time < end_time`.
4. Begin transaction.
5. Query active bookings in room for overlap.
6. If overlap → rollback → 409.
7. Insert booking (`status = active`, `recurring_series_id = NULL`).
8. Commit → return 201.

### 12.2 Create recurring booking (R1)

1. Validate request.
2. Load room and timezone.
3. Validate time range and `repeat_until`.
4. Generate exactly one occurrence every week from first date through `repeat_until` using `zoneinfo` (Section 13).
5. Include only occurrences where `occurrence_date <= repeat_until`.
6. If `repeat_until` does not fall on the recurring weekday, generate the last occurrence on the matching weekday before `repeat_until`.
7. Begin transaction.
8. For each occurrence, check conflicts against active bookings.
9. If any conflict → rollback → 409 (nothing persisted).
10. Insert `recurring_series` row.
11. Insert all booking rows linked to series.
12. Commit → return 201 with occurrences.

### 12.3 Cancel single booking

1. Load booking; 404 if missing.
2. If already cancelled → return 200 (IA-006).
3. Set `status = cancelled`.
4. Commit → return 200.

### 12.4 Cancel recurring series (future only)

1. Load series; 404 if missing.
2. Compute current naive local datetime in room timezone.
3. Begin transaction.
4. Update `status = cancelled` for active bookings in series where `start_time >= now`.
5. Leave past bookings unchanged (BR-4).
6. Commit → return counts.

### 12.5 List rooms

1. Query all rooms ordered by `id`.
2. Return `[{id, name, capacity}]` only (IC-2).

---

## 13. Timezone Strategy

This section addresses the most error-prone requirement (Denver bookings "an hour off" in the assignment).

### 13.1 Wall-clock recurrence (BR-5)

Recurring bookings must repeat at the same **local** hour and minute every week — e.g. every Monday at 09:00 stays 09:00 after DST changes.

**Implementation:**

1. Read room IANA timezone from `rooms.timezone`.
2. Treat request `start_time` / `end_time` as **room-local** naive datetimes (IC-1).
3. Derive weekday from first occurrence.
4. Advance week-by-week using **calendar dates in the room timezone** via `zoneinfo` — not by adding fixed 168-hour deltas.
5. Combine each date with template `TIME` values from the series.
6. Store result as naive `DATETIME` (strip timezone info for persistence).

### 13.2 Room timezone assumption (IA-001)

Each room has one timezone matching its office (Berlin → `Europe/Berlin`, Denver → `America/Denver`). All bookings in that room are interpreted in that timezone. User timezone is ignored.

### 13.3 DST handling (BR-6)

| Case | Approach |
|---|---|
| Spring forward | `zoneinfo` resolves skipped local times when building occurrences; covered by unit tests |
| Fall back | Use consistent disambiguation (`fold=0`) when constructing datetimes |
| Berlin (CET/CEST) | Same approach as Denver |

Correct behaviour is verified by generating occurrences across DST boundaries and asserting local time remains 09:00 (not UTC-shifted).

### 13.4 Why timestamps remain naive (AD-005 / IC-1)

Reporting parses `2026-07-02T09:00:00` with **no offset**. Storing and returning naive local strings preserves backward compatibility. Timezone logic runs internally during recurrence generation and cancellation reference time only.

### 13.5 Backward compatibility

- External API consumers see unchanged timestamp format.
- Room listing unchanged (timezone internal only).
- DST fix is behavioural, not format-related — addresses the Office Manager's Denver issue without breaking reporting.

---

## 14. Conflict Detection Strategy

### Single booking

One overlap query per request against active bookings in the target room. Cancelled bookings never participate in conflict detection.

### Recurring booking (R1)

Check every generated occurrence before any insert against active bookings only. One failure rejects the entire request.

### Complexity

For N occurrences and B existing bookings in a room: O(N × B) per request. Acceptable for assignment scope (BR-7 — no optimization required).

### Availability by room ID

BR-7 allows iterating rooms 1..N for availability checks. Not exposed as a separate API unless added later; conflict check per room is sufficient for create flows.

---

## 15. Testing Strategy

**Framework:** pytest

### Unit tests

- Overlap vs back-to-back (BR-1, BR-2)
- Recurrence date generation across DST (Berlin + Denver)
- repeat_until before recurring weekday
- deterministic recurrence generation
- overlapping bookings in different rooms do not conflict
- Naive timestamp serialization (no `+` or `Z` suffix)
- `repeat_until` validation

### Integration tests

- `GET /rooms` — exact IC-2 shape
- `POST /bookings` — success, 404, 409, 400
- `POST /bookings/recurring` — full series; R1 rollback on partial conflict
- `DELETE /bookings/{id}` — cancel + idempotent re-cancel
- `DELETE /bookings/recurring/{id}` — future cancelled, past preserved
- cancelled booking frees the time slot
- recurring booking where every occurrence conflicts
- recurring booking partial conflict returns full rollback (R1)
- recurring cancellation with past and future occurrences
- timestamp format never contains timezone offset
- Booking can be created in the same time slot after an existing booking has been cancelled.

### Test data

`seed.sql` plus pytest fixtures cover edge cases from `requirements.md` §9, especially DST and recurring cancellation.

---

## 16. Non-Functional Requirements

| Quality | How this design supports it |
|---|---|
| **Maintainability** | Layered structure; recurring logic isolated in `RecurringBookingService` |
| **Readability** | One service per domain area; repositories named by entity |
| **Backward compatibility** | IC-1 naive timestamps; IC-2 room response; no versioning prefix on legacy contract |
| **Transaction safety** | Service-owned transactions; R1 recurring creation is atomic |
| **Testability** | Services testable with mocked repositories; integration tests against MySQL |
| **Modularity** | R2 switch affects recurring service only (Section 5) |
| **Scalability (assignment scope)** | Single MySQL instance sufficient for ~200 employees; indexed conflict queries |

---

## 17. Future Improvements

Features outside current assignment scope (`requirements.md` §8.4, §8.5, and assignment deliverables):

- Authentication and authorization
- Booking update (edit time/room/user)
- Booking search
- Room filtering
- Recurring series editing (change end date or time)
- Notification service (e.g. Slack/email on cancel)
- Booking history / audit API
- Permanent deletion (only cancellation is defined)
- Multi-weekday recurring rules (§8.3)
- CLI alternative (assignment allows REST or CLI; this repo implements REST)

---

## 18. Requirement Traceability

| Requirement | TSD Section |
|---|---|
| §4.1 Create single booking | §10.2, §11, §12.1 |
| §4.2 Create recurring booking | §5, §10.3, §12.2, §13 |
| §4.3 Cancel single booking | §10.4, §12.3 |
| §4.4 Cancel recurring booking | §10.5, §12.4 |
| §4.5 Room listing | §10.1, §12.5 |
| BR-1 Conflict | §11, §14 |
| BR-2 Back-to-back | §11, §14 |
| BR-3 Upfront generation | §7, §12.2 |
| BR-4 Future-only cancel | §10.5, §12.4 |
| BR-5 Wall-clock | §13.1 |
| BR-6 DST | §13.3 |
| BR-7 Sequential room IDs | §7, §10.1 |
| IC-1 Timestamp format | §10, §13.4, AD-005 |
| IC-2 Room response | §10.1 |
| IC-3 Backward compatibility | §13.5, §16 |
| §8.1 R1 vs R2 | §5 |
| §8.2 Timezone ownership | §4 IA-001, §13.2 |
| §8.3 Weekly repeat | §4 IA-002 |
| §8.6 Past bookings | §4 IA-003 |
| §8.7 Max recurrence | §4 IA-004 |
| §8.8 Concurrency | §4 IA-005 |
| §9 Edge cases | §11, §15 |
| §10 Success checklist | §15, §18 |
| Assignment C1/C2 | §10.1, §13.4 |
| Assignment R3–R5 | §13, §11, §14 |
| DECISIONS.md deliverable | §4, §5 (content to mirror) |

---

## Appendix — Reviewer Quick Reference

**Stack:** Python 3.11, FastAPI, MySQL 8, SQLAlchemy, Pydantic, zoneinfo, pytest  

**Init:** `database/schema.sql` → `database/seed.sql`  

**Legacy contracts:** `GET /rooms` response shape; booking timestamps as naive ISO  

**Open PM question:** R1 (implemented) vs R2 (skip conflicts) — see Section 5 and `DECISIONS.md`

**Open PM questions:** IA-001 through IA-004 should be confirmed before production
