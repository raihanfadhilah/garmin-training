import time
from collections.abc import Callable, Iterator
from typing import Any

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
)

from garmin.config import Settings


class GarminClient:
    def __init__(
        self,
        settings: Settings,
        prompt_mfa: Callable[[], str] | None = None,
    ) -> None:
        self._settings = settings
        self._prompt_mfa = prompt_mfa
        self._api: Garmin | None = None

    def login(self) -> None:
        api = Garmin(
            email=self._settings.email,
            password=self._settings.password,
            prompt_mfa=self._prompt_mfa,
            retry_attempts=self._settings.login_retries,
        )
        api.login(str(self._settings.tokenstore))
        self._api = api

    @property
    def api(self) -> Garmin:
        if self._api is None:
            raise RuntimeError("Client is not logged in; call login() first")
        return self._api

    def iter_activity_pages(self, batch: int = 100) -> Iterator[list[dict[str, Any]]]:
        start = 0
        while True:
            page = self.api.get_activities(start, batch)
            items = _as_activity_list(page)
            if not items:
                return
            yield items
            if len(items) < batch:
                return
            start += batch
            self._pause()

    def activity_details(self, activity_id: str) -> Any:
        return self._safe(self.api.get_activity_details, activity_id)

    def activity_splits(self, activity_id: str) -> Any:
        return self._safe(self.api.get_activity_split_summaries, activity_id)

    def training_status(self, cdate: str) -> Any:
        return self._safe(self.api.get_training_status, cdate)

    def training_readiness(self, cdate: str) -> Any:
        return self._safe(self.api.get_training_readiness, cdate)

    def max_metrics(self, cdate: str) -> Any:
        return self._safe(self.api.get_max_metrics, cdate)

    def hrv(self, cdate: str) -> Any:
        return self._safe(self.api.get_hrv_data, cdate)

    def daily_stats(self, cdate: str) -> Any:
        return self._safe(self.api.get_stats, cdate)

    def endurance_score(self, start: str, end: str) -> Any:
        return self._safe(self.api.get_endurance_score, start, end)

    def hill_score(self, start: str, end: str) -> Any:
        return self._safe(self.api.get_hill_score, start, end)

    def race_predictions(self, start: str, end: str) -> Any:
        return self._safe(self.api.get_race_predictions, start, end, "daily")

    def _safe(self, func: Callable[..., Any], *args: Any) -> Any:
        try:
            return func(*args)
        except (GarminConnectTooManyRequestsError, GarminConnectAuthenticationError):
            raise
        except Exception:
            return None

    def _pause(self) -> None:
        if self._settings.request_delay > 0:
            time.sleep(self._settings.request_delay)


def _as_activity_list(page: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
    if isinstance(page, list):
        return [item for item in page if isinstance(item, dict)]
    if isinstance(page, dict):
        items = page.get("activities")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    return []
