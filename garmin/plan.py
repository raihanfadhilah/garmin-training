from dataclasses import dataclass, field
from datetime import date, datetime
from statistics import mean
from typing import Any

RACE_NAME = "Ultra X Madeira 25K"
RACE_DATE = date(2026, 11, 1)
EASY_TARGET_PCT = 80.0
CADENCE_TARGET = 178
DECOUPLING_TARGET = 5.0

RUN_KINDS = frozenset({"easy", "long", "hill_tempo", "strides", "race"})
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


def _runs(
    label: str, long_km: float, easy_kms: tuple[float, ...], easy_days: tuple[int, ...]
) -> list[Session]:
    sessions = [Session("long", label, SUN, km=long_km)]
    sessions += [
        Session("easy", f"Easy run {km:.0f} km (Z2)", day, km=km)
        for km, day in zip(easy_kms, easy_days, strict=False)
    ]
    return sessions


def _base(
    long_km: float, easy_kms: tuple[float, ...], vertical_min: int, eccentric: bool
) -> tuple[Session, ...]:
    sessions = _runs(f"Long run {long_km:.0f} km (Z2)", long_km, easy_kms, (WED, FRI))
    sessions.append(
        Session(
            "vertical",
            f"Vertical {vertical_min} min (stairs/ramp/incline)",
            TUE,
            minutes=vertical_min,
        )
    )
    if eccentric:
        sessions.append(
            Session("eccentric", "Controlled ramp/stair descents (after the vertical)", TUE)
        )
    sessions.append(Session("legs", "Legs — heavy, brief, single-leg biased", THU))
    sessions.append(Session("push", "Push (upper)", MON))
    sessions.append(Session("pull", "Pull (upper)", THU))
    return tuple(sessions)


def _build(long_km: float, easy_kms: tuple[float, ...], tempo_min: int) -> tuple[Session, ...]:
    sessions = _runs(f"Long run {long_km:.0f} km (Z2)", long_km, easy_kms, (TUE, FRI))
    sessions.append(
        Session("eccentric", "Downhill dose in the long run (decline / down-ramps)", SUN)
    )
    sessions.append(
        Session(
            "hill_tempo",
            f"Hill tempo {tempo_min} min (uphill cruise intervals)",
            WED,
            minutes=tempo_min,
        )
    )
    sessions.append(Session("legs", "Legs — heavy, brief", THU))
    sessions.append(Session("push", "Push (upper)", MON))
    sessions.append(Session("pull", "Pull (upper)", THU))
    return tuple(sessions)


def _peak(
    long_km: float, easy_kms: tuple[float, ...], climb_min: int, rehearsal: bool
) -> tuple[Session, ...]:
    label = (
        "Long run 25 km — DRESS REHEARSAL (full kit + fuel, hilliest route, decline segment)"
        if rehearsal
        else f"Long run {long_km:.0f} km (Z2, hilly, downhill segment)"
    )
    sessions = _runs(label, long_km, easy_kms, (TUE, FRI))
    sessions.append(
        Session(
            "vertical",
            f"Sustained climbs {climb_min} min (race simulation)",
            WED,
            minutes=climb_min,
        )
    )
    sessions.append(Session("legs", "Legs — reduced volume (maintain, don't build)", THU))
    sessions.append(Session("push", "Push (upper, lighter)", MON))
    sessions.append(Session("pull", "Pull (upper, lighter)", THU))
    return tuple(sessions)


PLAN: tuple[PlanWeek, ...] = (
    PlanWeek(1, date(2026, 7, 5), date(2026, 7, 11), "Base", _base(7, (4, 5), 20, False)),
    PlanWeek(2, date(2026, 7, 12), date(2026, 7, 18), "Base", _base(8, (4, 5), 25, False)),
    PlanWeek(
        3,
        date(2026, 7, 19),
        date(2026, 7, 25),
        "Base",
        _base(9, (5, 5), 25, True),
        note="Eccentric enters: start running controlled descents.",
    ),
    PlanWeek(
        4,
        date(2026, 7, 26),
        date(2026, 8, 1),
        "Base",
        _base(6, (4, 4), 20, True),
        down_week=True,
        note="Down week — cut long run, lighter everything.",
    ),
    PlanWeek(
        5,
        date(2026, 8, 2),
        date(2026, 8, 8),
        "Build",
        _build(10, (5, 6), 25),
        note="Quality enters: one weekly hill tempo (uphill, not flat).",
    ),
    PlanWeek(6, date(2026, 8, 9), date(2026, 8, 15), "Build", _build(12, (5, 6), 25)),
    PlanWeek(7, date(2026, 8, 16), date(2026, 8, 22), "Build", _build(14, (6, 6), 30)),
    PlanWeek(
        8,
        date(2026, 8, 23),
        date(2026, 8, 29),
        "Build",
        _build(10, (5, 5), 20),
        down_week=True,
        note="Down week — halve hill-tempo volume, lighter legs.",
    ),
    PlanWeek(9, date(2026, 8, 30), date(2026, 9, 5), "Build", _build(15, (6, 6), 30)),
    PlanWeek(10, date(2026, 9, 6), date(2026, 9, 12), "Build", _build(17, (6, 7), 35)),
    PlanWeek(11, date(2026, 9, 13), date(2026, 9, 19), "Build", _build(19, (7, 6), 35)),
    PlanWeek(
        12,
        date(2026, 9, 20),
        date(2026, 9, 26),
        "Peak",
        _peak(12, (6, 5), 30, False),
        down_week=True,
        note="Down week before the push to the dress rehearsal.",
    ),
    PlanWeek(13, date(2026, 9, 27), date(2026, 10, 3), "Peak", _peak(21, (7, 7), 40, False)),
    PlanWeek(
        14,
        date(2026, 10, 4),
        date(2026, 10, 10),
        "Peak",
        _peak(25, (6, 6), 35, True),
        note="Keystone week: 25 km dress rehearsal validates fuel, kit, climbing, descending.",
    ),
    PlanWeek(
        15,
        date(2026, 10, 11),
        date(2026, 10, 17),
        "Taper",
        (
            Session("long", "Reduced long run 12-15 km (Z2)", SUN, km=15),
            Session("easy", "Easy run + short uphill strides", TUE, km=6),
            Session(
                "vertical", "Short vertical 15-20 min (maintain, don't build)", WED, minutes=20
            ),
            Session("legs", "Legs — last heavy session ~10 days out, then stop", THU),
            Session("easy", "Easy run (Z2)", FRI, km=5),
        ),
        note="Taper begins — volume drops ~40%, keep a touch of intensity.",
    ),
    PlanWeek(
        16,
        date(2026, 10, 18),
        date(2026, 10, 24),
        "Taper",
        (
            Session("long", "Reduced long run 10 km (Z2)", SUN, km=10),
            Session("easy", "Easy run 6 km (Z2)", TUE, km=6),
            Session("vertical", "Vertical 20 min (light)", WED, minutes=20),
            Session("easy", "Easy run 5 km (Z2)", FRI, km=5),
        ),
        note="Taper — reduced volume, arrive fresh. Last heavy legs behind you.",
    ),
    PlanWeek(
        17,
        date(2026, 10, 25),
        date(2026, 11, 1),
        "Race",
        (
            Session("easy", "Easy shakeout 5 km", MON, km=5),
            Session("strides", "Easy 3-4 km + strides", WED, km=4),
            Session("easy", "Shakeout in Machico 3-4 km", FRI, km=4),
            Session("race", "RACE — Madeira 25K", RACE_DAY, km=25),
        ),
        note="Race week — fitness is banked; the taper's only job is freshness.",
    ),
)


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
            return "missed"
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
