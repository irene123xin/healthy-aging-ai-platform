from src.ai.schemas import Difficulty


ORDER = [Difficulty.easy, Difficulty.medium, Difficulty.hard]


def adapt_difficulty(current: Difficulty, recent_scores: list[float], window: int = 3) -> Difficulty:
    scores = recent_scores[:window]
    if len(scores) < window: return current
    average = sum(scores) / len(scores); index = ORDER.index(current)
    if average > 85: return ORDER[min(index + 1, len(ORDER) - 1)]
    if average < 55: return ORDER[max(index - 1, 0)]
    return current

