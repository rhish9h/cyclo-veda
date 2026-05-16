# Cycling Training Calendar — Overview

## Goal

Give users a single view of their cycling life: past Strava activities alongside future
workouts they plan themselves. The calendar replaces the current placeholder Dashboard as
the primary page of the app.

---

## Current State

### Existing Assets
- ✅ Strava OAuth — tokens stored in DB, activities fetchable via `GET /api/strava/activities`
- ✅ PostgreSQL + SQLAlchemy + Alembic migrations pipeline
- ✅ Clean architecture: `models/`, `schemas/`, `routers/`, `services/`, `repositories/`
- ✅ React + TypeScript frontend with CSS Modules, React Router, protected routes
- ✅ `Dashboard` page exists but shows placeholder content only

### Gaps
- No local storage of Strava activities (always fetched live, no caching)
- No concept of a "planned workout"
- No calendar UI
- No training load / metrics summary
- 90 hardcoded colour values across 5 module CSS files with inconsistent brand colour

---

## User Stories

| # | As a… | I want to… | So that… |
|---|-------|-----------|---------|
| 1 | cyclist | see all my past Strava rides on a monthly calendar | I can review my training history at a glance |
| 2 | cyclist | click a past ride to see key stats (distance, duration, elevation, avg power/HR) | I can understand each session without leaving the app |
| 3 | cyclist | create a planned workout on a future date | I can structure my training week in advance |
| 4 | cyclist | edit or delete a planned workout | I can adjust my plan when life happens |
| 5 | cyclist | switch between month and week views | I can zoom in for daily detail or zoom out for the big picture |
| 6 | cyclist | see a weekly training load summary (total distance + elevation) | I can monitor fatigue and avoid overtraining |

---

## Requirements

### Functional
1. Month view (default) and week view, navigable with prev/next and a "Today" button
2. Strava activity tiles appear on the calendar on their activity date
3. Users can create, edit, and delete planned workout entries for any date
4. Clicking any tile opens a detail panel with full information
5. A weekly summary strip shows total distance and elevation for the visible week(s)
6. If Strava is not connected, the calendar still loads with planned workouts only and shows a connection prompt

### Non-Functional
1. Month view renders within 500 ms; Strava activities fetched with `after`/`before` unix timestamps per month
2. Follows existing clean architecture patterns — no shortcuts
3. No new auth model changes
4. Mobile-responsive: week view promoted on narrow screens
5. Unit tests for new service layer; integration tests for new API endpoints

---

## Architecture Overview

### Data Model

One new table: `planned_workouts` (user-created future workouts).

Strava activities are **not cached locally in v1** — fetched live per month via the existing
`/api/strava/activities` endpoint. This keeps the schema minimal; a caching layer can be added
later for offline support or advanced analytics.

```
users (existing)
  └─── planned_workouts  (new, one-to-many)
```

Key columns: `user_id`, `title`, `workout_type`, `planned_date` (DATE), `planned_duration_minutes`,
`planned_distance_km`, `notes`.

### API Surface

All new routes under `/api/calendar/`, requiring JWT auth.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/calendar/entries?year=YYYY&month=MM` | Returns planned workouts + Strava activities for the month |
| `POST` | `/api/calendar/workouts` | Create a planned workout |
| `PUT` | `/api/calendar/workouts/{id}` | Update a planned workout |
| `DELETE` | `/api/calendar/workouts/{id}` | Delete a planned workout |

**Key architectural decision — server-side Strava proxy**: `GET /api/calendar/entries` fetches
Strava activities on behalf of the client rather than returning a token for the frontend to use
directly. This keeps Strava tokens server-side only, handles token refresh transparently, and
gives us a single combined response the frontend can consume without knowing about Strava at all.
The tradeoff is slightly higher backend latency on this endpoint.

### Backend Structure

New files follow the existing `models / schemas / repositories / services / routers` pattern.

```
app/
├── models/
│   └── planned_workout.py          (Phase 2 — SQLAlchemy ORM)
├── schemas/
│   └── calendar.py                 (Phase 1 — Pydantic request/response schemas)
├── repositories/
│   └── planned_workout_repository.py  (Phase 2 — CRUD)
├── services/
│   └── calendar_service.py         (Phase 1 — orchestrates DB + Strava proxy)
├── routers/
│   └── calendar.py                 (Phase 1 — FastAPI router)
└── main.py                         (Phase 1 — register router)
```

Alembic migration for `planned_workouts` table added in Phase 2.

### Frontend Architecture

New route: `/calendar` (protected, lazy-loaded). All component CSS uses `var(--token)` — no
raw colour values.

```
CalendarPage
├── CalendarHeader          (navigation, view toggle)
├── WeeklySummaryStrip      (distance + elevation totals)
├── MonthView | WeekView    (conditional)
│   └── CalendarDayCell
│       ├── StravaActivityTile
│       └── PlannedWorkoutTile
├── EntryDetailPanel        (slide-in on tile click)
└── WorkoutFormModal        (create / edit planned workout)
```

New supporting files: `src/services/calendarService.ts`, `src/types/calendar.ts`,
`ROUTES.CALENDAR` and `API_ENDPOINTS.CALENDAR` constants.

---

## Phases

| Phase | Name | Status |
|-------|------|--------|
| [Phase 0](./phase-0-design-tokens.md) | Design Token Foundation | Detailed — ready to implement |
| [Phase 1](./phase-1-read-only-calendar.md) | Read-Only Calendar (Strava Activities) | Detailed — ready to implement |
| [Phase 2](./phase-2-planned-workouts.md) | Planned Workouts CRUD | Outline |
| [Phase 3](./phase-3-week-view-polish.md) | Week View + Polish | Outline |

---

## Open Questions

1. **Strava activity caching**: cache in a `strava_activities` table for offline/analytics support? Deferred to post-v1.
2. **Workout type taxonomy**: fixed enum (`endurance`, `intervals`, `race`, `recovery`, `other`) or user-extensible? Decision needed before Phase 2.
3. **Planned → actual linking**: should a planned workout be linkable to a Strava activity after the fact (compliance tracking)? Deferred to post-v1.
4. **Timezone handling**: `planned_date` is a calendar date. Strava timestamps are UTC. Should the user's timezone preference (already in Settings) drive the conversion? Decision needed before Phase 1.
5. **Default landing page**: should `/calendar` replace `/dashboard` as the post-login redirect? Dashboard is currently a placeholder.
