# Phase 1 — Planned Workouts Calendar

**Depends on: Phase 0 complete.**

---

## Goal

A fully working training calendar built entirely around user-created planned workouts —
no Strava integration yet. Users can view a monthly calendar, create/edit/delete workouts,
and choose from system-default or their own custom workout types. This is the MVP that
proves the full stack end-to-end.

---

## Backend

### New DB Models

#### `workout_types`

```sql
CREATE TABLE workout_types (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL,
    is_system   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, name)
);
```

Seeded system defaults (via migration, `user_id = NULL`, `is_system = TRUE`):
`endurance`, `intervals`, `race`, `recovery`, `other`

Rules:
- Users can read all system defaults + their own custom types
- Users can create and delete their own custom types only
- System defaults cannot be modified or deleted

#### `planned_workouts`

```sql
CREATE TABLE planned_workouts (
    id                       SERIAL PRIMARY KEY,
    user_id                  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workout_type_id          INTEGER NOT NULL REFERENCES workout_types(id),
    title                    VARCHAR(255) NOT NULL,
    planned_date             DATE NOT NULL,
    planned_duration_minutes INTEGER,
    planned_distance_km      NUMERIC(6, 2),
    notes                    TEXT,
    created_at               TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at               TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_planned_workouts_user_date ON planned_workouts(user_id, planned_date);
```

All timestamps are UTC. `planned_date` is a `DATE` — no timezone, displayed as-is.

### New Endpoints

#### Calendar entries

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/calendar/entries?year=YYYY&month=MM` | Returns planned workouts for the month. `strava_activities` is always `[]` until Phase 3. |

#### Planned workouts CRUD

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/calendar/workouts` | Create a planned workout |
| `PUT` | `/api/calendar/workouts/{id}` | Update (owner check enforced) |
| `DELETE` | `/api/calendar/workouts/{id}` | Delete (owner check enforced) |

#### Workout types

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/calendar/workout-types` | Returns system defaults + user's custom types |
| `POST` | `/api/calendar/workout-types` | Create a custom type (name required) |
| `DELETE` | `/api/calendar/workout-types/{id}` | Delete a custom type (own types only) |

### Response Schemas (`app/schemas/calendar.py`)

```python
class WorkoutTypeRead(BaseModel):
    id: int
    name: str
    is_system: bool

class PlannedWorkoutRead(BaseModel):
    id: int
    workout_type: WorkoutTypeRead
    title: str
    planned_date: date
    planned_duration_minutes: int | None
    planned_distance_km: float | None
    notes: str | None

class PlannedWorkoutCreate(BaseModel):
    workout_type_id: int
    title: str
    planned_date: date
    planned_duration_minutes: int | None = None
    planned_distance_km: float | None = None
    notes: str | None = None

class PlannedWorkoutUpdate(BaseModel):  # all optional
    workout_type_id: int | None = None
    title: str | None = None
    planned_date: date | None = None
    planned_duration_minutes: int | None = None
    planned_distance_km: float | None = None
    notes: str | None = None

class CalendarEntriesResponse(BaseModel):
    year: int
    month: int
    planned_workouts: list[PlannedWorkoutRead]
    strava_activities: list  # always [] until Phase 3
    strava_error: str | None = None
```

### New Backend Files

| File | Description |
|------|-------------|
| `app/models/planned_workout.py` | SQLAlchemy ORM for `planned_workouts` |
| `app/models/workout_type.py` | SQLAlchemy ORM for `workout_types` |
| `app/schemas/calendar.py` | All Pydantic schemas above |
| `app/repositories/planned_workout_repository.py` | CRUD for planned workouts |
| `app/repositories/workout_type_repository.py` | CRUD for workout types |
| `app/services/calendar_service.py` | Business logic (owner checks, type resolution) |
| `app/routers/calendar.py` | All calendar endpoints |
| `app/main.py` | Register calendar router |
| `migrations/versions/xxxx_add_workout_types.py` | Migration: `workout_types` + seed defaults |
| `migrations/versions/xxxx_add_planned_workouts.py` | Migration: `planned_workouts` |

---

## Frontend

### New Route

`/calendar` added to `ROUTES` constant and registered in `App.tsx` as a protected lazy-loaded
route.

### Dashboard Button

A "Go to Training Calendar →" button/link added to the Dashboard content area. Uses
`--color-primary` styling. Marked with a `{/* TODO: replace with mini calendar widget */}`
comment for future scope.

### New TypeScript Types (`src/types/calendar.ts`)

```typescript
export interface WorkoutType {
  id: number;
  name: string;
  is_system: boolean;
}

export interface PlannedWorkout {
  id: number;
  workout_type: WorkoutType;
  title: string;
  planned_date: string;           // YYYY-MM-DD
  planned_duration_minutes?: number;
  planned_distance_km?: number;
  notes?: string;
}

export interface CalendarEntries {
  year: number;
  month: number;
  planned_workouts: PlannedWorkout[];
  strava_activities: never[];     // always [] until Phase 3
  strava_error: string | null;
}

export type CalendarView = 'month' | 'week';  // 'week' used in Phase 2
```

### New Service (`src/services/calendarService.ts`)

```typescript
const calendarService = {
  getEntries(year: number, month: number): Promise<CalendarEntries | null>,
  getWorkoutTypes(): Promise<WorkoutType[]>,
  createWorkout(data: PlannedWorkoutCreate): Promise<PlannedWorkout | null>,
  updateWorkout(id: number, data: PlannedWorkoutUpdate): Promise<PlannedWorkout | null>,
  deleteWorkout(id: number): Promise<boolean>,
  createWorkoutType(name: string): Promise<WorkoutType | null>,
  deleteWorkoutType(id: number): Promise<boolean>,
}
```

Follows the same pattern as `stravaService.ts`. Add `CALENDAR` block to `API_ENDPOINTS`
in `src/constants/index.ts`.

### Component Architecture

#### `CalendarPage.tsx` — page root, owns all state

```typescript
const [currentPeriod, setCurrentPeriod] = useState({ year, month }); // today's month
const [entries, setEntries] = useState<CalendarEntries | null>(null);
const [workoutTypes, setWorkoutTypes] = useState<WorkoutType[]>([]);
const [loading, setLoading] = useState(false);
const [selectedWorkout, setSelectedWorkout] = useState<PlannedWorkout | null>(null);
const [isFormOpen, setIsFormOpen] = useState(false);
const [editingWorkout, setEditingWorkout] = useState<PlannedWorkout | null>(null);
const [preselectedDate, setPreselectedDate] = useState<string | null>(null);
```

Fetches entries + workout types on mount. Re-fetches entries on `currentPeriod` change.
After any create/update/delete, re-fetches the current month (simple, correct, no optimistic
state needed at this stage).

Clicking an empty day cell → opens `WorkoutFormModal` with that date pre-filled.
Clicking a planned workout tile → opens `EntryDetailPanel`.
Edit button in detail panel → closes panel, opens `WorkoutFormModal` pre-filled.

#### `CalendarHeader.tsx`

Props: `year`, `month`, `onPrev`, `onNext`, `onToday`

Renders month/year label (`"May 2026"`), arrow buttons, and "Today" button. No view toggle
yet (added in Phase 2).

#### `WeeklySummaryStrip.tsx`

Props: `plannedWorkouts: PlannedWorkout[]`, `weekStart: Date`

Filters workouts to the given week (Mon–Sun). Shows total planned distance (km) and total
planned duration (hours + minutes). In month view, shows the summary for **today's week**.

#### `MonthView.tsx`

Props: `year`, `month`, `entries: CalendarEntries`, `onSelectWorkout`, `onDayCellClick`

5–6 row × 7 column grid. Each cell is a `CalendarDayCell`. Leading/trailing days from
adjacent months are greyed out and not interactive.

#### `CalendarDayCell.tsx`

Props: `date: Date`, `plannedWorkouts: PlannedWorkout[]`, `isCurrentMonth: boolean`,
`isToday: boolean`, `onSelectWorkout`, `onClick`

Renders date number and workout tiles. Shows `+N more` overflow chip if > 3 tiles.
Clicking the cell background (not a tile) fires `onClick` to open the create form.

#### `PlannedWorkoutTile.tsx`

Props: `workout: PlannedWorkout`, `onClick`

Chip using `--color-planned-workout`. Shows workout type name and title, truncated to one
line.

#### `EntryDetailPanel.tsx`

Props: `workout: PlannedWorkout | null`, `onClose`, `onEdit`, `onDelete`

Right slide-in panel. Shows all workout fields. Edit button fires `onEdit` (opens form).
Delete button shows an inline confirmation before firing `onDelete`. Closes on backdrop click
or close button.

#### `WorkoutFormModal.tsx`

Props: `initialDate?: string`, `workout?: PlannedWorkout`, `workoutTypes: WorkoutType[]`,
`onSave`, `onClose`

Used for both create (no `workout` prop) and edit (`workout` prop pre-fills all fields).
Fields: title (text), workout type (select — system + custom + "＋ Add custom type..." option),
date (native `<input type="date">`), duration (number, minutes), distance (number, km), notes
(textarea). Inline "Add custom type" flow: shows a small text input to name the new type, calls
`calendarService.createWorkoutType`, then selects the new type automatically.

Validates: title required, date required, duration and distance must be positive if provided.

### New Frontend Files

| File | Description |
|------|-------------|
| `src/components/layout/Calendar/CalendarPage.tsx` + `.module.css` | Page root |
| `src/components/layout/Calendar/CalendarHeader.tsx` + `.module.css` | Month navigation |
| `src/components/layout/Calendar/WeeklySummaryStrip.tsx` + `.module.css` | Weekly totals |
| `src/components/layout/Calendar/MonthView.tsx` + `.module.css` | Month grid |
| `src/components/layout/Calendar/CalendarDayCell.tsx` + `.module.css` | Day cell |
| `src/components/layout/Calendar/PlannedWorkoutTile.tsx` + `.module.css` | Workout chip |
| `src/components/layout/Calendar/EntryDetailPanel.tsx` + `.module.css` | Detail slide-in |
| `src/components/layout/Calendar/WorkoutFormModal.tsx` + `.module.css` | Create/edit form |
| `src/services/calendarService.ts` | API calls |
| `src/types/calendar.ts` | TypeScript types |
| `src/constants/index.ts` | Add `ROUTES.CALENDAR` and `API_ENDPOINTS.CALENDAR` |
| `src/App.tsx` | Add `/calendar` route |
| `src/components/layout/Dashboard/Dashboard.tsx` | Add calendar navigation button |

All `.module.css` files use `var(--token)` exclusively.

---

## Definition of Done

- `GET /api/calendar/entries?year=&month=` returns planned workouts for the month
- `GET /api/calendar/workout-types` returns system defaults + user's custom types
- Users can create, edit, and delete planned workouts via the form modal
- Users can create custom workout types inline from the form, and they persist across sessions
- Workout tiles appear on the correct date in the month grid
- Clicking a tile opens the detail panel with correct data; Edit and Delete work
- Navigating prev/next month fetches fresh data; "Today" returns to the current month
- Weekly summary strip shows correct totals
- Clicking an empty day cell opens the create form with that date pre-filled
- Dashboard has a "Go to Training Calendar" button that navigates to `/calendar`
- No raw hex values in any new `.module.css` file
