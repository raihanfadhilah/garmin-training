from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from garmin.config import Settings
from garmin.models import Base


class Database:
    def __init__(self, settings: Settings) -> None:
        settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(settings.db_url)
        Base.metadata.create_all(self._engine)
        self._add_missing_columns()
        self._sessions = sessionmaker(bind=self._engine, expire_on_commit=False)

    def _add_missing_columns(self) -> None:
        inspector = inspect(self._engine)
        with self._engine.begin() as connection:
            for table in Base.metadata.sorted_tables:
                if not inspector.has_table(table.name):
                    continue
                existing = {column["name"] for column in inspector.get_columns(table.name)}
                for column in table.columns:
                    if column.name in existing:
                        continue
                    ddl = column.type.compile(dialect=self._engine.dialect)
                    connection.execute(
                        text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {ddl}')
                    )

    @property
    def engine(self) -> Engine:
        return self._engine

    @contextmanager
    def session(self) -> Iterator[Session]:
        session = self._sessions()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
