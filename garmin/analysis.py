from statistics import mean
from typing import Any

from garmin.models import Activity


def _num(value: Any) -> bool:
    return isinstance(value, (int, float))


def _clean(values: list[Any]) -> list[float]:
    return [float(v) for v in values if _num(v)]


def index_map(details: dict[str, Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for descriptor in details.get("metricDescriptors", []):
        key = descriptor.get("key")
        position = descriptor.get("metricsIndex")
        if isinstance(key, str) and isinstance(position, int):
            out[key] = position
    return out


def stream(details: dict[str, Any], positions: dict[str, int], key: str) -> list[Any]:
    position = positions.get(key)
    if position is None:
        return []
    out: list[Any] = []
    for row in details.get("activityDetailMetrics", []):
        values = row.get("metrics") or []
        out.append(values[position] if position < len(values) else None)
    return out


def pace_seconds(speed: float | None) -> float | None:
    if not speed or speed <= 0:
        return None
    return 1000.0 / speed


def zone_percentages(activity: Activity) -> list[int]:
    zones = [activity.raw.get(f"hrTimeInZone_{i}") or 0 for i in range(1, 6)]
    total = sum(zones) or 1
    return [round(z / total * 100) for z in zones]


def run_metrics(activity: Activity, details: dict[str, Any] | None) -> dict[str, Any]:
    detail = details or {}
    positions = index_map(detail)
    hr = stream(detail, positions, "directHeartRate")
    speed = stream(detail, positions, "directSpeed")
    cadence = stream(detail, positions, "directDoubleCadence")
    gct = stream(detail, positions, "directGroundContactTime")
    vertical = stream(detail, positions, "directVerticalOscillation")
    perf = stream(detail, positions, "directPerformanceCondition")

    n = len(hr)
    moving = [i for i in range(n) if _num(speed[i]) and speed[i] > 0.6 and _num(hr[i]) and hr[i]]
    decoupling: float | None = None
    drift: float | None = None
    if len(moving) > 20:
        half = len(moving) // 2
        first, second = moving[:half], moving[half:]
        ef_first = mean(speed[i] for i in first) / mean(hr[i] for i in first)
        ef_second = mean(speed[i] for i in second) / mean(hr[i] for i in second)
        decoupling = round((ef_first - ef_second) / ef_first * 100, 1)
        drift = round(mean(hr[i] for i in second) - mean(hr[i] for i in first), 1)

    cadence_moving = _clean([cadence[i] for i in moving])
    cadence_fade: float | None = None
    if len(cadence_moving) > 20:
        third = len(cadence_moving) // 3
        cadence_fade = round(mean(cadence_moving[-third:]) - mean(cadence_moving[:third]), 1)

    speed_mps = activity.average_speed_mps
    efficiency = (
        round(speed_mps / activity.average_hr * 100, 3)
        if speed_mps and activity.average_hr
        else None
    )

    return {
        "activity_id": activity.activity_id,
        "date": activity.start_time_local,
        "name": activity.name,
        "type_key": activity.type_key,
        "dist_km": round((activity.distance_m or 0) / 1000, 2),
        "dur_min": round((activity.duration_s or 0) / 60, 1),
        "pace_s": pace_seconds(speed_mps),
        "avg_hr": int(activity.average_hr) if activity.average_hr else None,
        "max_hr": int(activity.max_hr) if activity.max_hr else None,
        "avg_cadence": round(mean(cadence_moving)) if cadence_moving else activity.average_cadence,
        "cadence_fade": cadence_fade,
        "gct": round(mean(_clean(gct))) if _clean(gct) else None,
        "vertical_osc": round(mean(_clean(vertical)), 1) if _clean(vertical) else None,
        "aerobic_te": activity.aerobic_training_effect,
        "load": round(activity.training_load) if activity.training_load else None,
        "vo2": activity.vo2max,
        "elev_gain": round(activity.elevation_gain_m) if activity.elevation_gain_m else 0,
        "efficiency": efficiency,
        "decoupling": decoupling,
        "hr_drift": drift,
        "perf_cond": round(mean(_clean(perf))) if _clean(perf) else None,
        "zones": zone_percentages(activity),
    }


def _pace(speed: float | None) -> str | None:
    seconds = pace_seconds(speed)
    if seconds is None:
        return None
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def run_detail(
    activity: Activity, details: dict[str, Any] | None, segment_km: float = 0.5
) -> dict[str, Any]:
    detail = details or {}
    positions = index_map(detail)
    distance = stream(detail, positions, "sumDistance")
    hr = stream(detail, positions, "directHeartRate")
    speed = stream(detail, positions, "directSpeed")
    cadence = stream(detail, positions, "directDoubleCadence")
    duration = stream(detail, positions, "sumDuration")
    n = len(distance)
    total_km = (activity.distance_m or 0) / 1000

    km_hr = []
    for marker in range(1, int(total_km) + 1):
        near = [i for i in range(n) if _num(distance[i]) and abs(distance[i] - marker * 1000) < 60]
        if near and _num(hr[near[0]]):
            km_hr.append({"km": marker, "hr": round(hr[near[0]])})

    segments = []
    for bucket in range(int(total_km / segment_km) + 1):
        low, high = bucket * segment_km * 1000, (bucket + 1) * segment_km * 1000
        idx = [i for i in range(n) if _num(distance[i]) and low <= distance[i] < high]
        if not idx:
            continue
        heart = [hr[i] for i in idx if _num(hr[i])]
        running = [speed[i] for i in idx if _num(speed[i]) and speed[i] > 1.6]
        turns = [cadence[i] for i in idx if _num(cadence[i]) and cadence[i] > 120]
        walking = [i for i in idx if _num(speed[i]) and speed[i] < 1.6]
        segments.append(
            {
                "from_km": round(low / 1000, 1),
                "to_km": round(high / 1000, 1),
                "avg_hr": round(mean(heart)) if heart else None,
                "pace": _pace(mean(running)) if running else None,
                "cadence": round(mean(turns)) if turns else None,
                "walk_pct": round(len(walking) / len(idx) * 100),
            }
        )

    walk_breaks = []
    start: tuple[Any, Any] | None = None
    for i in range(n):
        slow = _num(speed[i]) and speed[i] < 1.6
        if slow and start is None:
            start = (duration[i], distance[i])
        elif not slow and start is not None:
            seconds = (duration[i] or 0) - (start[0] or 0)
            if seconds >= 8:
                walk_breaks.append(
                    {"at_km": round((start[1] or 0) / 1000, 2), "seconds": round(seconds)}
                )
            start = None

    moving = [i for i in range(n) if _num(speed[i]) and speed[i] > 1.6 and _num(hr[i])]
    halves: dict[str, Any] = {}
    if len(moving) > 20:
        half = len(moving) // 2
        halves = {
            "first_half": {
                "avg_hr": round(mean(hr[i] for i in moving[:half])),
                "pace": _pace(mean(speed[i] for i in moving[:half])),
            },
            "second_half": {
                "avg_hr": round(mean(hr[i] for i in moving[half:])),
                "pace": _pace(mean(speed[i] for i in moving[half:])),
            },
        }
    return {"km_hr": km_hr, "segments": segments, "walk_breaks": walk_breaks, **halves}


def run_traces(details: dict[str, Any] | None, bins: int = 120) -> dict[str, list[float]]:
    detail = details or {}
    positions = index_map(detail)
    distance = stream(detail, positions, "sumDistance")
    channels = {
        "hr": stream(detail, positions, "directHeartRate"),
        "speed": stream(detail, positions, "directSpeed"),
        "cadence": stream(detail, positions, "directDoubleCadence"),
        "elevation": stream(detail, positions, "directElevation"),
    }
    points = [
        (distance[i], {name: values[i] for name, values in channels.items()})
        for i in range(len(distance))
        if _num(distance[i])
    ]
    result: dict[str, list[float]] = {
        "km": [],
        "hr": [],
        "speed": [],
        "cadence": [],
        "elevation": [],
    }
    if not points:
        return result
    dmax = max(p[0] for p in points)
    if dmax <= 0:
        return result
    buckets: list[list[tuple[float, dict[str, Any]]]] = [[] for _ in range(bins)]
    for dist, values in points:
        slot = min(bins - 1, int(dist / dmax * bins))
        buckets[slot].append((dist, values))
    for bucket in buckets:
        if not bucket:
            continue
        result["km"].append(round(mean(p[0] for p in bucket) / 1000, 3))
        for name in channels:
            good = _clean([p[1][name] for p in bucket])
            result[name].append(round(mean(good), 2) if good else float("nan"))
    return result
