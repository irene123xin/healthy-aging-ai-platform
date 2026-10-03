from src.ai.schemas import Difficulty
from src.recommendation.difficulty import adapt_difficulty


def test_uses_rolling_window_to_raise_and_lower():
    assert adapt_difficulty(Difficulty.medium,[90,88,91]) == Difficulty.hard
    assert adapt_difficulty(Difficulty.medium,[40,50,54]) == Difficulty.easy
    assert adapt_difficulty(Difficulty.medium,[100]) == Difficulty.medium

