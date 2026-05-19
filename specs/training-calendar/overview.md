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
| 1 | cyclist | create a planned workout on a future date | I can structure my training week in advance |
| 2 | cyclist | edit or delete a planned workout | I can adjust my plan when life happens |
| 3 | cyclist | switch between daily, weekly, monthly, and yearly views | I can zoom in for daily detail or zoom out for the big picture |
| 4 | cyclist | see a training load summary (total distance + elevation) for the visible period | I can monitor fatigue and avoid overtraining |
| 5 | cyclist | see all my past Strava rides on the calendar | I can review my training history at a glance |
| 6 | cyclist | click a past ride to see key stats (distance, duration, elevation, avg power/HR) | I can understand each session without leaving the app |

---

## Requirements

### Functional
1. Daily, weekly, monthly, and yearly calendar views (monthly is default), navigable with prev/next and a "Today" button
2. Strava activity tiles appear on the calendar on their activity date
3. Users can create, edit, and delete planned workout entries for any date
4. Clicking any tile opens a detail panel with full information
5. A summary strip shows total distance and elevation for the visible period (daily/weekly/monthly/yearly)
6. If Strava is not connected, the calendar still loads with planned workouts only and shows a connection prompt

### Non-Functional
1. Monthly view renders within 500 ms; Strava activities fetched with `after`/`before` unix timestamps per month
2. Follows existing clean architecture patterns — no shortcuts
3. No new auth model changes
4. Mobile-responsive: daily view promoted on narrow screens, weekly view on medium screens
5. Unit tests for new service layer; integration tests for new API endpoints

---

## Architecture Overview

### Data Model

Two new tables introduced across Phase 1 and Phase 4.

```
users (existing)
  ├── planned_workouts  (Phase 1 — one-to-many)
  └── workout_types     (Phase 1 — user-created custom types; system defaults use NULL user_id)
```

**`planned_workouts`** key columns: `user_id`, `workout_type_id` (FK), `title`, `planned_date` (DATE),
`planned_duration_minutes`, `planned_distance_km`, `notes`.

**`workout_types`** key columns: `user_id` (NULL = system default), `name`, `is_system`.
System defaults seeded in migration: `endurance`, `intervals`, `race`, `recovery`, `other`.
Users can create, rename, and delete their own custom types.

**Strava activities are not stored locally until Phase 4.** Phases 1–3 never touch the DB
for Strava data — Phase 3 fetches live per request.

**Timezone strategy**: all `TIMESTAMP WITH TIME ZONE` columns store UTC. `planned_date` is a
`DATE` (timezone-agnostic). The frontend is responsible for converting UTC timestamps to the
user's preferred timezone (already in Settings) using `Intl.DateTimeFormat`.

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
│   └── planned_workout.py          (Phase 1 — SQLAlchemy ORM)
├── schemas/
│   └── calendar.py                 (Phase 1 — Pydantic request/response schemas)
├── repositories/
│   └── planned_workout_repository.py  (Phase 1 — CRUD)
├── services/
│   └── calendar_service.py         (Phase 1 — orchestrates DB + Strava proxy)
├── routers/
│   └── calendar.py                 (Phase 1 — FastAPI router)
└── main.py                         (Phase 1 — register router)
```

Alembic migrations for `workout_types` and `planned_workouts` added in Phase 1.

### Frontend Architecture

New route: `/calendar` (protected, lazy-loaded). All component CSS uses `var(--token)` — no
raw colour values. Dashboard is **not replaced** — a "Go to Training Calendar" button is added
there in Phase 1 (future scope: mini calendar widget).

```
CalendarPage
├── CalendarHeader          (navigation; view toggle added in Phase 2)
├── PeriodSummaryStrip      (distance + duration totals for visible period)
├── DailyView | WeekView | MonthView | YearView    (WeekView added in Phase 2)
│   └── CalendarDayCell
│       ├── PlannedWorkoutTile    (Phase 1)
│       └── StravaActivityTile    (Phase 3)
├── EntryDetailPanel        (slide-in on tile click)
└── WorkoutFormModal        (create / edit planned workout)
```

New supporting files: `src/services/calendarService.ts`, `src/types/calendar.ts`,
`ROUTES.CALENDAR` and `API_ENDPOINTS.CALENDAR` constants.

---

## Phases

| Phase | File | Name | Detail |
|-------|------|------|--------|
| 0 | [phase-0-design-tokens.md](./phase-0-design-tokens.md) | Design Token Foundation | Detailed — ready to implement |
| 1 | — | Planned Workouts Calendar (no Strava) | Not yet written |
| 2 | [phase-2-week-view-polish.md](./phase-2-week-view-polish.md) | Week View + Polish | Outline |
| 3 | — | Strava Live Feed | Not yet written |
| 4 | — | Strava Activity Caching | Not yet written |
| 5 | — | Planned → Actual Activity Linking | Not yet written |

---

## Decisions

| # | Decision |
|---|----------|
| 1 | **Strava caching** — deferred to Phase 4. Phases 1–3 work without any local Strava storage. |
| 2 | **Workout type taxonomy** — fixed system defaults (`endurance`, `intervals`, `race`, `recovery`, `other`) seeded in DB. Users can create and save their own custom types, also stored in DB (`workout_types` table). |
| 3 | **Timezone** — all timestamps stored as UTC. `planned_date` is a `DATE` (no timezone). Frontend converts UTC to the user's preferred timezone via `Intl.DateTimeFormat`. |
| 4 | **Dashboard** — not replaced. A "Go to Training Calendar" button is added to the Dashboard content area in Phase 1. Future scope: replace with a mini calendar widget showing the next 7 days. |
| 5 | **Planned → actual linking** — deferred to Phase 5. Users will be able to link a planned workout to a completed Strava activity for compliance tracking. |

## Open Questions

1. **Week view time slots** (Phase 2): all-day list per column, or timed hour-row grid? Depends on whether activity start times are important to users.
2. **Custom workout type colours** (Phase 1): should users be able to assign a colour to a custom type, or use a single default colour for all custom types?
3. **Mini calendar widget scope** (post-Phase 2): what data should the widget show — just planned workouts, or Strava activities too once Phase 3 is done?
