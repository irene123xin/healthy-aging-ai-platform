from sqlalchemy import text

from src.database.init_db import make_engine


def test_sqlite_configuration_enables_foreign_keys(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'configured.db'}")
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar() == 1
