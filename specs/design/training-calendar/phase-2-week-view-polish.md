# Phase 2 — Calendar Views + Polish

**Depends on: Phase 1 complete.**

---

## Goal

Finish the planned-workout calendar to a production-quality state. Add daily, weekly, and yearly views
to complement the monthly view from Phase 1, improve mobile responsiveness, and handle edge cases.
No new data model changes. Strava-specific features (connection banner, activity tiles) are added in Phase 3.

---

## Features

### Daily View

- New `DailyView.tsx` component: single-day detailed view with time slots or all-day list (TBD)
- Shows all entries for the selected date with expanded detail

### Weekly View

- New `WeekView.tsx` component: 7-column layout with time slots or all-day rows (TBD)
- Shows the full week with entries for each day

### Yearly View

- New `YearlyView.tsx` component: 12-month grid overview
- Shows month-level summary (total rides, total distance) for each month
- Clicking a month navigates to that month in monthly view

### View Toggle

- View selector added to `CalendarHeader` — `day | week | month | year` button group
- `CalendarPage` view state wired to selector and persisted in `localStorage` so the user's
  preference survives page refresh
- `PeriodSummaryStrip` is always visible, showing totals for the visible period

### Mobile Responsiveness

- On screens narrower than `768px`, daily view is the default (month view cramped on mobile)
- On screens 768px–1024px, weekly view is the default
- `CalendarDayCell` tiles stack vertically with reduced padding
- `EntryDetailPanel` renders as a bottom sheet instead of right slide-in on mobile
- `WorkoutFormModal` is full-screen on mobile

### UX Polish

- Loading skeleton for calendar grid while data is fetching (prevents layout shift)
- Empty state for days with no entries — subtle dashed border or greyed text
- Keyboard navigation: arrow keys move between day cells, Enter opens detail panel
- `today` cell highlighted with a distinct ring using `--color-primary`
- Tile overflow (`+N more`) expands to show all tiles on click, not just navigate

### Performance

- Prefetch adjacent months (prev and next) in the background after the current month loads,
  so navigating feels instant
- `useMemo` to derive per-day entry maps from the flat activities/workouts arrays, avoiding
  re-computation on every render

---

## Considerations

- **Keyboard navigation** scope: basic arrow key support only — full ARIA calendar widget
  pattern is out of scope for this phase
- **Daily/weekly view time slots**: decide between a simple all-day list (simpler) vs a
  timed grid with hour rows (more complex, only useful if activity start times matter to the user)
- **Prefetching**: only implement if the Phase 1 calendar feels noticeably slow in practice
- **Yearly view data**: can be computed from existing monthly data without additional API calls

---

## Definition of Done

- Daily, weekly, and yearly views render correctly and the view selector persists across page refreshes
- App is usable and readable on a 375px wide screen (daily view default)
- Loading skeletons visible during initial fetch and period navigation
- Today's date is always visually distinct
- Yearly view shows accurate month-level summaries
- No regression in Phase 1 functionality
