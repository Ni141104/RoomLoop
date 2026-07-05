# RoomLoop Booking Service
## Requirement Analysis

> **Purpose of this document**
>
> This document captures the functional requirements, business rules, implementation expectations, constraints, assumptions, ambiguities, and edge cases identified from the assignment.
>
> It serves as the primary reference for designing and implementing the solution.
>
> This document intentionally focuses on **what** needs to be built rather than **how** it will be implemented.

---

# 1. Project Goal

The objective is to rebuild the core booking service for **RoomLoop**, an internal meeting room booking system.

The new implementation should support reliable room booking while remaining compatible with existing internal systems that already consume the current API.

The implementation should improve correctness, maintainability, and recurring booking support without breaking existing integrations.

---

# 2. Existing System

This project replaces an existing booking implementation rather than building a completely new system.

Multiple internal tools already depend on the current booking API.

Because of this:

- Existing integrations should continue working.
- Backward compatibility must be preserved wherever explicitly required.
- Integration constraints provided in the assignment are mandatory.
- Any implementation decision should consider compatibility before introducing changes.

---

# 3. What Needs To Be Built

The booking service should support the following operations:

- Create a single booking.
- Create a recurring booking.
- Cancel a single booking.
- Cancel future occurrences of a recurring booking.
- Detect booking conflicts.
- Provide room information.

---

# 4. Functional Requirements

## 4.1 Create Single Booking

### Purpose

Allow a user to reserve a meeting room for a specific time period.

### Input

- Room
- User
- Start Time
- End Time

### Expected Behaviour

Implementation must:

- Validate the room exists.
- Validate the booking duration.
- Check for booking conflicts.
- Create the booking if validation succeeds.

### Validation

Implementation should reject requests when:

- Room does not exist.
- Start time is greater than or equal to end time.
- Booking conflicts with an existing booking.

---

## 4.2 Create Recurring Booking

### Purpose

Allow users to reserve the same room repeatedly on a weekly schedule.

### Input

- Room
- User
- Start Time
- End Time
- Weekly repeat rule
- Repeat until date

### Expected Behaviour

Implementation must:

- Generate every booking occurrence during booking creation.
- Store every occurrence individually.
- Apply conflict validation for every occurrence.
- Respect recurring booking rules defined in the assignment.

Recurring bookings should not be generated dynamically in the future.

---

## 4.3 Cancel Single Booking

### Purpose

Allow users to cancel an individual booking.

### Expected Behaviour

Only the selected booking should be cancelled.

No other bookings should be affected.

---

## 4.4 Cancel Recurring Booking

### Purpose

Allow users to cancel an entire recurring booking series.

### Expected Behaviour

Implementation must:

- Cancel only future occurrences.
- Preserve all historical occurrences.
- Leave unrelated bookings unchanged.

---

## 4.5 Room Listing

The service should expose room information while preserving the existing API response format required by dependent systems.

---

# 5. Business Rules

## BR-1 Booking Conflict

Two bookings conflict only when:

- They belong to the same room.
- Their time intervals overlap.

Bookings in different rooms never conflict.

---

## BR-2 Back-to-Back Bookings

Back-to-back bookings are allowed.

Example:

09:00 – 10:00

10:00 – 11:00

These should not be considered conflicting.

---

## BR-3 Recurring Booking Generation

Recurring bookings must generate every occurrence during booking creation.

Occurrences should not be created lazily.

---

## BR-4 Recurring Cancellation

Cancelling a recurring booking should affect only future occurrences belonging to the same recurring series.

Historical occurrences must remain available.

---

## BR-5 Wall Clock Time

Recurring bookings must repeat at the same local wall-clock time for every occurrence.

Example:

Every Monday

09:00

must always remain

09:00

even when daylight saving time changes.

---

## BR-6 Daylight Saving Time (DST)

The implementation must correctly handle daylight saving time transitions.

Recurring bookings should preserve their intended local booking time rather than shifting by one hour after DST changes.

---

## BR-7 Sequential Room IDs

Room identifiers are sequential.

Availability checks may iterate room IDs from 1 to N.

No optimization is required for this assignment.

---

# 6. Integration Constraints

The following constraints exist because other internal systems already consume the current API.

These constraints are mandatory.

---

## IC-1 Timestamp Format

Implementation must preserve the existing timestamp format.

Required format:

2026-07-02T09:00:00

Timezone offsets must not be added.

Reason:

The reporting system depends on naive local ISO timestamps.

---

## IC-2 Room API Response

The existing response structure for room listing must remain unchanged.

Dependent systems render the response directly.

Changing the response structure may break existing integrations.

---

## IC-3 Backward Compatibility

Implementation should preserve existing externally visible behaviour unless the assignment explicitly allows changes.

Compatibility should take priority over preferred internal implementation choices.

---

# 7. Implementation Expectations

Although implementation details are intentionally excluded from this document, the following behaviours must be guaranteed.

Implementation should ensure:

- Every recurring booking belongs to one logical recurring series.
- Future cancellation can identify every booking in that recurring series.
- Historical bookings remain available after cancellation.
- Conflict detection follows the business rules consistently.
- Existing API compatibility is preserved.
- Timezone behaviour remains correct while respecting the required timestamp format.
- Booking generation is deterministic and reproducible.

---

# 8. Points Requiring Clarification

The assignment contains several areas where the expected behaviour is not fully defined.

These should be documented before implementation.

---

## 8.1 Recurring Booking Creation

### Issue

Requirement R1 states:

Recurring booking creation is all-or-nothing.

Requirement R2 states:

If one or two occurrences conflict, skip those occurrences and create the remaining bookings.

### Why it matters

These two behaviours cannot both occur simultaneously.

### Current Status

Implementation requires a documented assumption before development.

---

## 8.2 Timezone Ownership

### Issue

The assignment mentions Berlin and Denver offices but does not explicitly define whether booking time should be interpreted using:

- Room timezone
- Office timezone
- User timezone

### Why it matters

Timezone ownership affects recurring booking generation and DST handling.

### Current Interpretation

Bookings should follow the local timezone of the room's office because this is a room booking system rather than a calendar scheduling system.

---

## 8.3 Weekly Repeat Rule

The assignment specifies a weekly repeat rule but does not define whether multiple weekdays are supported.

Example:

- Every Monday
- Monday and Wednesday

---

## 8.4 Booking Updates

Editing an existing booking is not described.

---

## 8.5 Booking Deletion

Only cancellation is defined.

Permanent deletion behaviour is not specified.

---

## 8.6 Past Bookings

The assignment does not specify whether bookings can be created for past dates.

---

## 8.7 Maximum Recurrence Duration

No limit is defined for how many booking occurrences may be generated.

---

## 8.8 Concurrent Booking Requests

The assignment does not define behaviour when multiple users attempt to reserve the same room simultaneously.

---

# 9. Edge Cases

| Scenario | Expected Behaviour |
|------------|-------------------|
| Room does not exist | Reject booking |
| Start time equals end time | Reject booking |
| Start time after end time | Reject booking |
| Booking overlaps existing booking | Reject booking |
| Back-to-back booking | Allow booking |
| Repeat until before first occurrence | Reject recurring booking |
| Entire recurring booking conflicts | Depends on R1 / R2 clarification |
| Partial recurring booking conflict | Depends on R1 / R2 clarification |
| DST transition | Preserve local booking time |
| Cancel already cancelled booking | Should not fail unexpectedly |

---

# 10. Success Checklist

The implementation can be considered complete when all of the following are satisfied.

- Single bookings can be created successfully.
- Recurring bookings generate every required occurrence.
- Booking conflicts are detected correctly.
- Back-to-back bookings are allowed.
- Future recurring bookings can be cancelled.
- Historical recurring bookings remain available.
- Existing timestamp format remains unchanged.
- Existing room API response remains unchanged.
- Backward compatibility is preserved.
- Daylight saving time behaviour remains correct.
- Important assumptions are documented.
- Edge cases are tested.