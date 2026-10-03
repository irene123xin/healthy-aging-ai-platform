from functools import lru_cache

from src.database.repository import Repository


@lru_cache
def get_repository() -> Repository:
    return Repository()

