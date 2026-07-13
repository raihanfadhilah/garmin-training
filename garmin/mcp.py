import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from sqlalchemy import select

from garmin import plan
from garmin.analysis import run_detail, run_metrics
from garmin.client import GarminClient
from garmin.config import Settings
from garmin.database import Database
from garmin.models import Activity, ActivityStream, DailyMetric, RacePrediction
from garmin.sync import SyncService

server = FastMCP("garmin_mcp")


def _read(title: str) -> ToolAnnotations:
    return ToolAnnotations(
        title=title,
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )


@dataclass(frozen=True)
class _Loaded:
    metrics: list[dict[str, Any]]
    progress: list[plan.WeekProgress]
    daily: list[dict[str, Any]]
    predictions: list[dict[str, Any]]


def _load(today: date) -> _Loaded:
    database = Database(Settings())
    with database.session() as session:
        activities = list(
            session.scalars(
                select(Activity)
                .where(Activity.type_key == "running")
                .order_by(Activity.start_time_local)
            ).all()
        )
        streams = {s.activity_id: s.details for s in session.scalars(select(ActivityStream)).all()}
        metrics = [
            run_metrics(a, streams.get(a.activity_id))
            for a in activities
            if (a.distance_m or 0) > 0
        ]
        daily = [
            {
                "day": d.day.isoformat(),
                "status": d.training_status,
                "readiness": d.training_readiness,
                "vo2": d.vo2max_running,
                "resting_hr": d.resting_hr,
                "endurance": d.endurance_score,
            }
            for d in session.scalars(select(DailyMetric).order_by(DailyMetric.day)).all()
        ]
        predictions = [
            {
                "day": p.day.isoformat(),
                "time_5k": p.time_5k,
                "time_10k": p.time_10k,
                "time_half": p.time_half,
                "time_marathon": p.time_marathon,
            }
            for p in session.scalars(select(RacePrediction).order_by(RacePrediction.day)).all()
        ]
    return _Loaded(metrics, plan.evaluate_all(metrics, today), daily, predictions)


def _run_summary(metric: dict[str, Any]) -> dict[str, Any]:
    return {
        "activity_id": metric["activity_id"],
        "date": metric["date"].isoformat() if metric.get("date") else None,
        "dist_km": metric["dist_km"],
        "pace_per_km": _mmss(metric["pace_s"]),
        "avg_hr": metric["avg_hr"],
        "max_hr": metric["max_hr"],
        "avg_cadence": metric["avg_cadence"],
        "decoupling_pct": metric["decoupling"],
        "hr_drift_bpm": metric["hr_drift"],
        "easy_pct": (metric["zones"][0] + metric["zones"][1]) if metric.get("zones") else None,
        "zones_pct": metric["zones"],
        "efficiency": metric["efficiency"],
        "training_load": metric["load"],
        "vo2max": metric["vo2"],
    }


def _mmss(seconds: float | None) -> str | None:
    if seconds is None:
        return None
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def _race_time(seconds: int | None) -> str | None:
    if seconds is None:
        return None
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def _week_view(progress: plan.WeekProgress) -> dict[str, Any]:
    week = progress.week
    schedule = []
    for offset in range(week.span_days + 1):
        day = week.start + timedelta(days=offset)
        sessions = [s.label for s in week.sessions if s.day == offset]
        schedule.append(
            {
                "date": day.isoformat(),
                "weekday": day.strftime("%a"),
                "sessions": sessions or ["Rest"],
            }
        )
    return {
        "week": week.number,
        "phase": week.phase,
        "dates": f"{week.start.isoformat()} to {week.end.isoformat()}",
        "down_week": week.down_week,
        "note": week.note or None,
        "planned": {
            "runs": week.planned_runs,
            "long_km": week.long_km,
            "total_km": week.planned_km,
        },
        "actual": {
            "runs": progress.actual_runs,
            "long_km": progress.long_km,
            "total_km": progress.actual_km,
            "easy_pct": progress.easy_pct,
            "climb_m": progress.elevation_m,
        },
        "status": progress.status,
        "schedule": schedule,
        "logged": [_run_summary(r) for r in progress.matched],
    }


@server.tool(name="garmin_training_summary", annotations=_read("Training summary"))
def garmin_training_summary() -> str:
    """High-level state of the runner's training: run count, VO2 max trend, average aerobic
    decoupling, endurance score, race countdown, and the current plan week/phase. Start here
    for an overview before drilling into specific runs or weeks.

    Returns a JSON object with totals, latest metrics, and the current plan position.
    """
    today = date.today()
    data = _load(today)
    vo2 = [m["vo2"] for m in data.metrics if m["vo2"] is not None]
    decos = [m["decoupling"] for m in data.metrics if m["decoupling"] is not None]
    endurance = [d["endurance"] for d in data.daily if d["endurance"] is not None]
    statuses = [d["status"] for d in data.daily if d["status"]]
    current = plan.current_week(today)
    result = {
        "runs_logged": len(data.metrics),
        "vo2max": {
            "latest": vo2[-1] if vo2 else None,
            "change": (vo2[-1] - vo2[0]) if len(vo2) > 1 else None,
        },
        "avg_decoupling_pct": round(sum(decos) / len(decos)) if decos else None,
        "endurance_score": endurance[-1] if endurance else None,
        "latest_training_status": statuses[-1] if statuses else None,
        "race": {
            "name": plan.RACE_NAME,
            "date": plan.RACE_DATE.isoformat(),
            "days_out": plan.days_to_race(today),
        },
        "current_week": current.number if current else None,
        "current_phase": current.phase if current else "off-plan",
    }
    return json.dumps(result, indent=2)


@server.tool(name="garmin_recent_runs", annotations=_read("Recent runs"))
def garmin_recent_runs(limit: int = 10) -> str:
    """List the most recent runs with their key metrics (distance, pace, heart rate, cadence,
    aerobic decoupling, HR drift, easy%, training load, VO2 max).

    Args:
        limit: Maximum number of runs to return, newest first (default 10).

    Returns a JSON array of run summaries. Use garmin_analyze_run for a deep per-run breakdown.
    """
    data = _load(date.today())
    runs = list(reversed(data.metrics))[: max(1, limit)]
    return json.dumps([_run_summary(m) for m in runs], indent=2)


@server.tool(name="garmin_analyze_run", annotations=_read("Analyze a run"))
def garmin_analyze_run(activity_id: int | None = None) -> str:
    """Deep analysis of a single run from its per-second time series: per-kilometer heart rate,
    0.5 km segment breakdown (pace/HR/cadence/walk%), detected walk breaks, and first-half vs
    second-half comparison that reveals cardiac drift (aerobic-base signal).

    Args:
        activity_id: The run's Garmin activity id. Omit to analyze the most recent run.

    Returns a JSON object combining the run summary with the intra-run detail. If the run has
    no stored time series, the detail sections will be empty.
    """
    database = Database(Settings())
    with database.session() as session:
        query = select(Activity).where(Activity.type_key == "running")
        if activity_id is not None:
            query = query.where(Activity.activity_id == activity_id)
        activity = session.scalars(query.order_by(Activity.start_time_local.desc())).first()
        if activity is None:
            return json.dumps(
                {"error": f"No running activity found for activity_id={activity_id}."}
            )
        stream_row = session.get(ActivityStream, activity.activity_id)
        details = stream_row.details if stream_row else None
        summary = _run_summary(run_metrics(activity, details))
        detail = run_detail(activity, details)
    return json.dumps({"summary": summary, "detail": detail}, indent=2)


@server.tool(name="garmin_plan_status", annotations=_read("Plan status"))
def garmin_plan_status() -> str:
    """Where the runner stands in the 17-week Madeira 25K plan: today's scheduled session,
    the current week's plan-vs-actual progress, and overall adherence to date.

    Returns a JSON object with the current week detail plus runs-done-vs-planned so far.
    """
    today = date.today()
    data = _load(today)
    current = plan.current_week(today)
    if current is None:
        return json.dumps({"status": "off-plan", "days_to_race": plan.days_to_race(today)})
    week_progress = next(p for p in data.progress if p.week.number == current.number)
    todays = [s.label for s in current.sessions if current.start + timedelta(days=s.day) == today]
    done = [p for p in data.progress if not p.is_future and p.actual_runs > 0]
    result = {
        "today": today.isoformat(),
        "todays_session": todays or ["Rest"],
        "days_to_race": plan.days_to_race(today),
        "runs_done_so_far": sum(p.actual_runs for p in done),
        "runs_planned_so_far": sum(p.week.planned_runs for p in data.progress if not p.is_future),
        "current_week": _week_view(week_progress),
    }
    return json.dumps(result, indent=2)


@server.tool(name="garmin_week", annotations=_read("Week detail"))
def garmin_week(number: int | None = None) -> str:
    """The day-by-day schedule and plan-vs-actual results for one plan week (1-17).

    Args:
        number: Plan week number 1-17. Omit for the current week.

    Returns a JSON object with the week's phase, day-by-day sessions, planned/actual totals,
    status, and the runs logged that week.
    """
    today = date.today()
    data = _load(today)
    current = plan.current_week(today)
    target = number if number is not None else (current.number if current else 1)
    match = [p for p in data.progress if p.week.number == target]
    if not match:
        return json.dumps({"error": f"Week {target} is out of range (plan has weeks 1-17)."})
    return json.dumps(_week_view(match[0]), indent=2)


@server.tool(name="garmin_race_predictions", annotations=_read("Race predictions"))
def garmin_race_predictions() -> str:
    """Garmin's predicted race times (5K, 10K, half, marathon) — the latest values and how
    they have trended, as human-readable times.

    Returns a JSON object with the latest prediction and the first stored one for comparison.
    """
    data = _load(date.today())
    if not data.predictions:
        return json.dumps({"error": "No race predictions stored. Run garmin_sync first."})
    latest, first = data.predictions[-1], data.predictions[0]
    keys = [
        ("5k", "time_5k"),
        ("10k", "time_10k"),
        ("half", "time_half"),
        ("marathon", "time_marathon"),
    ]
    result = {
        "as_of": latest["day"],
        "latest": {name: _race_time(latest[key]) for name, key in keys},
        "since": {"day": first["day"], **{name: _race_time(first[key]) for name, key in keys}},
    }
    return json.dumps(result, indent=2)


@server.tool(
    name="garmin_sync",
    annotations=ToolAnnotations(
        title="Sync from Garmin",
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def garmin_sync(days: int = 3) -> str:
    """Pull the latest data from Garmin Connect into the local database: new activities, their
    time series, and recent daily metrics + race predictions. Use when the runner has just
    logged a run and wants fresh data before analysis.

    Args:
        days: How many days back to refresh daily metrics/predictions (default 3).

    Returns a JSON object with counts of what was written, or an actionable error if login fails.
    """
    settings = Settings()
    client = GarminClient(settings)
    try:
        client.login()
    except Exception as error:
        return json.dumps(
            {"error": f"Garmin login failed: {error}. Run 'garmin login' to re-authenticate."}
        )
    service = SyncService(client, Database(settings))
    activities = service.sync_activities()
    streams = service.sync_streams()
    end = date.today()
    start = end - timedelta(days=max(1, days))
    training = service.sync_training(start, end)
    wellness = service.sync_wellness(start, end)
    predictions = service.sync_race_predictions(start, end)
    return json.dumps(
        {
            "activities_written": activities.activities_written,
            "streams_written": streams.streams_written,
            "training_days": training.days_written,
            "wellness_days": wellness.days_written,
            "predictions_written": predictions.predictions_written,
            "synced_at": datetime.now(UTC).isoformat(),
        }
    )


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
