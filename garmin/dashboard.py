from datetime import date, timedelta
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import select

from garmin import plan
from garmin.analysis import run_metrics, run_traces
from garmin.config import Settings
from garmin.database import Database
from garmin.models import Activity, ActivityStream, DailyMetric, RacePrediction

ACCENT = "#3987e5"
INK = "#e9edf0"
MUTED = "#8b9296"
GRID = "#232a2e"
ZONES = ["#3987e5", "#199e70", "#c98500", "#d95926", "#e66767"]
ZONE_NAMES = ["Z1 recovery", "Z2 easy", "Z3 moderate", "Z4 threshold", "Z5 max"]
GOOD, WARN, SERIOUS, CRIT = "#12b312", "#fab219", "#ec835a", "#e05555"
DISTANCES = {
    "time_5k": ("5K", 5.0),
    "time_10k": ("10K", 10.0),
    "time_half": ("Half", 21.0975),
    "time_marathon": ("Marathon", 42.195),
}
STATUS_COLOR = {
    "RECOVERY": ZONES[1],
    "MAINTAINING": ZONES[1],
    "PRODUCTIVE": GOOD,
    "DETRAINING": SERIOUS,
    "UNPRODUCTIVE": CRIT,
    "OVERREACHING": WARN,
    "NO_STATUS": MUTED,
}


def _mmss(seconds: float | None) -> str:
    if seconds is None or pd.isna(seconds):
        return "–"
    total = int(round(seconds))
    return f"{total // 60}:{total % 60:02d}"


def _race_time(seconds: float | None) -> str:
    if seconds is None or pd.isna(seconds):
        return "–"
    total = int(round(seconds))
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def _decoupling_color(value: float | None) -> str:
    if value is None or pd.isna(value):
        return MUTED
    if value < 5:
        return GOOD
    if value < 10:
        return WARN
    if value < 20:
        return SERIOUS
    return CRIT


def _status_base(status: str | None) -> str:
    if not status:
        return "NO_STATUS"
    cleaned = status.rstrip("0123456789_")
    return "NO_STATUS" if cleaned in {"", "NONE"} else cleaned


@st.cache_data(ttl=120)
def load_frames() -> dict[str, Any]:
    return build_frames()


def build_frames() -> dict[str, Any]:
    database = Database(Settings())
    with database.session() as session:
        activities = list(
            session.scalars(select(Activity).order_by(Activity.start_time_local)).all()
        )
        streams = {s.activity_id: s.details for s in session.scalars(select(ActivityStream)).all()}
        dailies = list(session.scalars(select(DailyMetric).order_by(DailyMetric.day)).all())
        predictions = list(
            session.scalars(select(RacePrediction).order_by(RacePrediction.day)).all()
        )

        runs = [
            run_metrics(a, streams.get(a.activity_id))
            for a in activities
            if a.type_key == "running" and (a.distance_m or 0) > 0
        ]
        traces = {
            a.activity_id: run_traces(streams.get(a.activity_id))
            for a in activities
            if a.type_key == "running" and (a.distance_m or 0) > 0
        }
        daily_rows = [
            {
                "day": d.day,
                "status": _status_base(d.training_status),
                "readiness": d.training_readiness,
                "vo2": d.vo2max_running,
                "stress": d.stress_avg,
                "steps": d.steps,
                "body_battery_high": d.body_battery_high,
                "endurance": d.endurance_score,
                "hill": d.hill_score,
                "acwr": d.acwr,
            }
            for d in dailies
        ]
        pred_rows = [
            {
                "day": p.day,
                "time_5k": p.time_5k,
                "time_10k": p.time_10k,
                "time_half": p.time_half,
                "time_marathon": p.time_marathon,
            }
            for p in predictions
        ]

    runs_df = pd.DataFrame(runs)
    if not runs_df.empty:
        runs_df["date"] = pd.to_datetime(runs_df["date"])
        runs_df["label"] = runs_df["date"].dt.strftime("%b %d")
    daily_df = pd.DataFrame(daily_rows)
    if not daily_df.empty:
        daily_df["day"] = pd.to_datetime(daily_df["day"])
    pred_df = pd.DataFrame(pred_rows)
    if not pred_df.empty:
        pred_df["day"] = pd.to_datetime(pred_df["day"])
    progress = plan.evaluate_all(runs, date.today())
    return {
        "runs": runs_df,
        "daily": daily_df,
        "pred": pred_df,
        "traces": traces,
        "progress": progress,
    }


def _style(fig: go.Figure, height: int = 320, ylabel: str = "") -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=28, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=12),
        showlegend=False,
        yaxis_title=ylabel,
        hoverlabel=dict(bgcolor="rgba(17,21,24,0.92)", font_size=12),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


def fig_weekly(runs_df: pd.DataFrame) -> go.Figure:
    weekly = runs_df.set_index("date").resample("W-MON")["dist_km"].sum()
    colors = [ACCENT if v > 0 else GRID for v in weekly.values]
    fig = go.Figure(
        go.Bar(
            x=weekly.index,
            y=weekly.values,
            marker_color=colors,
            marker_line_width=0,
            hovertemplate="week of %{x|%b %d}<br>%{y:.1f} km<extra></extra>",
        )
    )
    return _style(fig, 300, "km / week")


def fig_status(daily_df: pd.DataFrame) -> go.Figure:
    df = daily_df.dropna(subset=["status"])
    colors = [STATUS_COLOR.get(s, MUTED) for s in df["status"]]
    fig = go.Figure(
        go.Bar(
            x=df["day"],
            y=[1] * len(df),
            marker_color=colors,
            marker_line_width=0,
            customdata=df["status"],
            hovertemplate="%{x|%b %d}<br>%{customdata}<extra></extra>",
        )
    )
    fig.update_yaxes(visible=False, range=[0, 1])
    return _style(fig, 130, "")


def fig_line(
    runs_df: pd.DataFrame,
    column: str,
    ylabel: str,
    color: str = ACCENT,
    reference: float | None = None,
) -> go.Figure:
    df = runs_df.dropna(subset=[column])
    fig = go.Figure()
    if reference is not None:
        fig.add_hline(y=reference, line_dash="dot", line_color=MUTED, opacity=0.6)
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df[column],
            mode="lines+markers",
            line=dict(color=color, width=2.6),
            marker=dict(size=8, color=color),
            hovertemplate="%{x|%b %d}<br>%{y}<extra></extra>",
        )
    )
    return _style(fig, 300, ylabel)


def fig_decoupling(runs_df: pd.DataFrame) -> go.Figure:
    df = runs_df.dropna(subset=["decoupling"])
    colors = [_decoupling_color(v) for v in df["decoupling"]]
    fig = go.Figure(
        go.Bar(
            x=df["date"],
            y=df["decoupling"],
            marker_color=colors,
            marker_line_width=0,
            hovertemplate="%{x|%b %d}<br>decoupling %{y}%<extra></extra>",
        )
    )
    fig.add_hline(y=5, line_dash="dot", line_color=GOOD, opacity=0.6)
    return _style(fig, 300, "decoupling %")


def fig_vo2(runs_df: pd.DataFrame, daily_df: pd.DataFrame) -> go.Figure:
    points: dict[Any, float] = {}
    if not daily_df.empty:
        for _, row in daily_df.dropna(subset=["vo2"]).iterrows():
            points[row["day"]] = row["vo2"]
    for _, row in runs_df.dropna(subset=["vo2"]).iterrows():
        points.setdefault(row["date"].normalize(), row["vo2"])
    series = pd.Series(points).sort_index()
    fig = go.Figure(
        go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines+markers",
            fill="tozeroy",
            line=dict(color=ACCENT, width=2.6),
            marker=dict(size=7, color=ACCENT),
            fillcolor="rgba(57,135,229,0.10)",
            hovertemplate="%{x|%b %d}<br>VO₂ %{y}<extra></extra>",
        )
    )
    lo = float(series.min()) - 1
    fig.update_yaxes(range=[lo, float(series.max()) + 1])
    return _style(fig, 300, "ml/kg/min")


def fig_zones(runs_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    labels = runs_df["label"]
    for zi in range(5):
        values = [z[zi] for z in runs_df["zones"]]
        fig.add_trace(
            go.Bar(
                y=labels,
                x=values,
                orientation="h",
                name=ZONE_NAMES[zi],
                marker_color=ZONES[zi],
                marker_line=dict(width=1, color="rgba(0,0,0,0)"),
                hovertemplate=f"%{{y}}<br>{ZONE_NAMES[zi]}: %{{x}}%<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="stack", showlegend=True, legend=dict(orientation="h", y=-0.12, font=dict(size=11))
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    return _style(fig, 60 + 34 * len(runs_df), "")


def fig_predictions(pred_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    palette = [ZONES[0], ZONES[1], ZONES[2], ZONES[4]]
    for (column, (name, km)), color in zip(DISTANCES.items(), palette, strict=False):
        df = pred_df.dropna(subset=[column])
        if df.empty:
            continue
        pace = df[column] / km
        fig.add_trace(
            go.Scatter(
                x=df["day"],
                y=pace,
                mode="lines",
                name=name,
                line=dict(color=color, width=2.4),
                customdata=[_mmss(p) for p in pace],
                hovertemplate=f"{name} · %{{x|%b %d}}<br>%{{customdata}}/km<extra></extra>",
            )
        )
    ticks = list(range(240, 480, 30))
    fig.update_yaxes(autorange="reversed", tickvals=ticks, ticktext=[_mmss(t) for t in ticks])
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.15, font=dict(size=11)))
    return _style(fig, 340, "predicted pace /km")


def fig_wellness(daily_df: pd.DataFrame, column: str, ylabel: str, color: str) -> go.Figure:
    df = daily_df.dropna(subset=[column])
    fig = go.Figure(
        go.Bar(
            x=df["day"],
            y=df[column],
            marker_color=color,
            marker_line_width=0,
            hovertemplate="%{x|%b %d}<br>%{y}<extra></extra>",
        )
    )
    return _style(fig, 280, ylabel)


def _pace_ticks(values: list[float]) -> tuple[list[int], list[str]]:
    lo, hi = int(min(values)), int(max(values))
    step = max(15, round((hi - lo) / 4 / 15) * 15) or 15
    ticks = list(range(lo - lo % step, hi + step, step))
    return ticks, [_mmss(t) for t in ticks]


def fig_trace(
    traces: dict[int, dict[str, list[float]]], run_id: int, channel: str, title: str, color: str
) -> go.Figure | None:
    data = traces.get(run_id) or {}
    km = data.get("km") or []
    if channel == "pace":
        raw = data.get("speed") or []
        values = [1000.0 / s if s and s > 1.4 else float("nan") for s in raw]
    else:
        values = data.get(channel) or []
    pairs = [(k, v) for k, v in zip(km, values, strict=False) if not pd.isna(v)]
    if len(pairs) < 3:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    fig = go.Figure(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            line=dict(color=color, width=2),
            hovertemplate="%{x:.1f} km<br>%{y}<extra></extra>",
        )
    )
    if channel == "pace":
        ticks, text = _pace_ticks(ys)
        fig.update_yaxes(autorange="reversed", tickvals=ticks, ticktext=text)
    fig.update_xaxes(ticksuffix=" km")
    return _style(fig, 200, title)


def _walk_spans(
    km: list[float], speed: list[float], threshold: float = 1.6
) -> list[tuple[float, float]]:
    spans: list[tuple[float, float]] = []
    start: float | None = None
    for i in range(len(km)):
        slow = not pd.isna(speed[i]) and speed[i] < threshold
        if slow and start is None:
            start = km[i]
        elif not slow and start is not None:
            spans.append((start, km[i]))
            start = None
    if start is not None and km:
        spans.append((start, km[-1]))
    return spans


def fig_hr_drift(traces: dict[int, dict[str, list[float]]], run_id: int) -> go.Figure | None:
    data = traces.get(run_id) or {}
    km = data.get("km") or []
    hr = data.get("hr") or []
    speed = data.get("speed") or []
    pairs = [(km[i], hr[i]) for i in range(len(km)) if not pd.isna(hr[i])]
    if len(pairs) < 5:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    fifth = max(1, len(ys) // 5)
    base = round(sum(ys[:fifth]) / fifth)
    late = round(sum(ys[-fifth:]) / fifth)
    fig = go.Figure()
    for span_start, span_end in _walk_spans(km, speed):
        fig.add_vrect(x0=span_start, x1=span_end, fillcolor=MUTED, opacity=0.16, line_width=0)
    fig.add_hline(
        y=base,
        line_dash="dot",
        line_color=MUTED,
        opacity=0.8,
        annotation_text=f"start ~{base}",
        annotation_position="top left",
        annotation_font_color=MUTED,
    )
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            line=dict(color=ZONES[4], width=2.6),
            hovertemplate="%{x:.1f} km<br>HR %{y:.0f}<extra></extra>",
        )
    )
    fig.add_annotation(
        x=xs[-1],
        y=late,
        text=f"drift +{late - base} bpm",
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        font=dict(color=ZONES[4], size=13),
    )
    fig.update_xaxes(ticksuffix=" km")
    return _style(fig, 260, "heart rate (bpm)")


def fig_long_progression(progress: list[plan.WeekProgress]) -> go.Figure:
    weeks = [p.week.number for p in progress]
    planned = [p.week.long_km for p in progress]
    done = [p for p in progress if not p.is_future and p.actual_runs > 0]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=weeks,
            y=planned,
            mode="lines+markers",
            name="planned",
            line=dict(color=MUTED, width=2, dash="dot"),
            marker=dict(size=6, color=MUTED),
            hovertemplate="W%{x} planned %{y} km<extra></extra>",
        )
    )
    if done:
        fig.add_trace(
            go.Scatter(
                x=[p.week.number for p in done],
                y=[p.long_km for p in done],
                mode="markers",
                name="actual",
                marker=dict(size=11, color=ACCENT),
                hovertemplate="W%{x} actual %{y} km<extra></extra>",
            )
        )
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.18))
    fig.update_xaxes(title="week", dtick=1)
    return _style(fig, 320, "long run km")


def fig_volume_plan(progress: list[plan.WeekProgress]) -> go.Figure:
    weeks = [f"W{p.week.number}" for p in progress]
    planned = [p.week.planned_km for p in progress]
    actual = [p.actual_km if (not p.is_future and p.actual_runs > 0) else None for p in progress]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=weeks, y=planned, name="planned", marker_color=GRID, marker_line_width=0)
    )
    fig.add_trace(
        go.Bar(x=weeks, y=actual, name="actual", marker_color=ACCENT, marker_line_width=0)
    )
    fig.update_layout(barmode="group", showlegend=True, legend=dict(orientation="h", y=-0.18))
    return _style(fig, 320, "km / week")


def fig_easy_discipline(progress: list[plan.WeekProgress]) -> go.Figure:
    pairs = [(f"W{p.week.number}", e) for p in progress if (e := p.easy_pct) is not None]
    weeks = [label for label, _ in pairs]
    values = [value for _, value in pairs]
    colors = [GOOD if v >= plan.EASY_TARGET_PCT else SERIOUS for v in values]
    fig = go.Figure(
        go.Bar(
            x=weeks,
            y=values,
            marker_color=colors,
            marker_line_width=0,
            hovertemplate="%{x}<br>%{y}% easy<extra></extra>",
        )
    )
    fig.add_hline(y=plan.EASY_TARGET_PCT, line_dash="dot", line_color=GOOD, opacity=0.7)
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return _style(fig, 300, "% easy (Z1+Z2)")


def fig_vertical(progress: list[plan.WeekProgress]) -> go.Figure:
    pts = [p for p in progress if not p.is_future and p.actual_runs > 0]
    weeks = [f"W{p.week.number}" for p in pts]
    values = [p.elevation_m for p in pts]
    fig = go.Figure(
        go.Bar(
            x=weeks,
            y=values,
            marker_color=ZONES[2],
            marker_line_width=0,
            hovertemplate="%{x}<br>%{y} m climb<extra></extra>",
        )
    )
    return _style(fig, 300, "elevation gain (m)")


def _plan_table(progress: list[plan.WeekProgress]) -> pd.DataFrame:
    labels = {
        "on-track": "on track",
        "partial": "partial",
        "in-progress": "in progress",
        "missed": "missed",
        "upcoming": "—",
    }
    rows = []
    for p in progress:
        week = p.week
        live = not p.is_future and p.actual_runs > 0
        rows.append(
            {
                "Wk": week.number,
                "Dates": f"{week.start:%b %d} – {week.end:%b %d}",
                "Phase": week.phase,
                "Plan runs": week.planned_runs,
                "Plan long": week.long_km,
                "Plan km": week.planned_km,
                "Vert min": week.vertical_min,
                "Runs": p.actual_runs if not p.is_future else None,
                "Long km": p.long_km if live else None,
                "Total km": p.actual_km if live else None,
                "Climb m": p.elevation_m if live else None,
                "Easy %": p.easy_pct,
                "Status": labels[p.status],
            }
        )
    return pd.DataFrame(rows)


def _plan_tab(progress: list[plan.WeekProgress]) -> None:
    today = date.today()
    active = plan.current_week(today)
    countdown = plan.days_to_race(today)
    cols = st.columns(4)
    cols[0].metric(
        "Race day", f"{plan.RACE_DATE:%b %d}", delta=f"{countdown} days", delta_color="off"
    )
    if active is not None:
        current = next(p for p in progress if p.week.number == active.number)
        cols[1].metric(
            "Current week", f"{active.number} of 17", delta=active.phase, delta_color="off"
        )
        cols[2].metric("Runs this week", f"{current.actual_runs} / {active.planned_runs}")
        cols[3].metric("Long run", f"{current.long_km:.0f} / {active.long_km:.0f} km")
    else:
        cols[1].metric("Current week", "—", delta="off-plan", delta_color="off")

    done = [p for p in progress if not p.is_future and p.actual_runs > 0]
    if done:
        easy_vals = [p.easy_pct for p in done if p.easy_pct is not None]
        avg_easy = round(sum(easy_vals) / len(easy_vals)) if easy_vals else None
        note = st.columns(3)
        completed_runs = sum(p.actual_runs for p in done)
        planned_so_far = sum(p.week.planned_runs for p in progress if not p.is_future)
        note[0].metric("Runs done / planned so far", f"{completed_runs} / {planned_so_far}")
        note[1].metric("Avg easy share", f"{avg_easy}%" if avg_easy is not None else "–")
        note[2].metric("Climb logged", f"{round(sum(p.elevation_m for p in done))} m")

    left, right = st.columns(2)
    with left:
        st.subheader("Long-run progression")
        st.caption("Dotted line is the plan; blue dots are your actual longest run each week.")
        st.plotly_chart(fig_long_progression(progress), width="stretch")
    with right:
        st.subheader("Weekly volume: plan vs actual")
        st.plotly_chart(fig_volume_plan(progress), width="stretch")

    if done:
        vleft, vright = st.columns(2)
        with vleft:
            st.subheader("Easy-pace discipline")
            st.caption("Rule 1: 80% easy. Bars below the line mean you ran too hard that week.")
            st.plotly_chart(fig_easy_discipline(progress), width="stretch")
        with vright:
            st.subheader("Vertical (elevation gained)")
            st.caption("Rule 4: vertical is non-negotiable. Flat weeks need stairs/incline work.")
            st.plotly_chart(fig_vertical(progress), width="stretch")

    st.subheader("Week by week")
    st.dataframe(_plan_table(progress), hide_index=True, width="stretch")

    st.subheader("Drill into a week")
    active_number = active.number if active is not None else 1
    week_numbers = [p.week.number for p in progress]
    chosen = st.selectbox(
        "Week",
        options=week_numbers,
        index=week_numbers.index(active_number),
        format_func=_week_label(progress),
    )
    selected = next(p for p in progress if p.week.number == chosen)
    _week_detail(selected)


def _week_label(progress: list[plan.WeekProgress]) -> Any:
    lookup = {
        p.week.number: f"Week {p.week.number} · {p.week.start:%b %d} · {p.week.phase}"
        for p in progress
    }

    def label(number: int) -> str:
        return lookup[number]

    return label


def _week_detail(progress: plan.WeekProgress) -> None:
    week = progress.week
    plan_col, actual_col = st.columns([1.15, 1])
    with plan_col:
        st.markdown(f"**Schedule — {week.phase}**" + ("  ·  down week" if week.down_week else ""))
        by_day: dict[int, list[str]] = {}
        for session in week.sessions:
            by_day.setdefault(session.day, []).append(session.label)
        lines: list[str] = []
        for offset in range(week.span_days + 1):
            day = week.start + timedelta(days=offset)
            sessions = by_day.get(offset)
            body = "  ·  ".join(sessions) if sessions else "_Rest_"
            lines.append(f"- **{day:%a %b %d}** — {body}")
        st.markdown("\n".join(lines))
        if week.note:
            st.caption(week.note)
    with actual_col:
        st.markdown("**Logged**")
        if not progress.matched:
            st.caption("No runs logged in this week yet.")
            return
        rows = [
            {
                "Date": r["date"].strftime("%a %b %d"),
                "km": r["dist_km"],
                "Pace": _mmss(r["pace_s"]) + "/km",
                "Avg HR": r["avg_hr"],
                "Easy %": (r["zones"][0] + r["zones"][1]) if r.get("zones") else None,
                "Climb m": r["elev_gain"],
                "Cadence": r["avg_cadence"],
            }
            for r in progress.matched
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def _kpi_row(runs_df: pd.DataFrame, daily_df: pd.DataFrame, pred_df: pd.DataFrame) -> None:
    latest_status = (
        daily_df.dropna(subset=["status"]).iloc[-1]["status"] if not daily_df.empty else "–"
    )
    vo2_series = runs_df.dropna(subset=["vo2"])["vo2"]
    endurance = daily_df.dropna(subset=["endurance"])["endurance"]
    columns = st.columns(6)
    columns[0].metric("Runs logged", len(runs_df))
    columns[1].metric(
        "VO₂ max",
        f"{vo2_series.iloc[-1]:.0f}" if not vo2_series.empty else "–",
        delta=f"{vo2_series.iloc[-1] - vo2_series.iloc[0]:.0f}" if len(vo2_series) > 1 else None,
    )
    columns[2].metric("Training status", latest_status.title().replace("_", " "))
    columns[3].metric("Avg decoupling", f"{runs_df['decoupling'].mean():.0f}%")
    columns[4].metric(
        "Endurance score", f"{endurance.iloc[-1]:.0f}" if not endurance.empty else "–"
    )
    if not pred_df.empty and pred_df["time_5k"].notna().any():
        columns[5].metric(
            "5K prediction", _mmss(pred_df.dropna(subset=["time_5k"]).iloc[-1]["time_5k"])
        )
    else:
        columns[5].metric("5K prediction", "–")


def main() -> None:
    st.set_page_config(page_title="Running Telemetry", layout="wide", page_icon="🏃")
    frames = load_frames()
    runs_df, daily_df, pred_df, traces, progress = (
        frames["runs"],
        frames["daily"],
        frames["pred"],
        frames["traces"],
        frames["progress"],
    )

    header = st.columns([4, 1])
    header[0].title("Madeira 25K — Training Console")
    out = plan.days_to_race(date.today())
    header[0].caption(f"{plan.RACE_NAME} · {plan.RACE_DATE:%b %d, %Y} · {out} days out.")
    if header[1].button("↻ Refresh data"):
        load_frames.clear()
        st.rerun()

    if runs_df.empty:
        st.warning("No running activities in the database yet. Run `garmin sync` first.")
        return

    _kpi_row(runs_df, daily_df, pred_df)

    tabs = st.tabs(
        [
            "Plan tracker",
            "Consistency",
            "Aerobic engine",
            "Intensity",
            "Form",
            "Recovery",
            "Race predictions",
            "Run explorer",
        ]
    )
    with tabs[0]:
        _plan_tab(progress)
    tabs = tabs[1:]

    with tabs[0]:
        st.subheader("Weekly volume")
        st.caption("Empty bars are weeks with no runs. Gaps are the main brake on your progress.")
        st.plotly_chart(fig_weekly(runs_df), width="stretch")
        if not daily_df.empty:
            st.subheader("Garmin training status")
            st.plotly_chart(fig_status(daily_df), width="stretch")

    with tabs[1]:
        left, right = st.columns(2)
        with left:
            st.subheader("Efficiency factor")
            st.caption("Speed per heartbeat — higher is a stronger aerobic base.")
            st.plotly_chart(fig_line(runs_df, "efficiency", "speed ÷ HR ×100"), width="stretch")
        with right:
            st.subheader("Aerobic decoupling")
            st.caption("HR drift within a run. Under 5% (green) is good endurance.")
            st.plotly_chart(fig_decoupling(runs_df), width="stretch")
        vleft, vright = st.columns(2)
        with vleft:
            st.subheader("VO₂ max")
            st.plotly_chart(fig_vo2(runs_df, daily_df), width="stretch")
        with vright:
            st.subheader("Endurance score")
            if not daily_df.empty and daily_df["endurance"].notna().any():
                st.plotly_chart(
                    fig_line(
                        daily_df.rename(columns={"day": "date"}), "endurance", "score", ZONES[1]
                    ),
                    width="stretch",
                )
            else:
                st.info("No endurance-score history yet.")

    with tabs[2]:
        st.subheader("Time in heart-rate zones, per run")
        st.caption(
            "A strong plan is mostly Zones 1–2 with a little hard. Yours swings Zone 3 to hard."
        )
        st.plotly_chart(fig_zones(runs_df), width="stretch")

    with tabs[3]:
        left, right = st.columns(2)
        with left:
            st.subheader("Cadence")
            st.caption("Steps/min. 170–180 is efficient; watch it fade on long runs.")
            st.plotly_chart(
                fig_line(runs_df, "avg_cadence", "steps/min", ZONES[1], reference=170),
                width="stretch",
            )
        with right:
            st.subheader("Ground contact time")
            st.caption("Milliseconds on the ground — lower is springier.")
            st.plotly_chart(fig_line(runs_df, "gct", "ms"), width="stretch")

    with tabs[4]:
        st.caption("You wear your watch mainly during runs, so daily wellness is partial.")
        if not daily_df.empty and daily_df["steps"].notna().any():
            left, right = st.columns(2)
            with left:
                st.subheader("Daily steps")
                st.plotly_chart(fig_wellness(daily_df, "steps", "steps", ACCENT), width="stretch")
            with right:
                st.subheader("Average stress")
                st.plotly_chart(fig_wellness(daily_df, "stress", "0–100", SERIOUS), width="stretch")
        if not daily_df.empty and daily_df["readiness"].notna().any():
            st.subheader("Training readiness")
            st.caption(
                "Consistently high (70–94) — recovery is not your limiter, training volume is."
            )
            st.plotly_chart(fig_wellness(daily_df, "readiness", "0–100", GOOD), width="stretch")

    with tabs[5]:
        st.subheader("Predicted race pace over time")
        st.caption(
            "Predicted times as pace per km, so all distances share one axis. Lower is faster."
        )
        if not pred_df.empty:
            st.plotly_chart(fig_predictions(pred_df), width="stretch")
            latest = pred_df.iloc[-1]
            cols = st.columns(4)
            for col, (column, (name, _)) in zip(cols, DISTANCES.items(), strict=False):
                col.metric(name, _race_time(latest[column]))
        else:
            st.info("No race predictions stored yet.")

    with tabs[6]:
        options = runs_df.sort_values("date", ascending=False)
        labels = {
            int(r.activity_id): f"{r.label} · {r.dist_km} km · {_mmss(r.pace_s)}/km"
            for r in options.itertuples()
        }

        def label_of(key: int) -> str:
            return labels[key]

        run_ids: list[int] = list(labels.keys())
        run_id = st.selectbox("Choose a run", options=run_ids, format_func=label_of)
        if run_id is None:
            return
        row = runs_df[runs_df["activity_id"] == run_id].iloc[0]
        info = st.columns(5)
        info[0].metric("Distance", f"{row['dist_km']} km")
        info[1].metric("Avg pace", _mmss(row["pace_s"]) + "/km")
        info[2].metric("Avg HR", f"{row['avg_hr']}")
        info[3].metric(
            "Decoupling", f"{row['decoupling']}%" if pd.notna(row["decoupling"]) else "–"
        )
        info[4].metric("HR drift", f"+{row['hr_drift']} bpm" if pd.notna(row["hr_drift"]) else "–")

        st.markdown("**Heart-rate drift**")
        st.caption(
            "HR vs distance. Grey bands are walk breaks; the dotted line is your starting HR. "
            "A rising line over a shaded second half is cardiac drift — the aerobic-base signal."
        )
        drift_fig = fig_hr_drift(traces, int(run_id))
        if drift_fig is not None:
            st.plotly_chart(drift_fig, width="stretch")
        else:
            st.caption("Not enough heart-rate samples for this run.")

        for channel, title, color in [
            ("pace", "Pace /km (faster is higher)", ACCENT),
            ("cadence", "Cadence (steps/min)", ZONES[1]),
            ("elevation", "Elevation (m)", MUTED),
        ]:
            figure = fig_trace(traces, int(run_id), channel, title, color)
            if figure is not None:
                st.plotly_chart(figure, width="stretch")


if __name__ == "__main__":
    main()
