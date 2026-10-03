from src.ai.evaluator import score_exercise
from src.ai.schemas import Difficulty, ExerciseSchema


def exercise(method="exact_match",expected="4"):
    return ExerciseSchema(exercise_type="test",category="Attention",difficulty=Difficulty.easy,instruction="Provide the requested answer.",content={},expected_answer=expected,hint="Take your time.",estimated_seconds=30,scoring_type=method)


def test_exact_and_fuzzy_scoring():
    assert score_exercise(exercise(),"4").normalized_score == 100
    assert score_exercise(exercise("fuzzy_match","garden"),"gardan").normalized_score > 70


def test_keyword_and_open_ended_scoring():
    assert score_exercise(exercise("keyword_coverage","red blue green"),"blue and red").normalized_score > 60
    assert score_exercise(exercise("open_ended","details"),"I remember a sunny garden near our house with red flowers.").normalized_score > 40

