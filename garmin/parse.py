from datetime import date, datetime
from typing import Any

_DATETIME_FORMATS = ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S")


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("T", " ").replace("Z", "")
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def first_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, list):
        head = value[0] if value else None
        return head if isinstance(head, dict) else {}
    if isinstance(value, dict):
        return value
    return {}


def activity_row(payload: dict[str, Any]) -> dict[str, Any]:
    activity_type = payload.get("activityType")
    type_key = activity_type.get("typeKey") if isinstance(activity_type, dict) else None
    return {
        "activity_id": as_int(payload.get("activityId")),
        "name": payload.get("activityName"),
        "type_key": type_key,
        "start_time_local": parse_datetime(payload.get("startTimeLocal")),
        "start_time_gmt": parse_datetime(payload.get("startTimeGMT")),
        "distance_m": as_float(payload.get("distance")),
        "duration_s": as_float(payload.get("duration")),
        "moving_duration_s": as_float(payload.get("movingDuration")),
        "elevation_gain_m": as_float(payload.get("elevationGain")),
        "elevation_loss_m": as_float(payload.get("elevationLoss")),
        "average_speed_mps": as_float(payload.get("averageSpeed")),
        "max_speed_mps": as_float(payload.get("maxSpeed")),
        "average_hr": as_float(payload.get("averageHR")),
        "max_hr": as_float(payload.get("maxHR")),
        "calories": as_float(payload.get("calories")),
        "steps": as_int(payload.get("steps")),
        "average_cadence": as_float(payload.get("averageRunningCadenceInStepsPerMinute")),
        "max_cadence": as_float(payload.get("maxRunningCadenceInStepsPerMinute")),
        "average_power_w": as_float(payload.get("avgPower")),
        "max_power_w": as_float(payload.get("maxPower")),
        "normalized_power_w": as_float(payload.get("normPower")),
        "aerobic_training_effect": as_float(payload.get("aerobicTrainingEffect")),
        "anaerobic_training_effect": as_float(payload.get("anaerobicTrainingEffect")),
        "training_effect_label": payload.get("trainingEffectLabel"),
        "training_load": as_float(payload.get("activityTrainingLoad")),
        "vo2max": as_float(payload.get("vO2MaxValue")),
        "location_name": payload.get("locationName"),
        "raw": payload,
    }


def training_device(training_status: Any) -> dict[str, Any]:
    if not isinstance(training_status, dict):
        return {}
    recent = training_status.get("mostRecentTrainingStatus")
    latest = recent.get("latestTrainingStatusData") if isinstance(recent, dict) else None
    if isinstance(latest, dict):
        for value in latest.values():
            if isinstance(value, dict):
                return value
    return {}


def daily_metric_row(
    day: date,
    training_status: Any,
    readiness: Any,
    max_metrics: Any,
    hrv: Any,
) -> dict[str, Any]:
    device = training_device(training_status)
    load = device.get("acuteTrainingLoadDTO")
    load = load if isinstance(load, dict) else {}
    ready = first_mapping(readiness)
    metrics = first_mapping(max_metrics)
    generic = metrics.get("generic")
    generic = generic if isinstance(generic, dict) else {}
    cycling = metrics.get("cycling")
    cycling = cycling if isinstance(cycling, dict) else {}
    summary = hrv.get("hrvSummary") if isinstance(hrv, dict) else None
    summary = summary if isinstance(summary, dict) else {}
    return {
        "day": day,
        "training_status": device.get("trainingStatusFeedbackPhrase")
        or _text(device.get("trainingStatus")),
        "acwr": as_float(load.get("dailyAcuteChronicWorkloadRatio")),
        "acwr_status": load.get("acwrStatus"),
        "training_readiness": as_int(ready.get("score")),
        "readiness_level": ready.get("level"),
        "readiness_feedback": ready.get("feedbackShort"),
        "vo2max_running": as_float(generic.get("vo2MaxValue")),
        "vo2max_cycling": as_float(cycling.get("vo2MaxValue")),
        "hrv_weekly_avg": as_float(summary.get("weeklyAvg")),
        "hrv_last_night_avg": as_float(summary.get("lastNightAvg")),
        "hrv_status": summary.get("status"),
        "raw_training_status": training_status if isinstance(training_status, dict) else None,
        "raw_readiness": readiness if isinstance(readiness, (dict, list)) else None,
        "raw_max_metrics": max_metrics if isinstance(max_metrics, (dict, list)) else None,
        "raw_hrv": hrv if isinstance(hrv, dict) else None,
    }


def _text(value: Any) -> str | None:
    return str(value) if value is not None else None


def _stress(value: Any) -> int | None:
    n = as_int(value)
    return n if n is not None and n >= 0 else None


def wellness_row(day: date, stats: Any) -> dict[str, Any]:
    s = stats if isinstance(stats, dict) else {}
    return {
        "day": day,
        "resting_hr": as_int(s.get("restingHeartRate")),
        "steps": as_int(s.get("totalSteps")),
        "calories": as_int(s.get("totalKilocalories")),
        "stress_avg": _stress(s.get("averageStressLevel")),
        "body_battery_high": as_int(s.get("bodyBatteryHighestValue")),
        "body_battery_low": as_int(s.get("bodyBatteryLowestValue")),
        "intensity_moderate": as_int(s.get("moderateIntensityMinutes")),
        "intensity_vigorous": as_int(s.get("vigorousIntensityMinutes")),
        "raw_stats": s or None,
    }


def endurance_scores(payload: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    if not isinstance(payload, dict):
        return out
    group_map = payload.get("groupMap")
    if isinstance(group_map, dict):
        for day, value in group_map.items():
            if isinstance(value, dict):
                score = as_int(value.get("groupAverage"))
                if score is not None:
                    out[str(day)] = score
    return out


def hill_scores(payload: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    if not isinstance(payload, dict):
        return out
    for item in payload.get("hillScoreDTOList") or []:
        if isinstance(item, dict):
            day = item.get("calendarDate")
            score = as_int(item.get("overallScore"))
            if day is not None and score is not None:
                out[str(day)] = score
    return out


def race_prediction_row(entry: Any) -> dict[str, Any]:
    e = entry if isinstance(entry, dict) else {}
    return {
        "day": e.get("calendarDate"),
        "time_5k": as_int(e.get("time5K")),
        "time_10k": as_int(e.get("time10K")),
        "time_half": as_int(e.get("timeHalfMarathon")),
        "time_marathon": as_int(e.get("timeMarathon")),
        "raw": e or None,
    }
