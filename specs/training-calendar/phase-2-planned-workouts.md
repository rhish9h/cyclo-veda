# Phase 2 — Planned Workouts CRUD

**Depends on: Phase 1 complete.**

---

## Goal

Let users create, edit, and delete planned workouts on the calendar. Planned workout tiles
appear alongside Strava activity tiles. Clicking a planned workout tile opens a detail panel
with edit and delete actions.

---

## Backend

### New DB Model: `planned_workouts`

```sql
CREATE TABLE planned_workouts (
    id                        SERIAL PRIMARY KEY,
    user_id                   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title                     VARCHAR(255) NOT NULL,
    workout_type              VARCHAR(50) NOT NULL,
    planned_date              DATE NOT NULL,
    planned_duration_minutes  INTEGER,
    planned_distance_km       NUMERIC(6, 2),
    notes                     TEXT,
    created_at                TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at                TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_planned_workouts_user_date ON planned_workouts(user_id, planned_date);
```

Workout type values (fixed enum for now — see Open Questions in overview):
`endurance`, `intervals`, `race`, `recovery`, `other`

### New Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/calendar/workouts` | Create a planned workout |
| `PUT` | `/api/calendar/workouts/{id}` | Update (owner check enforced) |
| `DELETE` | `/api/calendar/workouts/{id}` | Delete (owner check enforced) |

`GET /api/calendar/entries` from Phase 1 now returns real data in the `planned_workouts` array.

### New Backend Files

| File | Action |
|------|--------|
| `app/models/planned_workout.py` | New SQLAlchemy ORM model |
| `app/schemas/calendar.py` | Extend with `PlannedWorkoutCreate`, `PlannedWorkoutUpdate` |
| `app/repositories/planned_workout_repository.py` | CRUD repository |
| `app/services/calendar_service.py` | Add create/update/delete methods |
| `app/routers/calendar.py` | Add POST/PUT/DELETE routes |
| `migrations/versions/xxxx_add_planned_workouts.py` | Alembic migration |

---

## Frontend

### New Components

- **`PlannedWorkoutTile.tsx`** — chip using `--color-planned-workout`, shows title and workout type icon
- **`WorkoutFormModal.tsx`** — create/edit form with fields: title, workout type (select), date (date picker), duration, distance, notes. Used for both create (empty) and edit (pre-filled)
- **`EntryDetailPanel.tsx`** — extend Phase 1 panel to handle `PlannedWorkout` entries with Edit and Delete action buttons

### State additions to `CalendarPage`

```typescript
const [isFormOpen, setIsFormOpen] = useState(false);
const [editingWorkout, setEditingWorkout] = useState<PlannedWorkout | null>(null);
```

Clicking an empty day cell opens `WorkoutFormModal` pre-filled with that date.
Clicking a planned workout tile opens `EntryDetailPanel` in planned-workout mode.
Edit button in detail panel opens `WorkoutFormModal` pre-filled with workout data.

### `calendarService.ts` additions

```typescript
createWorkout(data: PlannedWorkoutCreate): Promise<PlannedWorkout | null>
updateWorkout(id: number, data: PlannedWorkoutUpdate): Promise<PlannedWorkout | null>
deleteWorkout(id: number): Promise<boolean>
```

---

## Key Decisions to Make Before Implementing

1. **Workout type enum**: confirm the fixed list or decide on user-extensibility (see overview Open Questions)
2. **Optimistic updates**: re-fetch the full month after a create/update/delete, or update local state immediately? Re-fetch is simpler and correct; optimistic is faster but adds complexity
3. **Date picker**: use a native `<input type="date">` (no dependency) or a library? Native is sufficient for MVP

---

## Definition of Done

- Users can create a planned workout from any future date cell
- Planned workout tiles appear on the correct date alongside Strava tiles
- Edit and Delete work correctly with owner checks enforced on the backend
- Form validates: title required, date required, duration/distance must be positive numbers if provided
- Optimistic or re-fetch strategy chosen and consistently applied
