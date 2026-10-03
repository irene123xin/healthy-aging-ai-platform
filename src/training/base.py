from __future__ import annotations

import random
from abc import ABC, abstractmethod

from src.ai.schemas import Difficulty, ExerciseSchema


class ExerciseGenerator(ABC):
    category: str

    @abstractmethod
    def generate(self, difficulty: Difficulty, seed: int | None = None) -> ExerciseSchema: ...

    @staticmethod
    def rng(seed: int | None) -> random.Random:
        return random.Random(seed)

