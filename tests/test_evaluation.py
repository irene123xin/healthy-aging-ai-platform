import pytest
from pydantic import ValidationError

from src.ai.evaluator import evaluate_open_ended
from src.ai.schemas import Difficulty, EvaluationSchema, ExerciseSchema


def open_exercise():
    return ExerciseSchema(exercise_type="reflection", category="Language",
        difficulty=Difficulty.easy, instruction="Write two sentences about a favorite meal.",
        content={"topic": "favorite meal"}, expected_answer="A relevant response with detail.",
        hint="Mention one detail.", estimated_seconds=60, scoring_type="open_ended")


def test_structured_evaluation_validation():
    result = EvaluationSchema(score=.7, relevance=.8, coherence=.7,
        task_completion=.6, feedback="Relevant response.", evaluation_tags=["relevant"])
    assert result.score == .7
    with pytest.raises(ValidationError):
        EvaluationSchema(score=1.2, relevance=.8, coherence=.7,
            task_completion=.6, feedback="Invalid.", evaluation_tags=[])


def test_evaluation_uses_named_fallback_without_key():
    class Config:
        llm_api_key = None
    result, method, version = evaluate_open_ended(open_exercise(), "I enjoyed soup with my family. It was warm and savory.", Config())
    assert 0 <= result.score <= 1
    assert method == "deterministic_rubric"
    assert version == "local-rubric-v1"

