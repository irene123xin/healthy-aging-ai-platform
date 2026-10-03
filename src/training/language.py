from src.ai.schemas import Difficulty, ExerciseSchema
from src.training.base import ExerciseGenerator


class LanguageGenerator(ExerciseGenerator):
    category = "Language"

    def generate(self, difficulty: Difficulty, seed=None) -> ExerciseSchema:
        topics = {Difficulty.easy: "a favorite meal", Difficulty.medium: "a memorable journey", Difficulty.hard: "a tradition worth preserving"}
        topic = topics[difficulty]
        return ExerciseSchema(exercise_type="guided_reflection", category=self.category, difficulty=difficulty,
            instruction=f"Write 2–4 sentences about {topic}.", content={"topic": topic, "suggested_keywords": ["detail", "feeling", "place"]},
            expected_answer="A relevant response with concrete details and complete thoughts.", hint="Include where, when, and how it felt.",
            estimated_seconds=120, scoring_type="open_ended")

