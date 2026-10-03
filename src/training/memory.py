from src.ai.schemas import Difficulty, ExerciseSchema
from src.training.base import ExerciseGenerator


class MemoryGenerator(ExerciseGenerator):
    category = "Memory"

    def generate(self, difficulty: Difficulty, seed=None) -> ExerciseSchema:
        rng = self.rng(seed)
        count = {Difficulty.easy: 3, Difficulty.medium: 5, Difficulty.hard: 7}[difficulty]
        words = rng.sample(["garden", "lantern", "river", "orange", "piano", "window", "coffee", "maple", "basket", "cloud"], count)
        return ExerciseSchema(exercise_type="word_recall", category=self.category, difficulty=difficulty,
            instruction="Study the words, then type as many as you remember in any order.",
            content={"items": words, "display_seconds": count * 4}, expected_answer=", ".join(words),
            hint="Picture the objects together in one scene.", estimated_seconds=count * 12, scoring_type="keyword_coverage")

