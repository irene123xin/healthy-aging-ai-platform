import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from src.database.repository import Repository


@pytest.fixture
def repo():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    return Repository(engine)


@pytest.fixture
def user(repo):
    return repo.create_user(display_name="Test User",age_range="60–69",preferred_language="English",cognitive_goals=["Memory"],preferred_session_length=15,preferred_training_types=["Memory"],activity_comfort_level="Seated",accessibility_preferences=[])

