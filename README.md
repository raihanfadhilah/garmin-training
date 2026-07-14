# garmin

Sync your Garmin Connect **running data** into a local SQLite database and explore
it in an interactive dashboard. Pulls activities, full per-second time series, and
daily training + wellness metrics, then serves a Streamlit dashboard on top.

Built on [`python-garminconnect`](https://github.com/cyberjunky/python-garminconnect).

## What it stores

- **`activities`** — one row per activity: distance, duration, heart rate, power,
  cadence, elevation, training effect/load, VO2 max, plus the full raw payload.
- **`activity_streams`** — the per-second time series for each activity (heart rate,
  pace, cadence, stride, ground contact, vertical oscillation, power…) and splits.
- **`daily_metrics`** — one row per day: training status, acute:chronic workload
  ratio, readiness, VO2 max, HRV, and wellness (resting HR, steps, stress, body
  battery, intensity minutes, endurance score, hill score), plus raw payloads.
- **`race_predictions`** — predicted 5K / 10K / half / marathon times per day.

Every table upserts on its primary key, so every sync is idempotent — safe to run
as often as you like. New model columns are auto-added to an existing database.

## Setup

```bash
uv sync
cp .env.example .env      # then edit with your Garmin email + password
```

## First login

Authenticate once. This handles MFA (if enabled on your account) and stores a
long-lived token under `~/.garmin/tokens`, so later syncs don't need your
password or another MFA code.

```bash
uv run garmin login
```

## Backfill (first run)

Pull your full history once — every activity, all time series, and daily metrics
from a start date:

```bash
uv run garmin backfill --since 2024-01-01
```

## Sync (ongoing)

```bash
uv run garmin sync                 # new activities + streams + last 30 days of metrics
uv run garmin sync --full          # re-fetch the entire activity history
uv run garmin sync --days 10       # narrower daily-metric window
uv run garmin sync --no-streams --no-wellness   # activities + training only
```

Activity sync is **incremental** by default: it pages newest-first and stops once
it reaches activities you already have. Time series, training, wellness, and race
predictions are pulled by default; use the `--no-*` flags to skip any of them.

## Dashboard

```bash
uv run garmin dashboard            # opens http://localhost:8501
```

An interactive Streamlit dashboard. The **Plan tracker** tab matches your actual
runs against the Madeira 25K training plan (`garmin/plan.py`) — long-run
progression, weekly volume plan-vs-actual, easy-pace discipline (the 80% rule),
vertical/elevation, a week-by-week table, and a per-week drill-down. Other tabs
cover consistency, aerobic engine, intensity/zones, form, recovery, race
predictions, and a per-run explorer (heart rate, pace, cadence, elevation across
the distance of any run).

## MCP server (use it from an AI client)

Expose your training data as tools any MCP client (Claude Desktop, Claude Code,
Cursor) can call — "analyze my last run", "how's this week going", "what's my 5K
prediction" become tool calls against your local database.

```bash
uv run garmin mcp                  # runs the stdio MCP server
```

Register it with Claude Code (works from any directory):

```bash
claude mcp add --scope user garmin -- /ABS/PATH/TO/training/.venv/bin/python -m garmin mcp
```

Point straight at the venv's Python rather than `uv run --directory ...` — `claude mcp add`
parses `--directory` as one of *its own* flags and silently drops the rest of the command,
leaving a server that can never start. The package is installed into the venv and the
database path is absolute, so no working directory is needed.

Verify it came up:

```bash
claude mcp list | grep garmin     # want: garmin ... - Connected
```

Then restart the client — MCP servers only connect at startup.

For Claude Desktop, add the same thing to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "garmin": {
      "command": "/ABS/PATH/TO/training/.venv/bin/python",
      "args": ["-m", "garmin", "mcp"]
    }
  }
}
```

Tools: `garmin_training_summary`, `garmin_recent_runs`, `garmin_analyze_run`,
`garmin_plan_status`, `garmin_week`, `garmin_race_predictions` (all read-only),
and `garmin_sync` (pulls fresh data from Garmin).

## Inspect

```bash
uv run garmin status               # what's in the DB, token state
uv run garmin activities --limit 20
```

The database is plain SQLite (`~/.garmin/garmin.db` by default), so you can also
open it with any SQLite tool or query it directly.

## Your own training plan

The plan lives in **`plans/madeira25k.json`** — plain JSON, no Python required. Edit
it, or copy it and point at your own:

```bash
GARMIN_PLAN=plans/my-marathon.json uv run garmin dashboard
```

```json
{
  "race": { "name": "Ultra X Madeira 25K", "date": "2026-11-01" },
  "settings": { "easy_hr_cap": 150, "benchmark_hr": 150, "benchmark_km": 7 },
  "weeks": [
    {
      "number": 1,
      "start": "2026-07-05",
      "end": "2026-07-11",
      "phase": "Base",
      "down_week": false,
      "note": "Optional note shown on the dashboard.",
      "sessions": [
        { "kind": "long", "label": "Long run 7 km", "day": 0, "km": 7 },
        { "kind": "easy", "label": "Easy run 4 km", "day": 3, "km": 4 },
        { "kind": "vertical", "label": "Vertical 20 min", "day": 2, "minutes": 20 }
      ]
    }
  ]
}
```

- **`day`** — 0 = Sunday, 1 = Monday … 6 = Saturday (7 = race day).
- **`km`** or **`minutes`** — give either, or both. A session with `minutes` is pushed to
  the watch as a *time* workout; `km` alone becomes a *distance* workout. Long days
  prescribed by time-on-feet should carry both: `minutes` is the target, `km` is only
  used for weekly-volume accounting.
- **`kind`** — drives how the session is tracked and whether it can be pushed to the
  watch. Runs: `easy`, `long`, `hill_tempo`, `strides`, `race`, `benchmark`. Everything
  else is tracked but not pushed: `vertical`, `eccentric`, `legs`, `push`, `pull`,
  `cp_test`.

Everything else — the dashboard, the `.ics` calendar, the workout push — reads from this
file, so editing the JSON is all you need to do.

## Export

```bash
uv run garmin export --out export   # activities, time series, daily metrics, plan
```

Writes `activities.csv`, `samples.csv` (every channel at 5s resolution, with a
`run`/`jog`/`walk`/`stop` gait label so walk breaks can be filtered out),
`daily.csv`, `race_predictions.csv`, and `plan.csv`. Useful for handing the data
to something else for analysis.

## Calendar

```bash
uv run garmin calendar --out plan.ics
```

Garmin Connect has no iOS/Google Calendar export, so this writes the plan as a
standard `.ics` feed — one all-day event per session, carrying the HR cap and a
days-to-race countdown. Email it to yourself and open it on your phone to import.

## Push workouts to the watch

```bash
uv run garmin push-workouts --since 2026-07-15 --until 2026-07-21           # dry run
uv run garmin push-workouts --since 2026-07-15 --until 2026-07-21 --confirm # writes
```

Builds the plan's runs as structured Garmin workouts with HR-zone targets,
uploads them, and schedules them on the given dates. They sync to the watch via
the phone, and the zone target makes the watch alert when you leave the zone.
Dry run unless `--confirm`; already-pushed workouts are skipped by name.

## Daily automatic sync (macOS launchd)

1. Edit `deploy/launchd.plist` and replace `REPLACE_WITH_PROJECT_PATH` with this
   project's absolute path (and check the `uv` path matches `which uv`).
2. Install and load it:

   ```bash
   cp deploy/launchd.plist ~/Library/LaunchAgents/com.user.garmin-sync.plist
   launchctl load ~/Library/LaunchAgents/com.user.garmin-sync.plist
   ```

It runs `garmin sync --days 10` daily at 07:00. Logs go to `deploy/sync.log`. Garmin's
refresh token is long-lived, but if it ever expires the job needs your
credentials — keep `GARMIN_EMAIL` / `GARMIN_PASSWORD` in `.env` so it can
re-authenticate unattended (MFA accounts will still require a manual
`garmin login`).

## Configuration

All settings are environment variables (or `.env`), prefix `GARMIN_`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `GARMIN_EMAIL` | – | Account email (needed for login) |
| `GARMIN_PASSWORD` | – | Account password (needed for login) |
| `GARMIN_TOKENSTORE` | `~/.garmin/tokens` | Where the auth token is cached |
| `GARMIN_DB_PATH` | `~/.garmin/garmin.db` | SQLite database location |
| `GARMIN_TRAINING_LOOKBACK_DAYS` | `30` | Default training sync window |
| `GARMIN_REQUEST_DELAY` | `0.3` | Delay between API calls (seconds) |
| `GARMIN_LOGIN_RETRIES` | `1` | Retries per login request (keep low to avoid 429) |

### Hitting a 429 on login?

Garmin rate-limits login requests per IP. If `garmin login` returns
`429 — IP rate limited`, stop retrying (each attempt makes it worse), wait
30–60 minutes, and try again from a non-VPN / home network. If it prompts for
an MFA code despite the 429s, enter a fresh code — a fallback login strategy
has usually reached the MFA step and can still complete.

## Layout

```
garmin/
  config.py     settings (env / .env)
  models.py     SQLAlchemy tables
  parse.py      Garmin JSON -> row transforms
  client.py     auth + paginated fetchers
  database.py   engine / session / auto-migration
  sync.py       idempotent upsert service
  analysis.py   time-series parsing, per-run metrics + intra-run detail
  plan.py       Madeira 25K plan + plan/actual adherence
  dashboard.py  Streamlit dashboard (Plotly)
  mcp.py        MCP server (7 tools for AI clients)
  cli.py        login / backfill / sync / dashboard / mcp / status / activities
```
