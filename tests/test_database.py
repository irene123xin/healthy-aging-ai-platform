from sqlalchemy import inspect


def test_database_initialization(repo):
    names=set(inspect(repo.engine).get_table_names())
    assert {"users","daily_checkins","sessions","exercise_attempts","recommendations","ai_generations","performance_metrics","feedback_events"} <= names


def test_user_creation(repo,user):
    assert repo.get_user(user.user_id).display_name == "Test User"


def test_saving_session(repo,user):
    session=repo.start_session(user.user_id); finished=repo.complete_session(session.session_id)
    assert finished.completion_status == "completed" and finished.duration >= 0

