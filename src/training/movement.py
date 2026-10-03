from src.ai.schemas import Difficulty, ExerciseSchema
from src.training.base import ExerciseGenerator


class MovementGenerator(ExerciseGenerator):
    category = "Movement"

    def generate(self, difficulty: Difficulty, seed=None) -> ExerciseSchema:
        reps = {Difficulty.easy: 3, Difficulty.medium: 5, Difficulty.hard: 7}[difficulty]
        return ExerciseSchema(exercise_type="seated_mobility", category=self.category, difficulty=difficulty,
            instruction=f"If comfortable, sit upright and make {reps} slow shoulder rolls in each direction. Stop if you feel pain, dizziness, or unsteady.",
            content={"movement": "shoulder rolls", "repetitions": reps, "optional": True}, expected_answer="completed or skipped",
            hint="Keep the motion small and comfortable.", estimated_seconds=60, scoring_type="completion")

