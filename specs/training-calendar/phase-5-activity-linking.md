# Phase 5 — Planned → Actual Activity Linking

**Depends on: Phase 4 complete.**

---

## Goal

Let users link a completed Strava activity to a planned workout entry. This closes the
loop between planning and execution, enabling compliance tracking — how often does the
user actually complete what they planned?

---

## Scope (Outline)

### Data Model Change

Add an optional `strava_activity_id` foreign key to `planned_workouts`:

```sql
ALTER TABLE planned_workouts
  ADD COLUMN strava_activity_id BIGINT REFERENCES strava_activities(strava_activity_id);
```

A planned workout can be linked to at most one Strava activity. A Strava activity can be
linked to at most one planned workout (enforced via unique constraint).

### User Flow

1. User opens a planned workout's detail panel
2. If the planned workout's date has passed and there are unlinked Strava activities on
   that day, a "Link to activity" button appears
3. Tapping it shows a small picker listing Strava activities from the same day
4. User selects one — the link is saved; the detail panel updates to show both planned
   and actual stats side by side (planned distance vs actual, planned duration vs actual)

### Compliance View (future scope within this phase)

- A summary somewhere (Dashboard widget or Calendar header strip) showing:
  workouts planned this week vs completed (linked)
- Colour-coded tiles: planned + linked = green, planned + unlinked + past date = amber,
  planned + future = default

### New Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/calendar/workouts/{id}/link` | Link a Strava activity to a planned workout |
| `DELETE` | `/api/calendar/workouts/{id}/link` | Unlink |

---

## Considerations

- **Ambiguity**: what if a user rode twice on a planned workout day? The picker shows all
  unlinked activities from that day so the user can choose.
- **Auto-linking**: could auto-suggest a link when a Strava activity's sport type and date
  match a planned workout. Purely a suggestion — never auto-link without user confirmation.
- **Retroactive linking**: users should be able to link activities to planned workouts from
  any past date, not just today.

---

## Definition of Done (to be detailed in full spec)

- Users can link and unlink a planned workout to a Strava activity
- Detail panel shows planned vs actual stats when linked
- Unique constraint prevents one Strava activity from being linked to multiple planned workouts
- No regression in Phase 1–4 functionality
