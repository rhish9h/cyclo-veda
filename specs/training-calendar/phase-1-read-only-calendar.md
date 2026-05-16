# Phase 1 — Read-Only Calendar (Strava Activities)

**Depends on: Phase 0 complete.**

---

## Goal

Render a working month-view calendar showing the authenticated user's past Strava activities.
No planned workouts yet. This phase proves the full data pipeline: backend proxies the Strava
API call and returns a combined response shape that the frontend calendar consumes.

---

## Backend

### New Endpoint: `GET /api/calendar/entries`

**Query params**: `year: int`, `month: int` (both required)

**Auth**: `get_current_user` dependency (JWT Bearer token)

**Behaviour**:
1. Compute the first and last unix timestamps of the requested month in UTC
2. If the user has a connected Strava account, call `GET /api/strava/activities` with
   `after` and `before` params using the stored token (auto-refreshed via `get_valid_token`)
3. Fetch the user's planned workouts from DB for the month (returns empty list in Phase 1)
4. Return combined `CalendarEntriesResponse`

**Error handling**:
- If Strava is not connected: return response with empty `strava_activities` list, no error
- If Strava token is revoked: return response with empty `strava_activities` + a
  `strava_error: "token_revoked"` field so the frontend can show a reconnect prompt
- If Strava API call fails (non-401): return response with empty `strava_activities` +
  `strava_error: "fetch_failed"`

### Response Schema

```json
{
  "year": 2026,
  "month": 5,
  "planned_workouts": [],
  "strava_activities": [
    {
      "id": 123456789,
      "name": "Morning Ride",
      "type": "Ride",
      "start_date": "2026-05-10T07:30:00Z",
      "distance_m": 55000,
      "moving_time_s": 6300,
      "total_elevation_gain_m": 450,
      "average_heartrate": 148,
      "average_watts": 195
    }
  ],
  "strava_error": null
}
```

### New Pydantic Schemas (`app/schemas/calendar.py`)

- `CalendarEntriesResponse` — top-level response shape with `year`, `month`,
  `planned_workouts`, `strava_activities`, `strava_error`
- `PlannedWorkoutRead` — stub for Phase 1 (empty list), full fields added in Phase 2
- Reuse existing `StravaActivity` schema from `app/schemas/strava.py`

### New Backend Files

| File | Description |
|------|-------------|
| `app/schemas/calendar.py` | Pydantic schemas for calendar responses |
| `app/routers/calendar.py` | FastAPI router, `GET /api/calendar/entries` |
| `app/services/calendar_service.py` | Orchestrates DB + Strava proxy call |
| `app/main.py` | Register the calendar router |

No new DB model or migration needed in Phase 1 (no planned workouts yet).

---

## Frontend

### New Route

`/calendar` added to `ROUTES` constant and `App.tsx` as a protected lazy-loaded route.

The Dashboard page gets a prominent "Go to Calendar" link/button pointing to `/calendar`.

### New Service: `src/services/calendarService.ts`

```typescript
// Minimal interface (Phase 1 shape)
interface CalendarEntries {
  year: number;
  month: number;
  planned_workouts: PlannedWorkout[];   // always [] in Phase 1
  strava_activities: StravaActivity[];
  strava_error: string | null;
}

const calendarService = {
  async getEntries(year: number, month: number): Promise<CalendarEntries | null>
}
```

Follows the same pattern as `stravaService.ts`: reads token from `authService.getToken()`,
calls `API_BASE_URL + API_ENDPOINTS.CALENDAR.ENTRIES`, returns null on error.

Add `CALENDAR.ENTRIES: '/api/calendar/entries'` to `src/constants/index.ts`.

### New TypeScript Types (`src/types/calendar.ts`)

```typescript
export interface StravaActivity {
  id: number;
  name: string;
  type: string;
  start_date: string;       // ISO 8601 UTC
  distance_m: number;
  moving_time_s: number;
  total_elevation_gain_m: number;
  average_heartrate?: number;
  average_watts?: number;
}

export interface PlannedWorkout {
  id: number;
  title: string;
  workout_type: string;
  planned_date: string;     // YYYY-MM-DD
  planned_duration_minutes?: number;
  planned_distance_km?: number;
  notes?: string;
}

export interface CalendarEntries {
  year: number;
  month: number;
  planned_workouts: PlannedWorkout[];
  strava_activities: StravaActivity[];
  strava_error: string | null;
}

export type CalendarEntry = StravaActivity | PlannedWorkout;
export type CalendarView = 'month' | 'week';
```

### Component Architecture

#### `CalendarPage.tsx` — page root, owns all state

```typescript
const [currentPeriod, setCurrentPeriod] = useState({ year, month }); // defaults to today
const [entries, setEntries] = useState<CalendarEntries | null>(null);
const [loading, setLoading] = useState(false);
const [selectedEntry, setSelectedEntry] = useState<CalendarEntry | null>(null);
```

Fetches on mount and on `currentPeriod` change. Passes data down to children as props.

#### `CalendarHeader.tsx`

Props: `year`, `month`, `onPrev`, `onNext`, `onToday`

Displays: `"May 2026"` label, left/right arrow buttons, "Today" button.
View toggle (month/week) is added in Phase 3 — not present yet.

#### `WeeklySummaryStrip.tsx`

Props: `activities: StravaActivity[]`, `weekStart: Date`

Filters activities to the given week, computes total distance (km) and total elevation (m),
renders a single row strip. In month view, shows the summary for the **current** week only.

#### `MonthView.tsx`

Props: `year`, `month`, `entries: CalendarEntries`, `onSelectEntry`

Renders a 5–6 row × 7 column grid. Each cell is a `CalendarDayCell`. Handles the
leading/trailing days from adjacent months (greyed out, not clickable).

#### `CalendarDayCell.tsx`

Props: `date: Date`, `activities: StravaActivity[]`, `plannedWorkouts: PlannedWorkout[]`,
`isCurrentMonth: boolean`, `isToday: boolean`, `onSelectEntry`

Renders the date number and a list of tiles. If there are more than 3 tiles, shows a
`+N more` overflow chip. Tiles are truncated to one line — no wrapping.

#### `StravaActivityTile.tsx`

Props: `activity: StravaActivity`, `onClick`

Renders: coloured chip using `--color-strava`, shows activity name and formatted distance.

#### `EntryDetailPanel.tsx` (Strava only in Phase 1)

Props: `entry: StravaActivity | null`, `onClose`

Slide-in panel from the right. Shows:
- Activity name, type, date
- Distance, duration, elevation
- Avg HR and avg watts (if available)
- "View on Strava" external link

Closes on backdrop click or an explicit close button.

### New Frontend Files

| File | Description |
|------|-------------|
| `src/components/layout/Calendar/CalendarPage.tsx` + `.module.css` | Page root |
| `src/components/layout/Calendar/CalendarHeader.tsx` + `.module.css` | Month nav |
| `src/components/layout/Calendar/WeeklySummaryStrip.tsx` + `.module.css` | Weekly totals |
| `src/components/layout/Calendar/MonthView.tsx` + `.module.css` | Month grid |
| `src/components/layout/Calendar/CalendarDayCell.tsx` + `.module.css` | Day cell |
| `src/components/layout/Calendar/StravaActivityTile.tsx` + `.module.css` | Strava chip |
| `src/components/layout/Calendar/EntryDetailPanel.tsx` + `.module.css` | Detail slide-in |
| `src/services/calendarService.ts` | API calls |
| `src/types/calendar.ts` | TypeScript types |
| `src/constants/index.ts` | Add `CALENDAR.ENTRIES` and `ROUTES.CALENDAR` |
| `src/App.tsx` | Add `/calendar` route |

All `.module.css` files use `var(--token)` exclusively — zero raw colour values.

---

## Definition of Done

- `GET /api/calendar/entries?year=2026&month=5` returns correct Strava activities for the month
- Month grid renders with correct day layout and Strava activity tiles on the right dates
- Clicking a tile opens the detail panel with correct data
- Navigating prev/next month fetches fresh data
- "Today" button returns to the current month
- Weekly summary strip shows correct totals for the current week
- Strava-not-connected state: calendar renders, no tiles, no error crash
- No raw hex values in any new `.module.css` file
