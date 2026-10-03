from src.ai.schemas import Difficulty, ExerciseSchema
from src.training.base import ExerciseGenerator


class AttentionGenerator(ExerciseGenerator):
    category = "Attention"

    def generate(self, difficulty: Difficulty, seed=None) -> ExerciseSchema:
        rng = self.rng(seed); length = {Difficulty.easy: 8, Difficulty.medium: 12, Difficulty.hard: 16}[difficulty]
        target = rng.choice([3, 7, 9]); sequence = [rng.randint(1, 9) for _ in range(length)]
        return ExerciseSchema(exercise_type="target_count", category=self.category, difficulty=difficulty,
            instruction=f"Count how many times the number {target} appears.", content={"sequence": sequence, "target": target},
            expected_answer=str(sequence.count(target)), hint="Scan once from left to right.", estimated_seconds=45, scoring_type="exact_match")

