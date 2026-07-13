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
