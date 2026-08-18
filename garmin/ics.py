from datetime import UTC, date, datetime, timedelta

from garmin import plan

PRODID = "-//garmin training//Madeira 25K plan//EN"
CALENDAR_NAME = f"{plan.RACE_NAME} training"
SLUG = "".join(c for c in plan.RACE_NAME.lower() if c.isalnum())
FOLD_WIDTH = 73


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    if len(line) <= FOLD_WIDTH:
        return line
    head, rest = line[:FOLD_WIDTH], line[FOLD_WIDTH:]
    chunks = [rest[i : i + FOLD_WIDTH - 1] for i in range(0, len(rest), FOLD_WIDTH - 1)]
    return "\r\n ".join([head, *chunks])


def _stamp(moment: datetime) -> str:
    return moment.strftime("%Y%m%dT%H%M%SZ")


SUMMARY_MAX = 48
KIND_ICONS = {
    "long": "\u25b2",
    "race": "\u2691",
    "legs": "\u25c6",
    "vertical": "\u25b2",
    "descent": "\u25bc",
    "swim": "\u2248",
    "cycling": "\u25cb",
    "brick": "\u25d0",
}


def _headline(label: str) -> tuple[str, bool]:
    for sep in (" - ", "\u2014 ", ". "):
        if sep in label:
            label = label.split(sep, 1)[0]
            break
    label = label.strip().rstrip(".")
    if len(label) <= SUMMARY_MAX:
        return label, False
    if " (" in label:
        short = label.split(" (", 1)[0].strip()
        if len(short) <= SUMMARY_MAX:
            return short, False
    return label[:SUMMARY_MAX].rsplit(" ", 1)[0] + "\u2026", True


def _title(week: plan.PlanWeek, session: plan.Session) -> str:
    text, clipped = _headline(session.label)
    if not clipped:
        if session.km and "km" not in text:
            text = f"{text} ({session.km:g} km)"
        elif session.minutes and "min" not in text:
            text = f"{text} ({session.minutes} min)"
    icon = KIND_ICONS.get(session.kind)
    return f"{icon} {text}" if icon else text


def _details(week: plan.PlanWeek, session: plan.Session) -> str:
    lines = [session.label, ""]
    lines.append(f"Week {week.number} of {len(plan.PLAN)} - {week.phase}")
    if week.down_week:
        lines.append("DOWN WEEK - recover, do not add volume.")
    if session.kind in {"easy", "long"}:
        lines.append(f"Keep HR under {plan.EASY_HR_CAP}. Walk the climbs. Talk test.")
    if week.note:
        lines.append(week.note)
    days = (plan.RACE_DATE - (week.start + timedelta(days=session.day))).days
    lines.append(f"{days} days to {plan.RACE_NAME}.")
    return "\n".join(lines)


def _event(
    week: plan.PlanWeek, session: plan.Session, index: int, now: datetime
) -> list[str]:
    day = week.start + timedelta(days=session.day)
    return [
        "BEGIN:VEVENT",
        f"UID:{SLUG}-w{week.number}-s{index}-{session.kind}@garmin-training",
        f"DTSTAMP:{_stamp(now)}",
        f"DTSTART;VALUE=DATE:{day:%Y%m%d}",
        f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}",
        f"SUMMARY:{_escape(_title(week, session))}",
        f"DESCRIPTION:{_escape(_details(week, session))}",
        "TRANSP:TRANSPARENT",
        "END:VEVENT",
    ]


def build(now: datetime | None = None) -> str:
    moment = now or datetime.now(UTC)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_escape(CALENDAR_NAME)}",
    ]
    for week in plan.PLAN:
        for index, session in enumerate(week.sessions):
            lines.extend(_event(week, session, index, moment))
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def event_count() -> int:
    return sum(len(week.sessions) for week in plan.PLAN)


def race_day() -> date:
    return plan.RACE_DATE
