import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from typing import Any

DEFAULT_PLAN = Path(__file__).parent.parent / "plans" / "madeira25k.json"

RUN_KINDS = frozenset({"easy", "long", "hill_tempo", "strides", "race", "benchmark"})
LONG_KINDS = frozenset({"long", "race"})
CLIMB_KINDS = frozenset({"vertical", "hill_tempo"})

SUN, MON, TUE, WED, THU, FRI, SAT, RACE_DAY = 0, 1, 2, 3, 4, 5, 6, 7


@dataclass(frozen=True)
class Session:
    kind: str
    label: str
    day: int
    km: float | None = None
    minutes: int | None = None


@dataclass(frozen=True)
class PlanWeek:
    number: int
    start: date
    end: date
    phase: str
    sessions: tuple[Session, ...]
    down_week: bool = False
    note: str = ""

    @property
    def long_km(self) -> float:
        kms = [s.km for s in self.sessions if s.kind in LONG_KINDS and s.km]
        return max(kms) if kms else 0.0

    @property
    def planned_runs(self) -> int:
        return sum(1 for s in self.sessions if s.kind in RUN_KINDS)

    @property
    def planned_km(self) -> float:
        return round(sum(s.km for s in self.sessions if s.kind in RUN_KINDS and s.km), 1)

    @property
    def vertical_min(self) -> int:
        mins = [s.minutes for s in self.sessions if s.kind in CLIMB_KINDS and s.minutes]
        return max(mins) if mins else 0

    @property
    def span_days(self) -> int:
        return (self.end - self.start).days

    def contains(self, day: date) -> bool:
        return self.start <= day <= self.end


LONG_DAY_MIN_PER_KM = 8.0
HILL_DAY_MIN_PER_KM = 12.0


def plan_path() -> Path:
    override = os.environ.get("GARMIN_PLAN")
    return Path(override) if override else DEFAULT_PLAN


def load(path: Path | None = None) -> tuple[dict[str, Any], tuple[PlanWeek, ...]]:
    document = json.loads((path or plan_path()).read_text(encoding="utf-8"))
    weeks = tuple(
        PlanWeek(
            number=int(week["number"]),
            start=date.fromisoformat(week["start"]),
            end=date.fromisoformat(week["end"]),
            phase=str(week["phase"]),
            sessions=tuple(
                Session(
                    kind=str(s["kind"]),
                    label=str(s["label"]),
                    day=int(s["day"]),
                    km=s.get("km"),
                    minutes=s.get("minutes"),
                )
                for s in week["sessions"]
            ),
            down_week=bool(week.get("down_week", False)),
            note=str(week.get("note", "")),
        )
        for week in document["weeks"]
    )
    return document, sorted_weeks(weeks)


def sorted_weeks(weeks: tuple[PlanWeek, ...]) -> tuple[PlanWeek, ...]:
    return tuple(sorted(weeks, key=lambda w: w.start))


_DOCUMENT, PLAN = load()
_SETTINGS: dict[str, Any] = _DOCUMENT.get("settings", {})

RACE_NAME: str = _DOCUMENT["race"]["name"]
RACE_DATE: date = date.fromisoformat(_DOCUMENT["race"]["date"])

EASY_HR_CAP: int = int(_SETTINGS.get("easy_hr_cap", 150))
BENCHMARK_HR: int = int(_SETTINGS.get("benchmark_hr", 150))
BENCHMARK_KM: int = int(_SETTINGS.get("benchmark_km", 7))
CADENCE_TARGET: int = int(_SETTINGS.get("cadence_target", 178))
EASY_TARGET_PCT: float = float(_SETTINGS.get("easy_target_pct", 80.0))
DECOUPLING_TARGET: float = float(_SETTINGS.get("decoupling_target", 5.0))


@dataclass(frozen=True)
class WeekProgress:
    week: PlanWeek
    actual_runs: int
    actual_km: float
    long_km: float
    elevation_m: float
    easy_pct: float | None
    avg_cadence: float | None
    is_future: bool
    is_past: bool
    matched: list[dict[str, Any]] = field(default_factory=list)

    @property
    def long_hit(self) -> bool:
        return self.long_km >= self.week.long_km * 0.9

    @property
    def runs_hit(self) -> bool:
        return self.actual_runs >= self.week.planned_runs

    @property
    def status(self) -> str:
        if self.is_future:
            return "upcoming"
        if self.actual_runs == 0:
            return "missed" if self.is_past else "in-progress"
        if self.long_hit and self.runs_hit:
            return "on-track"
        return "partial"


def current_week(today: date) -> PlanWeek | None:
    for week in PLAN:
        if week.contains(today):
            return week
    return None


def days_to_race(today: date) -> int:
    return (RACE_DATE - today).days


def evaluate(week: PlanWeek, runs: list[dict[str, Any]], today: date) -> WeekProgress:
    matched = [r for r in runs if week.contains(_as_day(r["date"]))]
    distances = [r["dist_km"] for r in matched if r.get("dist_km")]
    elevation = sum(r.get("elev_gain") or 0 for r in matched)
    durations = [r.get("dur_min") or 0 for r in matched]
    easy_share = [((r["zones"][0] + r["zones"][1]) if r.get("zones") else 0) for r in matched]
    total_dur = sum(durations)
    easy_pct = (
        round(sum(d * e for d, e in zip(durations, easy_share, strict=False)) / total_dur, 0)
        if total_dur
        else None
    )
    cadences = [r["avg_cadence"] for r in matched if r.get("avg_cadence")]
    return WeekProgress(
        week=week,
        actual_runs=len(matched),
        actual_km=round(sum(distances), 1),
        long_km=round(max(distances), 1) if distances else 0.0,
        elevation_m=round(elevation),
        easy_pct=easy_pct,
        avg_cadence=round(mean(cadences)) if cadences else None,
        is_future=week.start > today,
        is_past=week.end < today,
        matched=matched,
    )


def evaluate_all(runs: list[dict[str, Any]], today: date) -> list[WeekProgress]:
    return [evaluate(week, runs, today) for week in PLAN]


def _as_day(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])
