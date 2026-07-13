from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Activity(Base):
    __tablename__ = "activities"

    activity_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String)
    type_key: Mapped[str | None] = mapped_column(String, index=True)
    start_time_local: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    start_time_gmt: Mapped[datetime | None] = mapped_column(DateTime)
    distance_m: Mapped[float | None] = mapped_column(Float)
    duration_s: Mapped[float | None] = mapped_column(Float)
    moving_duration_s: Mapped[float | None] = mapped_column(Float)
    elevation_gain_m: Mapped[float | None] = mapped_column(Float)
    elevation_loss_m: Mapped[float | None] = mapped_column(Float)
    average_speed_mps: Mapped[float | None] = mapped_column(Float)
    max_speed_mps: Mapped[float | None] = mapped_column(Float)
    average_hr: Mapped[float | None] = mapped_column(Float)
    max_hr: Mapped[float | None] = mapped_column(Float)
    calories: Mapped[float | None] = mapped_column(Float)
    steps: Mapped[int | None] = mapped_column(Integer)
    average_cadence: Mapped[float | None] = mapped_column(Float)
    max_cadence: Mapped[float | None] = mapped_column(Float)
    average_power_w: Mapped[float | None] = mapped_column(Float)
    max_power_w: Mapped[float | None] = mapped_column(Float)
    normalized_power_w: Mapped[float | None] = mapped_column(Float)
    aerobic_training_effect: Mapped[float | None] = mapped_column(Float)
    anaerobic_training_effect: Mapped[float | None] = mapped_column(Float)
    training_effect_label: Mapped[str | None] = mapped_column(String)
    training_load: Mapped[float | None] = mapped_column(Float)
    vo2max: Mapped[float | None] = mapped_column(Float)
    location_name: Mapped[str | None] = mapped_column(String)
    raw: Mapped[dict[str, Any]] = mapped_column(JSON)
    synced_at: Mapped[datetime] = mapped_column(DateTime)


class ActivityStream(Base):
    __tablename__ = "activity_streams"

    activity_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    splits: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    synced_at: Mapped[datetime] = mapped_column(DateTime)


class DailyMetric(Base):
    __tablename__ = "daily_metrics"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    training_status: Mapped[str | None] = mapped_column(String)
    acwr: Mapped[float | None] = mapped_column(Float)
    acwr_status: Mapped[str | None] = mapped_column(String)
    training_readiness: Mapped[int | None] = mapped_column(Integer)
    readiness_level: Mapped[str | None] = mapped_column(String)
    readiness_feedback: Mapped[str | None] = mapped_column(String)
    vo2max_running: Mapped[float | None] = mapped_column(Float)
    vo2max_cycling: Mapped[float | None] = mapped_column(Float)
    hrv_weekly_avg: Mapped[float | None] = mapped_column(Float)
    hrv_last_night_avg: Mapped[float | None] = mapped_column(Float)
    hrv_status: Mapped[str | None] = mapped_column(String)
    resting_hr: Mapped[int | None] = mapped_column(Integer)
    steps: Mapped[int | None] = mapped_column(Integer)
    calories: Mapped[int | None] = mapped_column(Integer)
    stress_avg: Mapped[int | None] = mapped_column(Integer)
    body_battery_high: Mapped[int | None] = mapped_column(Integer)
    body_battery_low: Mapped[int | None] = mapped_column(Integer)
    intensity_moderate: Mapped[int | None] = mapped_column(Integer)
    intensity_vigorous: Mapped[int | None] = mapped_column(Integer)
    endurance_score: Mapped[int | None] = mapped_column(Integer)
    hill_score: Mapped[int | None] = mapped_column(Integer)
    raw_training_status: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    raw_readiness: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON)
    raw_max_metrics: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON)
    raw_hrv: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    raw_stats: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    synced_at: Mapped[datetime] = mapped_column(DateTime)


class RacePrediction(Base):
    __tablename__ = "race_predictions"

    day: Mapped[date] = mapped_column(Date, primary_key=True)
    time_5k: Mapped[int | None] = mapped_column(Integer)
    time_10k: Mapped[int | None] = mapped_column(Integer)
    time_half: Mapped[int | None] = mapped_column(Integer)
    time_marathon: Mapped[int | None] = mapped_column(Integer)
    raw: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    synced_at: Mapped[datetime] = mapped_column(DateTime)
