from __future__ import annotations

import json
import time

import requests
from pydantic import ValidationError

from src.ai.prompts import EXERCISE_PROMPT_VERSION, build_exercise_prompt
from src.ai.schemas import Difficulty, ExerciseSchema
from src.training.factory import ExerciseFactory
from src.utils.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self, repository=None, config=settings):
        self.repo, self.config = repository, config

    def _record(self, **values):
        if self.repo: self.repo.log_ai_generation(**values)

    def generate_exercise(self, profile: dict, category: str, difficulty: Difficulty, user_id=None, seed=None) -> ExerciseSchema:
        started = time.perf_counter(); error = None; validation_failure = False
        if self.config.llm_api_key:
            prompt = build_exercise_prompt(profile, category, difficulty.value)
            for attempt in range(self.config.llm_max_retries + 1):
                try:
                    response = requests.post(f"{self.config.llm_base_url.rstrip('/')}/chat/completions",
                        headers={"Authorization": f"Bearer {self.config.llm_api_key}"},
                        json={"model": self.config.llm_model, "temperature": 0.4, "response_format": {"type": "json_object"},
                              "messages": [{"role": "user", "content": prompt}]}, timeout=self.config.llm_timeout_seconds)
                    response.raise_for_status()
                    payload = response.json(); text = payload["choices"][0]["message"]["content"]
                    exercise = ExerciseSchema.model_validate(json.loads(text))
                    self._record(user_id=user_id, provider="openai-compatible", model=self.config.llm_model, success=True,
                        validation_failure=False, schema_valid=True, fallback_used=False,
                        prompt_version=EXERCISE_PROMPT_VERSION, generation_source="api", latency_ms=(time.perf_counter()-started)*1000,
                        estimated_tokens=payload.get("usage", {}).get("total_tokens"), error_type=None)
                    return exercise
                except (json.JSONDecodeError, ValidationError) as exc:
                    validation_failure, error = True, type(exc).__name__
                except (requests.RequestException, KeyError, TypeError) as exc:
                    error = type(exc).__name__
                logger.warning("LLM generation attempt %s failed: %s", attempt + 1, error)
        exercise = ExerciseFactory().generate(category, difficulty, seed)
        self._record(user_id=user_id, provider="local", model="deterministic-fallback", success=not bool(error),
            validation_failure=validation_failure, schema_valid=True, fallback_used=True,
            prompt_version=EXERCISE_PROMPT_VERSION, generation_source="fallback", latency_ms=(time.perf_counter()-started)*1000,
            estimated_tokens=0, error_type=error)
        return exercise
