# Testing Agent Checklist

This checklist contains verification tasks only. It uses `requirements.md`, `TSD.md`, and `docs/execution_roadmap.md` as the source of truth.

## Unit Tests

### Test 1: Validate single-booking overlap predicate
- Purpose: verify that bookings in the same room conflict only when their time intervals overlap.
- Expected Behaviour: overlapping same-room bookings are rejected; non-overlapping same-room bookings are allowed.
- Requirement Reference: BR-1, BR-2, requirements 4.1, 9.
- TSD Reference: Sections 11, 12.1, 14.
- Pass Criteria: the overlap predicate rejects true overlaps and accepts back-to-back bookings.

### Test 2: Validate different-room isolation
- Purpose: verify that bookings in different rooms never conflict.
- Expected Behaviour: the same time slot can be booked in two different rooms.
- Requirement Reference: BR-1, BR-7.
- TSD Reference: Sections 11, 14.
- Pass Criteria: a booking created in one room does not block the same time range in another room.

### Test 3: Validate recurring date generation
- Purpose: verify deterministic weekly recurrence generation.
- Expected Behaviour: the recurrence helper generates one occurrence per week using the first occurrence weekday and the room timezone.
- Requirement Reference: BR-3, BR-5, requirements 4.2, 8.2, 8.3, 8.7.
- TSD Reference: Sections 12.2, 13.1, 13.2.
- Pass Criteria: generated occurrences are stable across repeated runs and preserve the intended weekday and local time.

### Test 4: Validate repeat_until boundary handling
- Purpose: verify that recurring bookings stop at the correct final occurrence.
- Expected Behaviour: only occurrences with `occurrence_date <= repeat_until` are generated, and if `repeat_until` falls before the recurring weekday in the final week, the final occurrence is the last matching weekday before the cutoff.
- Requirement Reference: requirements 4.2, 8.7, 9.
- TSD Reference: Sections 12.2, 13.1.
- Pass Criteria: no occurrence is generated after `repeat_until`, and the last occurrence matches the expected weekly boundary.

### Test 5: Validate cancelled-booking exclusion from conflict checks
- Purpose: verify that cancelled bookings never block new bookings.
- Expected Behaviour: only bookings with `status = active` participate in conflict detection.
- Requirement Reference: requirements 4.3, 4.4, BR-1, BR-4.
- TSD Reference: Sections 11, 12.1, 12.4, 14.
- Pass Criteria: a slot freed by cancellation can be reused without conflict.

### Test 6: Validate timestamp serialization format
- Purpose: verify that booking timestamps remain naive ISO strings.
- Expected Behaviour: timestamps are serialized without timezone offsets or timezone suffixes.
- Requirement Reference: IC-1, IC-3.
- TSD Reference: Sections 10, 13.4, 13.5.
- Pass Criteria: serialized timestamps match `YYYY-MM-DDTHH:MM:SS` and never contain `+`, `Z`, or offset data.

### Test 7: Validate room listing response shape
- Purpose: verify that room output remains stable.
- Expected Behaviour: room listing returns only `id`, `name`, and `capacity` in an array.
- Requirement Reference: requirements 4.5, IC-2, IC-3.
- TSD Reference: Sections 10.1, 12.5.
- Pass Criteria: no extra fields are returned and the response remains an array at the root.

## Integration Tests

### Test 8: Create single booking successfully
- Purpose: verify the happy path for single booking creation.
- Expected Behaviour: a valid request creates a booking and returns the configured success response.
- Requirement Reference: requirements 4.1, BR-1, BR-2.
- TSD Reference: Sections 10.2, 11, 12.1.
- Pass Criteria: the endpoint returns success, stores the booking, and preserves the requested time range.

### Test 9: Reject single booking for missing room
- Purpose: verify room existence validation.
- Expected Behaviour: requests for unknown rooms are rejected.
- Requirement Reference: requirements 4.1, 9.
- TSD Reference: Sections 11, 12.1.
- Pass Criteria: the API returns the expected not-found response and no booking is created.

### Test 10: Reject single booking for invalid time range
- Purpose: verify duration validation.
- Expected Behaviour: `start_time >= end_time` is rejected.
- Requirement Reference: requirements 4.1, BR-2, 9.
- TSD Reference: Sections 11, 12.1.
- Pass Criteria: the API returns the expected validation failure and no booking is stored.

### Test 11: Reject overlapping single booking in same room
- Purpose: verify same-room conflict handling.
- Expected Behaviour: an overlapping active booking in the same room is rejected.
- Requirement Reference: BR-1, requirements 4.1, 9.
- TSD Reference: Sections 11, 12.1, 14.
- Pass Criteria: the API returns the conflict response and the database remains unchanged.

### Test 12: Allow back-to-back single bookings
- Purpose: verify that adjacent bookings are accepted.
- Expected Behaviour: one booking ending exactly when another begins does not conflict.
- Requirement Reference: BR-2.
- TSD Reference: Sections 11, 12.1, 14.
- Pass Criteria: the second booking is created successfully.

### Test 13: Cancel a single booking
- Purpose: verify single-booking cancellation.
- Expected Behaviour: the selected booking is marked cancelled and unrelated bookings are untouched.
- Requirement Reference: requirements 4.3, BR-4, 8.5.
- TSD Reference: Sections 10.4, 12.3.
- Pass Criteria: the booking status changes to cancelled and the response matches the contract.

### Test 14: Cancel already cancelled booking idempotently
- Purpose: verify cancellation idempotency.
- Expected Behaviour: cancelling an already-cancelled booking succeeds without error.
- Requirement Reference: requirements 9, 8.5.
- TSD Reference: Sections 10.4, 12.3.
- Pass Criteria: the API returns success and the booking remains cancelled.

### Test 15: Create recurring booking successfully
- Purpose: verify the happy path for recurring booking creation.
- Expected Behaviour: all generated occurrences are stored individually and linked to one series.
- Requirement Reference: requirements 4.2, BR-3.
- TSD Reference: Sections 5, 10.3, 12.2.
- Pass Criteria: every generated occurrence is persisted and the series response is returned successfully.

### Test 16: Reject recurring booking when any occurrence conflicts
- Purpose: verify all-or-nothing recurring booking behavior.
- Expected Behaviour: if any generated occurrence conflicts, nothing is saved.
- Requirement Reference: requirements 4.2, 8.1, BR-3.
- TSD Reference: Sections 5, 10.3, 12.2, 14.
- Pass Criteria: the API returns conflict and no series or bookings are persisted.

### Test 17: Reject recurring booking when every occurrence conflicts
- Purpose: verify full-series conflict handling.
- Expected Behaviour: a request whose every occurrence conflicts is rejected atomically.
- Requirement Reference: requirements 4.2, 8.1, BR-3.
- TSD Reference: Sections 5, 10.3, 12.2, 14.
- Pass Criteria: the API returns conflict and the transaction rolls back fully.

### Test 18: Cancel recurring booking future occurrences only
- Purpose: verify future-only recurring cancellation.
- Expected Behaviour: future occurrences in the series are cancelled and past occurrences remain unchanged.
- Requirement Reference: requirements 4.4, BR-4, 8.5.
- TSD Reference: Sections 10.5, 12.4.
- Pass Criteria: only future active bookings are cancelled and the response reports the correct counts.

### Test 19: Cancel recurring booking with mixed past and future occurrences
- Purpose: verify cancellation behavior when a series straddles the current time.
- Expected Behaviour: past occurrences are preserved and future occurrences are cancelled.
- Requirement Reference: requirements 4.4, BR-4.
- TSD Reference: Sections 10.5, 12.4.
- Pass Criteria: past rows remain active or unchanged as defined, and future rows are cancelled.

### Test 20: Reuse slot after cancellation
- Purpose: verify that a cancelled booking frees the time slot.
- Expected Behaviour: a new booking can be created in the same room and same time range after cancellation.
- Requirement Reference: requirements 4.3, BR-1, BR-4, 8.5.
- TSD Reference: Sections 11, 12.3, 14.
- Pass Criteria: the new booking succeeds and the cancelled booking does not block it.

### Test 21: Preserve room response compatibility
- Purpose: verify backward compatibility of `GET /rooms`.
- Expected Behaviour: room response structure remains unchanged for dependent systems.
- Requirement Reference: IC-2, IC-3, requirements 4.5.
- TSD Reference: Sections 10.1, 12.5, 13.5.
- Pass Criteria: response shape matches the documented legacy contract exactly.

### Test 22: Preserve booking timestamp format in API responses
- Purpose: verify that API responses keep naive timestamps.
- Expected Behaviour: booking responses never include timezone offsets.
- Requirement Reference: IC-1, IC-3.
- TSD Reference: Sections 10, 13.4.
- Pass Criteria: every booking response uses the naive ISO timestamp format only.

## Validation Tests

### Test 23: Validate request payload shape for single booking
- Purpose: verify request validation before service execution.
- Expected Behaviour: malformed requests are rejected by schema validation.
- Requirement Reference: requirements 4.1, IC-1.
- TSD Reference: Sections 10.2, 11.
- Pass Criteria: invalid payloads fail before business logic executes.

### Test 24: Validate request payload shape for recurring booking
- Purpose: verify recurring booking request validation.
- Expected Behaviour: malformed recurring requests are rejected.
- Requirement Reference: requirements 4.2, 8.3, 8.7.
- TSD Reference: Sections 10.3, 11, 12.2.
- Pass Criteria: invalid payloads fail with validation errors and no data is written.

### Test 25: Validate `repeat_until` before recurring weekday
- Purpose: verify boundary validation for recurring scheduling.
- Expected Behaviour: `repeat_until` earlier than the first generated occurrence window is rejected.
- Requirement Reference: requirements 4.2, 9.
- TSD Reference: Sections 10.3, 11, 12.2.
- Pass Criteria: the request is rejected and nothing is persisted.

### Test 26: Validate database constraints on status values
- Purpose: verify that only valid booking statuses are accepted.
- Expected Behaviour: booking rows only use allowed status values.
- Requirement Reference: BR-4, IC-3.
- TSD Reference: Sections 7, 11, 12.3, 12.4.
- Pass Criteria: the model or database layer prevents invalid status values from persisting.

## Conflict Detection

### Test 27: Same-room conflict rejection
- Purpose: verify conflict detection for overlapping same-room bookings.
- Expected Behaviour: overlapping bookings in the same room are rejected consistently across create flows.
- Requirement Reference: BR-1, requirements 4.1, 4.2.
- TSD Reference: Sections 11, 12.1, 12.2, 14.
- Pass Criteria: both single and recurring booking flows reject overlaps in the same room.

### Test 28: Different-room non-conflict
- Purpose: verify that conflict checks are room-scoped.
- Expected Behaviour: identical times in different rooms do not conflict.
- Requirement Reference: BR-1, BR-7.
- TSD Reference: Sections 11, 14.
- Pass Criteria: the second room’s booking succeeds.

### Test 29: Cancelled booking does not block conflicts
- Purpose: verify that cancellation removes the slot from active conflict checks.
- Expected Behaviour: only active bookings participate in conflict detection.
- Requirement Reference: requirements 4.3, 4.4, BR-4.
- TSD Reference: Sections 11, 12.1, 12.4, 14.
- Pass Criteria: a new booking is accepted after cancellation in the same time slot.

## Recurring Booking

### Test 30: Recurrence uses the first occurrence weekday
- Purpose: verify weekly repeat rule interpretation.
- Expected Behaviour: recurring bookings repeat on the weekday of the first occurrence.
- Requirement Reference: requirements 4.2, 8.3.
- TSD Reference: Sections 4 IA-002, 12.2.
- Pass Criteria: the generated series matches the first occurrence weekday and does not require an additional weekday field.

### Test 31: Recurrence stores all generated occurrences upfront
- Purpose: verify upfront generation behavior.
- Expected Behaviour: recurring bookings are stored at creation time and not generated lazily.
- Requirement Reference: BR-3, requirements 4.2.
- TSD Reference: Sections 12.2, 14.
- Pass Criteria: all series occurrences exist immediately after creation.

### Test 32: R1 rollback on partial recurring conflict
- Purpose: verify transactional all-or-nothing behavior for recurring creation.
- Expected Behaviour: any one conflicting occurrence cancels the entire recurring request.
- Requirement Reference: requirements 8.1, BR-3.
- TSD Reference: Sections 5, 9, 12.2, 14.
- Pass Criteria: no rows are persisted when a single occurrence conflicts.

### Test 33: R1 rollback on full recurring conflict
- Purpose: verify the all-conflict recurring case.
- Expected Behaviour: when every generated occurrence conflicts, nothing is saved.
- Requirement Reference: requirements 8.1, 4.2.
- TSD Reference: Sections 5, 10.3, 12.2, 14.
- Pass Criteria: the entire request is rolled back and the response is a conflict.

## Recurring Cancellation

### Test 34: Future recurring occurrences are cancelled
- Purpose: verify future-only cancellation behavior.
- Expected Behaviour: only future active bookings in the series are cancelled.
- Requirement Reference: requirements 4.4, BR-4.
- TSD Reference: Sections 10.5, 12.4.
- Pass Criteria: future rows are cancelled and the response count matches the number of affected rows.

### Test 35: Past recurring occurrences are preserved
- Purpose: verify historical preservation during recurring cancellation.
- Expected Behaviour: past occurrences stay unchanged after series cancellation.
- Requirement Reference: requirements 4.4, BR-4, 8.5.
- TSD Reference: Sections 10.5, 12.4.
- Pass Criteria: past occurrences remain present after cancellation.

## Timezone

### Test 36: Booking timezone interpretation uses room timezone
- Purpose: verify timezone ownership.
- Expected Behaviour: room-local time is the source of truth for booking interpretation.
- Requirement Reference: requirements 8.2, BR-5.
- TSD Reference: Sections 4 IA-001, 13.1, 13.2.
- Pass Criteria: booking creation and recurrence logic use the room’s timezone, not a user timezone.

### Test 37: Room timezone data is stored and read correctly
- Purpose: verify that room records support timezone-aware recurrence.
- Expected Behaviour: the room’s timezone field is available to the recurrence logic.
- Requirement Reference: requirements 8.2, BR-5, BR-6.
- TSD Reference: Sections 7, 13.2.
- Pass Criteria: the timezone value is persisted and used by recurrence generation.

## DST

### Test 38: Spring-forward DST preserves local time
- Purpose: verify DST handling during spring-forward transition.
- Expected Behaviour: recurring bookings remain at the intended local time instead of shifting by one hour.
- Requirement Reference: BR-6, requirements 8.2, 9.
- TSD Reference: Sections 13.3, 13.5.
- Pass Criteria: generated occurrences keep the intended local hour across the transition.

### Test 39: Fall-back DST preserves local time
- Purpose: verify DST handling during fall-back transition.
- Expected Behaviour: recurring bookings remain at the intended local time during the repeated hour.
- Requirement Reference: BR-6, requirements 8.2, 9.
- TSD Reference: Sections 13.3, 13.5.
- Pass Criteria: generated occurrences remain stable and deterministic across the transition.

### Test 40: Berlin DST recurrence remains stable
- Purpose: verify recurrence correctness in the Berlin office timezone.
- Expected Behaviour: the Berlin room’s recurring bookings preserve the intended wall-clock time across DST.
- Requirement Reference: BR-5, BR-6, requirements 8.2.
- TSD Reference: Sections 13.1, 13.3.
- Pass Criteria: local 09:00 remains local 09:00 in Berlin across the DST boundary.

### Test 41: Denver DST recurrence remains stable
- Purpose: verify recurrence correctness in the Denver office timezone.
- Expected Behaviour: the Denver room’s recurring bookings preserve the intended wall-clock time across DST.
- Requirement Reference: BR-5, BR-6, requirements 8.2.
- TSD Reference: Sections 13.1, 13.3.
- Pass Criteria: local 09:00 remains local 09:00 in Denver across the DST boundary.

## Backward Compatibility

### Test 42: Legacy room listing contract remains unchanged
- Purpose: verify that `GET /rooms` stays compatible with existing integrations.
- Expected Behaviour: response structure, field set, and ordering remain stable.
- Requirement Reference: IC-2, IC-3, requirements 4.5.
- TSD Reference: Sections 10.1, 13.5, 16.
- Pass Criteria: the response matches the legacy contract exactly.

### Test 43: Legacy timestamp contract remains unchanged
- Purpose: verify that all booking timestamps remain naive local ISO strings.
- Expected Behaviour: no endpoint returns timezone offsets in booking timestamps.
- Requirement Reference: IC-1, IC-3.
- TSD Reference: Sections 10, 13.4, 13.5.
- Pass Criteria: every response and persisted value exposed through APIs uses the naive format.

## API Responses

### Test 44: Single booking success response shape
- Purpose: verify the single-booking success payload.
- Expected Behaviour: the response includes the documented booking fields and status.
- Requirement Reference: requirements 4.1, IC-1.
- TSD Reference: Sections 10.2, 12.1.
- Pass Criteria: the response body matches the documented contract exactly.

### Test 45: Recurring booking success response shape
- Purpose: verify the recurring-booking success payload.
- Expected Behaviour: the response includes the series identifier, occurrence count, and booking list.
- Requirement Reference: requirements 4.2, BR-3.
- TSD Reference: Sections 10.3, 12.2.
- Pass Criteria: response fields and nested booking data match the TSD contract.

### Test 46: Cancellation response shape
- Purpose: verify the cancellation response payloads.
- Expected Behaviour: single and recurring cancellation responses return the documented identifiers and status/count fields.
- Requirement Reference: requirements 4.3, 4.4.
- TSD Reference: Sections 10.4, 10.5, 12.3, 12.4.
- Pass Criteria: the response bodies match the documented cancellation contracts exactly.

## Database Validation

### Test 47: Room IDs remain sequential
- Purpose: verify the sequential room identifier assumption.
- Expected Behaviour: room listing and room creation data remain ordered by sequential ids.
- Requirement Reference: BR-7.
- TSD Reference: Sections 7, 10.1.
- Pass Criteria: test data and query results preserve sequential room ids.

### Test 48: Booking rows store status correctly
- Purpose: verify booking persistence semantics.
- Expected Behaviour: active bookings and cancelled bookings persist with the correct status.
- Requirement Reference: requirements 4.3, 4.4, IC-3.
- TSD Reference: Sections 7, 11, 12.3, 12.4.
- Pass Criteria: persisted rows match the expected status values.

### Test 49: Conflict index supports room-scoped lookup
- Purpose: verify database shape supports room-scoped conflict queries.
- Expected Behaviour: booking queries can efficiently identify conflicts by room and time.
- Requirement Reference: BR-1, BR-7.
- TSD Reference: Sections 7, 14.
- Pass Criteria: the schema and query behavior support room-based conflict detection.

## Edge Cases

### Test 50: Start time equals end time is rejected
- Purpose: verify invalid duration rejection.
- Expected Behaviour: zero-length bookings are not allowed.
- Requirement Reference: requirements 4.1, 9.
- TSD Reference: Sections 11, 12.1.
- Pass Criteria: the request fails and no booking is created.

### Test 51: Start time after end time is rejected
- Purpose: verify reverse duration rejection.
- Expected Behaviour: bookings with inverted times are not allowed.
- Requirement Reference: requirements 4.1, 9.
- TSD Reference: Sections 11, 12.1.
- Pass Criteria: the request fails with the expected validation response.

### Test 52: Room does not exist is rejected
- Purpose: verify missing-room handling.
- Expected Behaviour: any booking request for an unknown room is rejected.
- Requirement Reference: requirements 4.1, 4.2, 9.
- TSD Reference: Sections 11, 12.1, 12.2.
- Pass Criteria: the API returns not-found and no data is stored.

### Test 53: Booking can be created after cancellation in same slot
- Purpose: verify slot reuse after cancellation.
- Expected Behaviour: cancellation releases the time slot for reuse.
- Requirement Reference: requirements 4.3, 8.5, BR-4.
- TSD Reference: Sections 11, 12.3, 14.
- Pass Criteria: the new booking succeeds in the same time range after cancellation.

### Test 54: Past bookings are handled as documented
- Purpose: verify the past-booking assumption is respected.
- Expected Behaviour: past-booking behavior follows the documented implementation assumption and does not introduce undocumented rejection logic.
- Requirement Reference: requirements 8.6.
- TSD Reference: Section 4 IA-003.
- Pass Criteria: the implementation behaves consistently with the documented assumption and does not silently add a different rule.

### Test 55: No undocumented behavior appears in responses
- Purpose: verify that API responses remain within the documented contract surface.
- Expected Behaviour: endpoints do not add undocumented fields or alternate response shapes.
- Requirement Reference: IC-2, IC-3.
- TSD Reference: Sections 10, 13.5, 16.
- Pass Criteria: response payloads remain exactly within the documented contract.

## Requirement Traceability

Every requirement must have at least one corresponding test:

| Requirement | Corresponding Test(s) |
|---|---|
| 4.1 Create single booking | Tests 8, 9, 10, 11, 12, 23, 44, 50, 51, 52 |
| 4.2 Create recurring booking | Tests 4, 15, 16, 17, 24, 25, 30, 31, 32, 33, 45 |
| 4.3 Cancel single booking | Tests 5, 13, 14, 20, 29, 46, 53 |
| 4.4 Cancel recurring booking | Tests 5, 18, 19, 29, 34, 35, 46 |
| 4.5 Room listing | Tests 2, 7, 21, 42 |
| BR-1 Booking conflict | Tests 1, 2, 8, 11, 27, 28, 29 |
| BR-2 Back-to-back bookings | Tests 1, 12 |
| BR-3 Recurring booking generation | Tests 3, 15, 16, 17, 31, 32, 33, 45 |
| BR-4 Recurring cancellation | Tests 5, 13, 14, 18, 19, 20, 29, 34, 35, 53 |
| BR-5 Wall clock time | Tests 3, 30, 36, 38, 39, 40, 41 |
| BR-6 DST | Tests 3, 36, 37, 38, 39, 40, 41 |
| BR-7 Sequential room IDs | Tests 2, 7, 47, 49 |
| IC-1 Timestamp format | Tests 6, 22, 43, 44, 46 |
| IC-2 Room API response | Tests 7, 21, 42 |
| IC-3 Backward compatibility | Tests 6, 21, 22, 42, 43, 55 |
| 8.1 Recurring booking creation | Tests 16, 17, 32, 33 |
| 8.2 Timezone ownership | Tests 3, 36, 37, 40, 41 |
| 8.3 Weekly repeat rule | Tests 3, 4, 30 |
| 8.4 Booking updates | No implementation scope in TSD; verify absence of undocumented update API in Test 55. |
| 8.5 Booking deletion | Tests 13, 14, 18, 19, 20, 53 |
| 8.6 Past bookings | Tests 23, 54 |
| 8.7 Maximum recurrence duration | Tests 4, 25, 32, 33 |
| 8.8 Concurrent booking requests | Tests 29 and transaction-sensitive recurring rollback tests 16, 17, 32, 33 |
| 9 Edge cases | Tests 9, 10, 14, 16, 17, 20, 23, 25, 50, 51, 52, 53, 54 |
| 10 Success checklist | Tests 8 through 55 as applicable |

## Regression Checklist

Before approving implementation verify:

- API contract unchanged.
- Timestamp format unchanged.
- `GET /rooms` unchanged.
- Conflict detection correct.
- Cancellation correct.
- Wall-clock recurrence correct.
- DST behaviour correct.

## Final QA Checklist

Approve implementation only if:

- Every requirement passes.
- Every implementation assumption is respected.
- Every edge case passes.
- No undocumented behaviour exists.

