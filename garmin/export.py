import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import select

from garmin import analysis
from garmin.database import Database
from garmin.models import Activity, ActivityStream, DailyMetric, RacePrediction

SAMPLE_STEP_SECONDS = 5
WALK_SPEED = 1.6
RUN_SPEED = 2.0

ACTIVITY_COLUMNS = [
    "activity_id",
    "date",
    "name",
    "type",
    "distance_km",
    "duration_min",
    "moving_min",
    "avg_pace_s_per_km",
    "avg_hr",
    "max_hr",
    "avg_cadence",
    "avg_power",
    "avg_stride_m",
    "avg_gct_ms",
    "avg_vertical_osc_mm",
    "elevation_gain_m",
    "elevation_loss_m",
    "calories",
    "aerobic_te",
    "anaerobic_te",
    "vo2max",
]

SAMPLE_COLUMNS = [
    "activity_id",
    "date",
    "elapsed_s",
    "distance_m",
    "hr",
    "speed_ms",
    "pace_s_per_km",
    "grade_adj_speed_ms",
    "cadence_spm",
    "power_w",
    "stride_m",
    "gct_ms",
    "vertical_osc_mm",
    "vertical_ratio",
    "elevation_m",
    "moving",
]

DAILY_COLUMNS = [
    "day",
    "resting_hr",
    "vo2max_running",
    "training_status",
    "acwr",
    "acwr_status",
    "training_readiness",
    "endurance_score",
    "hill_score",
    "body_battery_high",
    "body_battery_low",
    "stress_avg",
    "hrv_weekly_avg",
    "hrv_last_night_avg",
    "hrv_status",
    "intensity_moderate",
    "intensity_vigorous",
    "steps",
]


@dataclass(frozen=True)
class ExportResult:
    activities: int
    samples: int
    days: int
    predictions: int
    files: list[Path]


def _get(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = raw.get(key)
        if value is not None:
            return value
    return None


def _activity_row(activity: Activity) -> dict[str, Any]:
    raw = activity.raw or {}
    km = (activity.distance_m or 0) / 1000
    duration = activity.duration_s or 0
    moving = _get(raw, "movingDuration") or duration
    pace = (moving / km) if km else None
    return {
        "activity_id": activity.activity_id,
        "date": activity.start_time_local.isoformat() if activity.start_time_local else "",
        "name": activity.name or "",
        "type": activity.type_key or "",
        "distance_km": round(km, 3),
        "duration_min": round(duration / 60, 2),
        "moving_min": round(moving / 60, 2),
        "avg_pace_s_per_km": round(pace, 1) if pace else "",
        "avg_hr": activity.average_hr or "",
        "max_hr": activity.max_hr or "",
        "avg_cadence": _get(raw, "averageRunningCadenceInStepsPerMinute") or "",
        "avg_power": _get(raw, "avgPower") or "",
        "avg_stride_m": _get(raw, "avgStrideLength") or "",
        "avg_gct_ms": _get(raw, "avgGroundContactTime") or "",
        "avg_vertical_osc_mm": _get(raw, "avgVerticalOscillation") or "",
        "elevation_gain_m": _get(raw, "elevationGain") or "",
        "elevation_loss_m": _get(raw, "elevationLoss") or "",
        "calories": _get(raw, "calories") or "",
        "aerobic_te": activity.aerobic_training_effect or "",
        "anaerobic_te": _get(raw, "anaerobicTrainingEffect") or "",
        "vo2max": _get(raw, "vO2MaxValue") or "",
    }


def _gait(speed: float) -> str:
    if speed >= RUN_SPEED:
        return "run"
    return "walk" if speed < WALK_SPEED else "jog"


def _sample_rows(activity: Activity, details: dict[str, Any]) -> list[dict[str, Any]]:
    positions = analysis.index_map(details)
    channels = {
        "elapsed_s": "sumDuration",
        "distance_m": "sumDistance",
        "hr": "directHeartRate",
        "speed_ms": "directSpeed",
        "grade_adj_speed_ms": "directGradeAdjustedSpeed",
        "cadence_spm": "directDoubleCadence",
        "power_w": "directPower",
        "stride_m": "directStrideLength",
        "gct_ms": "directGroundContactTime",
        "vertical_osc_mm": "directVerticalOscillation",
        "vertical_ratio": "directVerticalRatio",
        "elevation_m": "directElevation",
    }
    data = {name: analysis.stream(details, positions, key) for name, key in channels.items()}
    length = max((len(v) for v in data.values()), default=0)
    day = activity.start_time_local.date().isoformat() if activity.start_time_local else ""

    rows: list[dict[str, Any]] = []
    last_emitted: float | None = None
    for i in range(length):
        elapsed = data["elapsed_s"][i] if i < len(data["elapsed_s"]) else None
        if not isinstance(elapsed, (int, float)):
            continue
        if last_emitted is not None and elapsed - last_emitted < SAMPLE_STEP_SECONDS:
            continue
        last_emitted = float(elapsed)
        row: dict[str, Any] = {"activity_id": activity.activity_id, "date": day}
        for name in channels:
            value = data[name][i] if i < len(data[name]) else None
            row[name] = round(value, 3) if isinstance(value, (int, float)) else ""
        speed = data["speed_ms"][i] if i < len(data["speed_ms"]) else None
        if isinstance(speed, (int, float)) and speed > 0:
            row["pace_s_per_km"] = round(1000.0 / speed, 1)
            row["moving"] = _gait(speed)
        else:
            row["pace_s_per_km"] = ""
            row["moving"] = "stop"
        rows.append(row)
    return rows


def _daily_row(metric: DailyMetric) -> dict[str, Any]:
    row: dict[str, Any] = {"day": metric.day.isoformat()}
    for column in DAILY_COLUMNS[1:]:
        value = getattr(metric, column)
        row[column] = value if value is not None else ""
    return row


def _write(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(database: Database, out_dir: Path, runs_only: bool = True) -> ExportResult:
    out_dir.mkdir(parents=True, exist_ok=True)
    activity_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    daily_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []

    with database.session() as session:
        query = select(Activity).order_by(Activity.start_time_local)
        for activity in session.scalars(query):
            if runs_only and "run" not in (activity.type_key or ""):
                continue
            activity_rows.append(_activity_row(activity))
            stream_row = session.get(ActivityStream, activity.activity_id)
            if stream_row and stream_row.details:
                sample_rows.extend(_sample_rows(activity, stream_row.details))

        for metric in session.scalars(select(DailyMetric).order_by(DailyMetric.day)):
            daily_rows.append(_daily_row(metric))

        for prediction in session.scalars(select(RacePrediction).order_by(RacePrediction.day)):
            prediction_rows.append(
                {
                    "day": prediction.day.isoformat(),
                    "race_5k_s": prediction.time_5k or "",
                    "race_10k_s": prediction.time_10k or "",
                    "race_half_s": prediction.time_half or "",
                    "race_marathon_s": prediction.time_marathon or "",
                }
            )

    files = [
        out_dir / "activities.csv",
        out_dir / "samples.csv",
        out_dir / "daily.csv",
        out_dir / "race_predictions.csv",
    ]
    _write(files[0], ACTIVITY_COLUMNS, activity_rows)
    _write(files[1], SAMPLE_COLUMNS, sample_rows)
    _write(files[2], DAILY_COLUMNS, daily_rows)
    _write(
        files[3],
        ["day", "race_5k_s", "race_10k_s", "race_half_s", "race_marathon_s"],
        prediction_rows,
    )
    return ExportResult(
        activities=len(activity_rows),
        samples=len(sample_rows),
        days=len(daily_rows),
        predictions=len(prediction_rows),
        files=files,
    )


def today() -> date:
    return date.today()
