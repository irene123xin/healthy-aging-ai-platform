from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from src.database.models import Base
from src.utils.config import settings


def make_engine(url: str | None = None) -> Engine:
    database_url = url or settings.database_url
    if database_url.startswith("sqlite:///"):
        Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(database_url, future=True)
    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return engine


def init_db(engine: Engine | None = None) -> Engine:
    engine = engine or make_engine()
    Base.metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    init_db()
    print("Database initialized.")

