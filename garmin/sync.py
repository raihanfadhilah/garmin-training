from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from garmin.client import GarminClient
from garmin.database import Database
from garmin.models import Activity, ActivityStream, Base, DailyMetric, RacePrediction
from garmin.parse import (
    activity_row,
    daily_metric_row,
    endurance_scores,
    hill_scores,
    race_prediction_row,
    wellness_row,
)


@dataclass(frozen=True)
class SyncResult:
    activities_seen: int = 0
    activities_written: int = 0
    days_written: int = 0
    streams_written: int = 0
    predictions_written: int = 0


class SyncService:
    def __init__(self, client: GarminClient, database: Database) -> None:
        self._client = client
        self._database = database

    def sync_activities(self, full: bool = False) -> SyncResult:
        stamp = _utcnow()
        seen = 0
        written = 0
        with self._database.session() as session:
            known = set() if full else self._known_activity_ids(session)
            for page in self._client.iter_activity_pages():
                new_in_page = 0
                for payload in page:
                    row = activity_row(payload)
                    activity_id = row["activity_id"]
                    if activity_id is None:
                        continue
                    seen += 1
                    if activity_id not in known:
                        new_in_page += 1
                    row["synced_at"] = stamp
                    self._upsert(session, Activity, row, "activity_id")
                    written += 1
                if not full and new_in_page == 0:
                    break
        return SyncResult(activities_seen=seen, activities_written=written)

    def sync_training(self, start: date, end: date) -> SyncResult:
        stamp = _utcnow()
        days = 0
        with self._database.session() as session:
            current = start
            while current <= end:
                cdate = current.isoformat()
                row = daily_metric_row(
                    current,
                    self._client.training_status(cdate),
                    self._client.training_readiness(cdate),
                    self._client.max_metrics(cdate),
                    self._client.hrv(cdate),
                )
                row["synced_at"] = stamp
                self._upsert(session, DailyMetric, row, "day")
                days += 1
                current += timedelta(days=1)
        return SyncResult(days_written=days)

    def sync_streams(self, refresh: bool = False) -> SyncResult:
        stamp = _utcnow()
        written = 0
        with self._database.session() as session:
            activity_ids = list(
                session.scalars(
                    select(Activity.activity_id).order_by(Activity.start_time_local.desc())
                ).all()
            )
            if not refresh:
                have = set(session.scalars(select(ActivityStream.activity_id)).all())
                activity_ids = [i for i in activity_ids if i not in have]
            for activity_id in activity_ids:
                details = self._client.activity_details(str(activity_id))
                splits = self._client.activity_splits(str(activity_id))
                row = {
                    "activity_id": activity_id,
                    "details": details if isinstance(details, dict) else None,
                    "splits": splits if isinstance(splits, dict) else None,
                    "synced_at": stamp,
                }
                self._upsert(session, ActivityStream, row, "activity_id")
                written += 1
        return SyncResult(streams_written=written)

    def sync_wellness(self, start: date, end: date) -> SyncResult:
        stamp = _utcnow()
        start_iso, end_iso = start.isoformat(), end.isoformat()
        endurance = endurance_scores(self._client.endurance_score(start_iso, end_iso))
        hills = hill_scores(self._client.hill_score(start_iso, end_iso))
        days = 0
        with self._database.session() as session:
            current = start
            while current <= end:
                iso = current.isoformat()
                row = wellness_row(current, self._client.daily_stats(iso))
                if iso in endurance:
                    row["endurance_score"] = endurance[iso]
                if iso in hills:
                    row["hill_score"] = hills[iso]
                row["synced_at"] = stamp
                self._upsert(session, DailyMetric, row, "day")
                days += 1
                current += timedelta(days=1)
        return SyncResult(days_written=days)

    def sync_race_predictions(self, start: date, end: date) -> SyncResult:
        stamp = _utcnow()
        data = self._client.race_predictions(start.isoformat(), end.isoformat())
        entries = data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
        written = 0
        with self._database.session() as session:
            for entry in entries:
                row = race_prediction_row(entry)
                day = _as_date(row["day"])
                if day is None:
                    continue
                row["day"] = day
                row["synced_at"] = stamp
                self._upsert(session, RacePrediction, row, "day")
                written += 1
        return SyncResult(predictions_written=written)

    def _known_activity_ids(self, session: Session) -> set[int]:
        return set(session.scalars(select(Activity.activity_id)).all())

    def _upsert(
        self,
        session: Session,
        model: type[Base],
        row: dict[str, Any],
        key: str,
    ) -> None:
        statement = insert(model).values(**row)
        updates = {column: getattr(statement.excluded, column) for column in row if column != key}
        statement = statement.on_conflict_do_update(index_elements=[key], set_=updates)
        session.execute(statement)


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _as_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip()[:10])
        except ValueError:
            return None
    return None
