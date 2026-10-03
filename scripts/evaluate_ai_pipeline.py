from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ai.client import LLMClient
from src.ai.schemas import Difficulty, ExerciseSchema
from src.database.repository import Repository
from src.training.factory import ExerciseFactory
from src.utils.config import settings


def evaluate() -> dict:
    categories = list(ExerciseFactory().generators)
    difficulties = list(Difficulty)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    repo = Repository(engine)
    client = LLMClient(repo)
    records = []
    for category in categories:
        for difficulty in difficulties:
            started = time.perf_counter()
            exercise = client.generate_exercise({}, category, difficulty, seed=42)
            latency_ms = (time.perf_counter() - started) * 1000
            records.append({"category": exercise.category, "difficulty": exercise.difficulty.value,
                            "schema_valid": isinstance(ExerciseSchema.model_validate(exercise), ExerciseSchema),
                            "latency_ms": latency_ms})
    offline = not bool(settings.llm_api_key)
    diagnostics = repo.ai_diagnostics()
    return {
        "mode": "fallback/offline evaluation" if offline else "configured API evaluation",
        "sample_count": len(records),
        "schema_valid_rate": sum(row["schema_valid"] for row in records) / len(records),
        "generation_success_rate": diagnostics["success_rate"] / 100,
        "fallback_rate": diagnostics["fallback_rate"] / 100,
        "average_latency_ms": diagnostics["average_latency_ms"],
        "category_coverage": dict(Counter(row["category"] for row in records)),
        "difficulty_coverage": dict(Counter(row["difficulty"] for row in records)),
        "note": "Rates are measured from this batch only." if not offline else "All outputs came from deterministic local generators.",
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
