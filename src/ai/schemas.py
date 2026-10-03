from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ExerciseSchema(BaseModel):
    exercise_type: str = Field(min_length=2, max_length=60)
    category: Literal["Memory", "Attention", "Reasoning", "Language", "Movement"]
    difficulty: Difficulty
    instruction: str = Field(min_length=10, max_length=600)
    content: dict[str, Any]
    expected_answer: str = Field(min_length=1, max_length=1000)
    hint: str = Field(min_length=2, max_length=300)
    estimated_seconds: int = Field(ge=15, le=600)
    scoring_type: Literal["exact_match", "fuzzy_match", "sequence_accuracy", "keyword_coverage", "open_ended", "completion"]

    @field_validator("instruction", "hint")
    @classmethod
    def safety_language(cls, value: str) -> str:
        banned = ["diagnose", "cure", "treat dementia", "guaranteed recovery"]
        if any(term in value.lower() for term in banned):
            raise ValueError("medical or misleading language is not allowed")
        return value


class EvaluationSchema(BaseModel):
    score: float = Field(ge=0, le=1)
    relevance: float = Field(ge=0, le=1)
    coherence: float = Field(ge=0, le=1)
    task_completion: float = Field(ge=0, le=1)
    feedback: str = Field(min_length=2, max_length=400)
    evaluation_tags: list[str] = Field(default_factory=list, max_length=6)
