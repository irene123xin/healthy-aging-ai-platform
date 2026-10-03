from src.ai.schemas import Difficulty, ExerciseSchema
from src.training.base import ExerciseGenerator


class ReasoningGenerator(ExerciseGenerator):
    category = "Reasoning"

    def generate(self, difficulty: Difficulty, seed=None) -> ExerciseSchema:
        rng = self.rng(seed); step = {Difficulty.easy: 2, Difficulty.medium: 3, Difficulty.hard: 5}[difficulty]
        start = rng.randint(1, 12); values = [start + step * i for i in range(5)]
        return ExerciseSchema(exercise_type="number_pattern", category=self.category, difficulty=difficulty,
            instruction="What number comes next in this pattern?", content={"sequence": values},
            expected_answer=str(values[-1] + step), hint="Look at the difference between neighbors.", estimated_seconds=55, scoring_type="exact_match")

