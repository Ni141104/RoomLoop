# AI Assisted Development

## Purpose

This project was developed using an AI-assisted software engineering workflow.

AI was used as an implementation accelerator rather than an autonomous developer. Every AI-generated artifact was manually reviewed, validated against the assignment requirements and the Technical Solution Document (TSD), and refined before becoming part of the final implementation.

The objective was not simply to generate code, but to demonstrate engineering judgment while using AI as a collaborative development tool.

---

# Development Workflow

The implementation followed the workflow below throughout every milestone.

```
Requirement Analysis
        ↓
Technical Solution Design
        ↓
Prompt Engineering
        ↓
AI Generated Implementation
        ↓
Manual Engineering Review
        ↓
Requirement Validation
        ↓
Testing & Verification
        ↓
Acceptance / Refinement
```

Every generated component was verified against:

- Assignment Requirements
- Technical Solution Document (TSD)
- Existing Architecture
- Backward Compatibility
- Automated Test Suite

Only after passing these validation steps was the implementation accepted.

---

# Areas Where AI Accelerated Development

AI significantly improved development speed for repetitive and boilerplate-heavy tasks, including:

- Project scaffolding
- Repository implementation
- Service boilerplate
- Pydantic schema generation
- SQLAlchemy model generation
- FastAPI route implementation
- Unit test generation
- Integration test generation
- Documentation drafting
- Makefile generation

The generated output served as a starting point and was subsequently refined through engineering review.

---

# Human Validation and Refinement

Several AI-generated suggestions required modification after comparing them with the assignment requirements and the TSD.

These examples demonstrate how engineering decisions remained human-driven throughout the project.

---

## Example 1 — Recurring Booking Conflict Strategy

### AI Initial Recommendation

The AI initially proposed an **R2 (Partial Success)** strategy.

Under this approach:

- Conflicting occurrences would be skipped.
- Remaining occurrences would still be created.
- The recurring series would be partially persisted.

### Why This Was Rejected

Although the assignment did not explicitly define the conflict strategy, this behaviour conflicted with the desired transactional semantics.

Partial creation would introduce:

- inconsistent recurring schedules
- more complex cancellation behaviour
- unpredictable user experience
- non-atomic transactions

### Final Engineering Decision

The implementation was changed to **R1 (All-or-Nothing)**.

Final behaviour:

- Every occurrence is validated.
- If any occurrence conflicts:
  - the request fails
  - no recurring series is created
  - no bookings are stored
  - the transaction is rolled back

This behaviour is documented in `DECISIONS.md` and verified through the service-layer test suite.

---

## Example 2 — API Route Naming

### AI Initial Recommendation

The initial implementation introduced REST endpoints using an `/api` prefix.

Example:

```
GET /api/rooms
POST /api/bookings
```

### Why This Was Rejected

The assignment explicitly requires backward compatibility.

Changing route names would unnecessarily break existing clients.

### Final Engineering Decision

The original route naming convention was preserved.

```
GET /rooms

POST /bookings

POST /bookings/recurring

DELETE /bookings/{id}

DELETE /bookings/recurring/{series_id}
```

---

## Example 3 — Repository Representation

The initial implementation represented recurring weekdays using string values.

Example:

```
MONDAY
```

The final implementation stores weekdays as integer values generated through:

```
determine_recurring_weekday()
```

This aligns with the database schema and improves consistency.

---

## Example 4 — SQLAlchemy Compatibility

The initial AI-generated test executed raw SQL using:

```python
session.execute("SELECT 1")
```

SQLAlchemy 2.x requires textual SQL to be wrapped using:

```python
session.execute(text("SELECT 1"))
```

The implementation was corrected accordingly.

---

## Example 5 — Local Development Configuration

The initial implementation assumed that `DATABASE_PASSWORD` must always be provided.

During integration testing, the local MySQL configuration intentionally used an empty root password.

The configuration layer was refined to support this development environment while maintaining compatibility with password-protected deployments.

---

## Example 6 — Documentation Testing Strategy

### AI Initial Recommendation

The initial testing strategy included automated tests for project documentation.

Examples included validating:

- README contents
- Decision records
- Requirement documentation

### Why This Was Rejected

These tests verify documentation rather than application behaviour.

Documentation should be reviewed by humans, whereas automated tests should focus on validating software correctness.

### Final Engineering Decision

The documentation tests were intentionally removed.

Engineering effort was redirected towards:

- API tests
- Integration tests
- End-to-end workflow validation
- Business rule verification

This resulted in a more valuable and maintainable automated test suite.

---

# Human Engineering Decisions

While AI accelerated implementation, the following decisions were made through manual engineering review:

- Layered architecture
- Repository pattern
- Transaction ownership
- Dependency injection strategy
- Conflict detection algorithm
- R1 recurring booking strategy
- Timezone ownership
- Daylight Saving Time handling
- Backward compatibility
- API route naming convention
- Validation strategy
- Exception handling
- Database integrity strategy
- Testing strategy
- Documentation strategy

---

# Validation Strategy

Every AI-generated artifact followed the validation process below before acceptance.

```
AI Suggestion
        ↓
Requirement Verification
        ↓
TSD Verification
        ↓
Architecture Review
        ↓
Manual Refinement
        ↓
Automated Testing
        ↓
Accepted Implementation
```

No AI-generated code was accepted without review.

---

# Lessons Learned

AI substantially accelerated development by reducing repetitive implementation effort and enabling rapid iteration.

However, engineering judgment remained essential throughout the project.

Examples included:

- identifying requirement ambiguities
- rejecting incorrect architectural assumptions
- preserving backward compatibility
- refining generated implementations
- correcting framework-specific issues
- selecting appropriate transactional behaviour
- improving automated test quality

The final implementation therefore represents a collaboration between AI-assisted generation and human engineering review rather than fully autonomous code generation.

---

# Project Summary

This project demonstrates the use of AI as a software engineering assistant while maintaining human ownership of all architectural and implementation decisions.

The final solution was produced through iterative refinement, continuous validation, and comprehensive automated testing to ensure consistency with the assignment requirements and the Technical Solution Document.