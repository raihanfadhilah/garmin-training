from dataclasses import dataclass, field
from datetime import date, timedelta
from operator import attrgetter
from typing import Any

from garminconnect.workout import ConditionType, SportType, StepType, TargetType

from garmin import plan
from garmin.client import GarminClient

EASY_PACE_SECONDS_PER_KM = 450
PUSHABLE = frozenset({"easy", "long", "hill_tempo", "strides", "race"})
ZONE_BY_KIND = {"easy": 2, "long": 2, "strides": 2, "race": 2, "hill_tempo": 3}
RUNNING = {"sportTypeId": SportType.RUNNING, "sportTypeKey": "running", "displayOrder": 1}


def _step(condition: str, value: float, zone: int) -> dict[str, Any]:
    conditions = {
        "distance": (ConditionType.DISTANCE, "distance", 3),
        "time": (ConditionType.TIME, "time", 2),
    }
    type_id, key, order = conditions[condition]
    return {
        "type": "ExecutableStepDTO",
        "stepOrder": 1,
        "stepType": {"stepTypeId": StepType.INTERVAL, "stepTypeKey": "interval", "displayOrder": 3},
        "endCondition": {
            "conditionTypeId": type_id,
            "conditionTypeKey": key,
            "displayOrder": order,
            "displayable": True,
        },
        "endConditionValue": value,
        "targetType": {
            "workoutTargetTypeId": TargetType.HEART_RATE_ZONE,
            "workoutTargetTypeKey": "heart.rate.zone",
            "displayOrder": 4,
        },
        "zoneNumber": zone,
    }


@dataclass(frozen=True)
class PlannedWorkout:
    day: date
    name: str
    kind: str
    summary: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class PushResult:
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def build(week: plan.PlanWeek, session: plan.Session) -> PlannedWorkout | None:
    if session.kind not in PUSHABLE:
        return None
    zone = ZONE_BY_KIND.get(session.kind, 2)
    if session.minutes:
        seconds = session.minutes * 60
        step = _step("time", seconds, zone)
        summary = f"{session.minutes} min, HR zone {zone}"
    elif session.km:
        seconds = int(session.km * EASY_PACE_SECONDS_PER_KM)
        step = _step("distance", session.km * 1000, zone)
        summary = f"{session.km:.0f} km, HR zone {zone}"
    else:
        return None
    name = f"W{week.number} {session.label}"[:80]
    payload = {
        "workoutName": name,
        "sportType": RUNNING,
        "estimatedDurationInSecs": seconds,
        "workoutSegments": [
            {"segmentOrder": 1, "sportType": RUNNING, "workoutSteps": [step]},
        ],
    }
    return PlannedWorkout(
        day=week.start + timedelta(days=session.day),
        name=name,
        kind=session.kind,
        summary=summary,
        payload=payload,
    )


def scheduled(start: date, end: date) -> list[PlannedWorkout]:
    out = [
        built
        for week in plan.PLAN
        for session in week.sessions
        if (built := build(week, session)) is not None and start <= built.day <= end
    ]
    return sorted(out, key=attrgetter("day", "name"))


def unpushable(start: date, end: date) -> list[str]:
    out = []
    for week in plan.PLAN:
        for session in week.sessions:
            day = week.start + timedelta(days=session.day)
            if session.kind not in PUSHABLE and start <= day <= end:
                out.append(f"{day.isoformat()} {session.label}")
    return out


def push(client: GarminClient, workouts: list[PlannedWorkout]) -> PushResult:
    existing = {
        w.get("workoutName") for w in (client.api.get_workouts(0, 200) or []) if isinstance(w, dict)
    }
    created: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []
    for item in workouts:
        if item.name in existing:
            skipped.append(f"{item.day} {item.name} (already on Garmin)")
            continue
        try:
            response = client.api.upload_workout(item.payload)
            workout_id = response.get("workoutId") if isinstance(response, dict) else None
            if workout_id is None:
                errors.append(f"{item.day} {item.name}: upload returned no workoutId")
                continue
            client.api.schedule_workout(workout_id, item.day.isoformat())
            created.append(f"{item.day} {item.name} (id {workout_id})")
        except Exception as error:
            errors.append(f"{item.day} {item.name}: {error}")
    return PushResult(created=created, skipped=skipped, errors=errors)
