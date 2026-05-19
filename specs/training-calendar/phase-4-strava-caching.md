# Phase 4 — Strava Activity Caching

**Depends on: Phase 3 complete.**

---

## Goal

Cache Strava activities in the local database so the calendar can display historical data
without hitting the Strava API on every page load. Enables future features like offline
access, advanced training load analytics (TSS, CTL/ATL/TSB), and querying activities across
arbitrary date ranges without Strava's pagination constraints.

---

## Scope (Outline)

### New DB Table: `strava_activities`

Stores a local copy of each Strava activity per user. Key columns:
`strava_activity_id` (unique, from Strava), `user_id`, `name`, `sport_type`,
`start_date_utc` (timestamptz), `distance_m`, `moving_time_s`,
`total_elevation_gain_m`, `average_heartrate`, `average_watts`, `synced_at`.

### Sync Strategy

Two options to decide before implementing:

- **On-demand sync**: when the user opens the calendar, fetch from DB first; if the last
  sync was > N minutes ago, fetch new activities from Strava and upsert into DB in the
  background.
- **Background job**: a scheduled task (e.g. Celery beat or APScheduler) polls Strava for
  each connected user at a fixed interval.

On-demand sync is simpler and sufficient for the user base at this stage. Background jobs
add infrastructure complexity (task queue, worker process).

### `GET /api/calendar/entries` change

Reads `strava_activities` from DB instead of calling Strava live. Falls back to a live
Strava call if the cache is empty or stale.

### New Backend Files

- `app/models/strava_activity.py` — SQLAlchemy ORM
- `app/repositories/strava_activity_repository.py` — upsert + date-range query
- `app/services/strava_sync_service.py` — sync logic (fetch from Strava API, upsert into DB)
- `migrations/versions/xxxx_add_strava_activities.py` — Alembic migration

---

## Considerations

- **Strava API rate limits**: 100 requests / 15 min, 1000 / day per token. An initial
  backfill of all historical activities must be rate-limit-aware (paginated, with delays).
- **Upsert strategy**: use `ON CONFLICT (strava_activity_id) DO UPDATE` to handle duplicate
  syncs cleanly.
- **Data freshness indicator**: the frontend may want to show "Last synced: X minutes ago"
  to set user expectations.

---

## Definition of Done (to be detailed in full spec)

- Calendar loads Strava activities from DB, not live API, on subsequent visits
- New activities from Strava are picked up within N minutes (TBD)
- Initial backfill completes without hitting Strava rate limits
- No regression in Phase 1–3 functionality
