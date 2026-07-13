import subprocess
from datetime import date, timedelta
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import func, select

from garmin.client import GarminClient
from garmin.config import Settings
from garmin.database import Database
from garmin.models import Activity, ActivityStream, DailyMetric, RacePrediction
from garmin.sync import SyncService

app = typer.Typer(
    add_completion=False,
    help="Sync Garmin Connect activities and training metrics into local SQLite.",
)
console = Console()


@app.command()
def login() -> None:
    """Authenticate with Garmin Connect and store a reusable token."""
    settings = Settings()
    email = settings.email or typer.prompt("Garmin email")
    password = settings.password or typer.prompt("Garmin password", hide_input=True)
    settings = settings.model_copy(update={"email": email, "password": password})
    client = GarminClient(settings, prompt_mfa=_prompt_mfa)
    client.login()
    console.print(f"[green]Logged in.[/] Token stored at {settings.tokenstore}")


def _connect() -> tuple[Settings, SyncService]:
    settings = Settings()
    client = GarminClient(settings)
    try:
        client.login()
    except Exception as error:
        console.print(f"[red]Login failed:[/] {error}")
        console.print("Run [bold]garmin login[/] to authenticate first.")
        raise typer.Exit(code=1) from error
    return settings, SyncService(client, Database(settings))


def _window(since: str | None, days: int | None, default_days: int) -> tuple[date, date]:
    end = date.today()
    if since is not None:
        return date.fromisoformat(since), end
    return end - timedelta(days=days if days is not None else default_days), end


@app.command()
def sync(
    full: bool = typer.Option(False, "--full", help="Re-fetch all activities, not just new ones."),
    since: str | None = typer.Option(None, "--since", help="Daily-metric start date (YYYY-MM-DD)."),
    days: int | None = typer.Option(None, "--days", help="Daily-metric lookback window in days."),
    activities: bool = typer.Option(True, "--activities/--no-activities"),
    training: bool = typer.Option(True, "--training/--no-training"),
    wellness: bool = typer.Option(True, "--wellness/--no-wellness"),
    predictions: bool = typer.Option(True, "--predictions/--no-predictions"),
    streams: bool = typer.Option(True, "--streams/--no-streams", help="Per-activity time series."),
    refresh_streams: bool = typer.Option(
        False, "--refresh-streams", help="Re-fetch existing streams."
    ),
) -> None:
    """Pull activities, time series, and daily training + wellness metrics into the database."""
    settings, service = _connect()
    if activities:
        result = service.sync_activities(full=full)
        console.print(
            f"Activities: {result.activities_written} written, {result.activities_seen} seen."
        )
    if streams or refresh_streams:
        result = service.sync_streams(refresh=refresh_streams)
        console.print(f"Streams: {result.streams_written} activities.")
    start, end = _window(since, days, settings.training_lookback_days)
    if training:
        result = service.sync_training(start, end)
        console.print(f"Training: {result.days_written} days ({start} to {end}).")
    if wellness:
        result = service.sync_wellness(start, end)
        console.print(f"Wellness: {result.days_written} days.")
    if predictions:
        result = service.sync_race_predictions(start, end)
        console.print(f"Race predictions: {result.predictions_written} days.")


@app.command()
def backfill(
    since: str = typer.Option("2024-01-01", "--since", help="Pull everything from this date."),
    refresh_streams: bool = typer.Option(False, "--refresh-streams", help="Re-fetch time series."),
) -> None:
    """One-shot deep pull: full history of activities, time series, and daily metrics."""
    settings, service = _connect()
    start, end = date.fromisoformat(since), date.today()
    a = service.sync_activities(full=True)
    console.print(f"Activities: {a.activities_written} written.")
    s = service.sync_streams(refresh=refresh_streams)
    console.print(f"Streams: {s.streams_written} activities.")
    console.print(f"Backfilling daily metrics {start} to {end} (this makes many API calls)...")
    t = service.sync_training(start, end)
    console.print(f"Training: {t.days_written} days.")
    w = service.sync_wellness(start, end)
    console.print(f"Wellness: {w.days_written} days.")
    p = service.sync_race_predictions(start, end)
    console.print(f"Race predictions: {p.predictions_written} days.")


@app.command()
def dashboard(
    port: int = typer.Option(8501, "--port", help="Port for the local dashboard server."),
) -> None:
    """Launch the interactive Streamlit dashboard against the local database."""
    app_path = Path(__file__).parent / "dashboard.py"
    subprocess.run(
        ["uv", "run", "streamlit", "run", str(app_path), "--server.port", str(port)],
        check=False,
    )


@app.command()
def mcp() -> None:
    """Run the MCP server (stdio) exposing training data as tools for AI clients."""
    from garmin.mcp import main as run_server

    run_server()


@app.command()
def status() -> None:
    """Show what is currently stored in the database."""
    settings = Settings()
    database = Database(settings)
    with database.session() as session:
        activity_count = session.scalar(select(func.count()).select_from(Activity)) or 0
        latest_activity = session.scalar(select(func.max(Activity.start_time_local)))
        metric_count = session.scalar(select(func.count()).select_from(DailyMetric)) or 0
        latest_metric = session.scalar(select(func.max(DailyMetric.day)))
        stream_count = session.scalar(select(func.count()).select_from(ActivityStream)) or 0
        prediction_count = session.scalar(select(func.count()).select_from(RacePrediction)) or 0

    table = Table(title="Garmin sync status")
    table.add_column("Item")
    table.add_column("Value")
    table.add_row("Database", str(settings.db_path))
    table.add_row("Token store", str(settings.tokenstore))
    table.add_row("Tokens present", "yes" if Path(settings.tokenstore).exists() else "no")
    table.add_row("Activities", str(activity_count))
    table.add_row("Latest activity", str(latest_activity) if latest_activity else "-")
    table.add_row("Time series stored", str(stream_count))
    table.add_row("Daily metrics", str(metric_count))
    table.add_row("Latest metric day", str(latest_metric) if latest_metric else "-")
    table.add_row("Race predictions", str(prediction_count))
    console.print(table)


@app.command()
def activities(
    limit: int = typer.Option(10, "--limit", help="Number of activities to show."),
) -> None:
    """List the most recent activities stored locally."""
    settings = Settings()
    database = Database(settings)
    with database.session() as session:
        rows = list(
            session.scalars(
                select(Activity).order_by(Activity.start_time_local.desc()).limit(limit)
            ).all()
        )

    table = Table(title=f"Latest {len(rows)} activities")
    for column in ("Date", "Type", "Name", "Dist km", "Dur min", "Avg HR", "Aerobic TE"):
        table.add_column(column)
    for row in rows:
        table.add_row(
            row.start_time_local.strftime("%Y-%m-%d %H:%M") if row.start_time_local else "-",
            row.type_key or "-",
            (row.name or "-")[:32],
            f"{row.distance_m / 1000:.2f}" if row.distance_m else "-",
            f"{row.duration_s / 60:.0f}" if row.duration_s else "-",
            f"{row.average_hr:.0f}" if row.average_hr else "-",
            f"{row.aerobic_training_effect:.1f}" if row.aerobic_training_effect else "-",
        )
    console.print(table)


def _prompt_mfa() -> str:
    return str(typer.prompt("Garmin MFA code"))


if __name__ == "__main__":
    app()
