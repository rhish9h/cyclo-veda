# Phase 3 — Strava Live Feed

**Depends on: Phase 2 complete.**

---

## Goal

Bring Strava activities onto the calendar alongside planned workouts. Activities are fetched
live from the Strava API per month — no local caching yet (that comes in Phase 4). The
calendar now shows the full picture: what was planned and what was actually ridden.

---

## Backend

### Update `GET /api/calendar/entries`

Extend `calendar_service.py` to:
1. Check if the user has a connected Strava account (`strava_token_repository.get_by_user_id`)
2. If connected, call `GET /api/strava/activities` with `after`/`before` unix timestamps for
   the requested month, using `get_valid_token` (auto-refreshes if expiring)
3. Return activities in `strava_activities` array; return empty array if not connected

Error handling (no errors thrown — calendar always renders):
- Strava not connected → `strava_activities: []`, `strava_error: null`
- Token revoked → `strava_activities: []`, `strava_error: "token_revoked"`
- Strava API failure → `strava_activities: []`, `strava_error: "fetch_failed"`

No new DB models or migrations in this phase.

### Response schema change

`strava_activities` in `CalendarEntriesResponse` changes from `list` to
`list[StravaActivity]` (reuse the existing schema from `app/schemas/strava.py`).

---

## Frontend

### New Component: `StravaActivityTile.tsx`

Chip using `--color-strava` (orange). Shows activity name and formatted distance.
Clicking opens `EntryDetailPanel` in Strava-activity mode.

### Update `EntryDetailPanel.tsx`

Handle both `PlannedWorkout` and `StravaActivity` entry types. Strava activity view shows:
name, type, date (converted to user's local timezone via `Intl.DateTimeFormat`), distance,
moving time, elevation, avg HR and watts (if present), and a "View on Strava" external link.

### Strava Disconnection Banner

New `StravaStatusBanner.tsx` component rendered at the top of `CalendarPage` when
`strava_error` is non-null:
- `"token_revoked"` → `"Your Strava connection has expired."` with a link to
  `/settings?section=connections`
- `"fetch_failed"` → `"Couldn't load Strava activities — they'll reappear when the
  connection is restored."` (softer, dismissible)

### Update `CalendarEntries` type (`src/types/calendar.ts`)

`strava_activities` changes from `never[]` to `StravaActivity[]`.

### Update `WeeklySummaryStrip.tsx`

Include Strava activity distance and elevation in weekly totals alongside planned workout
totals.

---

## Key Decisions Before Implementing

1. **Timezone display**: Strava `start_date` is UTC — confirm the frontend reads the user's
   timezone from the Settings profile API (or a cached value in `localStorage`) to pass to
   `Intl.DateTimeFormat`.
2. **Tile ordering within a day**: when a planned workout and a Strava activity fall on the
   same day, which appears first? Suggested: planned workouts first, then Strava activities.

---

## Definition of Done

- Strava activities appear on the correct date tiles in the month grid
- Activities are correctly filtered to the viewed month using `after`/`before` timestamps
- `StravaActivityTile` is visually distinct from `PlannedWorkoutTile`
- Strava activity detail panel shows all key fields with timezone-correct date display
- Strava disconnection banners appear, link correctly, and are dismissible
- Calendar renders correctly with no crash when Strava is not connected
- No regression in Phase 1 or Phase 2 functionality
