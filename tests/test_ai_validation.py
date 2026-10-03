import pytest
from pydantic import ValidationError
from src.ai.client import LLMClient
from src.ai.schemas import Difficulty, ExerciseSchema


def test_schema_rejects_unsafe_instruction():
    with pytest.raises(ValidationError):
        ExerciseSchema(exercise_type="x1",category="Movement",difficulty="easy",instruction="This will diagnose your medical condition today.",content={},expected_answer="done",hint="Move gently.",estimated_seconds=30,scoring_type="completion")


def test_no_key_uses_fallback(repo,user):
    class Config:
        llm_api_key=None; llm_model="none"; llm_max_retries=0; llm_base_url=""; llm_timeout_seconds=1
    result=LLMClient(repo,Config()).generate_exercise(user.__dict__,"Memory",Difficulty.easy,user.user_id,seed=1)
    assert result.category == "Memory"
    assert repo.ai_diagnostics()["fallback_rate"] == 100

