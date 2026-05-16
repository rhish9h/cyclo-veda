# Phase 3 — Week View + Polish

**Depends on: Phase 2 complete.**

---

## Goal

Finish the calendar to a production-quality state. Add the week view, improve mobile
responsiveness, handle edge cases, and add the Strava disconnection banner. No new data
model changes.

---

## Features

### Week View

- New `WeekView.tsx` component: 7-column layout with time slots or all-day rows (TBD)
- View toggle added to `CalendarHeader` — `month | week` button group
- `CalendarPage` view state wired to toggle and persisted in `localStorage` so the user's
  preference survives page refresh
- `WeeklySummaryStrip` is always visible in week view (showing that week's totals)

### Mobile Responsiveness

- On screens narrower than `768px`, week view is the default (month view cramped on mobile)
- `CalendarDayCell` tiles stack vertically with reduced padding
- `EntryDetailPanel` renders as a bottom sheet instead of right slide-in on mobile
- `WorkoutFormModal` is full-screen on mobile

### Strava Disconnection Banner

- If `strava_error` is `"token_revoked"` in the API response, render a dismissible banner
  above the calendar: "Your Strava connection has expired. Reconnect in Settings."
- Link in banner goes to `/settings?section=connections`
- If `strava_error` is `"fetch_failed"`, show a softer banner: "Couldn't load Strava
  activities. They'll appear when the connection is restored."

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
- **Week view time slots**: decide between a simple all-day list per column (simpler) vs a
  timed grid with hour rows (more complex, only useful if activity start times matter to the user)
- **Prefetching**: only implement if the Phase 1/2 calendar feels noticeably slow in practice

---

## Definition of Done

- Week view renders correctly and the toggle persists across page refreshes
- App is usable and readable on a 375px wide screen
- Strava error banners appear and link to the correct page
- Loading skeletons visible during initial fetch and month navigation
- Today's date is always visually distinct
- No regression in Phase 1 or Phase 2 functionality
