from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher

import requests
from pydantic import ValidationError

from src.ai.prompts import EVALUATION_PROMPT_VERSION, build_evaluation_prompt
from src.ai.schemas import EvaluationSchema, ExerciseSchema
from src.utils.config import settings


@dataclass
class ScoreResult:
    raw_score: float
    normalized_score: float
    feedback: str
    scoring_method: str
    evaluator_version: str
    tags: list[str]


def _tokens(value: str) -> list[str]:
    return re.findall(r"[\w']+", value.lower())


def deterministic_open_ended_evaluation(exercise: ExerciseSchema, response: str) -> EvaluationSchema:
    """Apply a transparent lexical rubric; this is not semantic AI evaluation."""
    words = _tokens(response)
    content_tokens = set(_tokens(str(exercise.content)))
    relevance = min(1.0, 0.35 + 0.15 * sum(token in content_tokens for token in set(words))) if words else 0.0
    coherence = min(1.0, 0.35 + len(words) / 60) if words else 0.0
    task_completion = min(1.0, len(words) / 25) if words else 0.0
    score = 0.4 * relevance + 0.3 * coherence + 0.3 * task_completion
    if score >= 0.75:
        feedback = "Response is relevant and complete."
    elif score >= 0.4:
        feedback = "Add one or two concrete details that address the prompt."
    else:
        feedback = "Try a short response that directly addresses the prompt."
    return EvaluationSchema(score=score, relevance=relevance, coherence=coherence,
                            task_completion=task_completion, feedback=feedback,
                            evaluation_tags=["deterministic-rubric"])


def evaluate_open_ended(exercise: ExerciseSchema, response: str, config=settings) -> tuple[EvaluationSchema, str, str]:
    if config.llm_api_key:
        try:
            api_response = requests.post(
                f"{config.llm_base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {config.llm_api_key}"},
                json={"model": config.llm_model, "temperature": 0,
                      "response_format": {"type": "json_object"},
                      "messages": [{"role": "user", "content": build_evaluation_prompt(
                          exercise.instruction, exercise.expected_answer, response)}]},
                timeout=config.llm_timeout_seconds,
            )
            api_response.raise_for_status()
            content = api_response.json()["choices"][0]["message"]["content"]
            return EvaluationSchema.model_validate(json.loads(content)), "llm_structured", EVALUATION_PROMPT_VERSION
        except (requests.RequestException, KeyError, TypeError, json.JSONDecodeError, ValidationError):
            pass
    return deterministic_open_ended_evaluation(exercise, response), "deterministic_rubric", "local-rubric-v1"


def score_exercise(exercise: ExerciseSchema, response: str, llm_evaluator=None) -> ScoreResult:
    response = response.strip()
    expected = exercise.expected_answer.strip()
    method = exercise.scoring_type
    if method == "exact_match":
        raw = float(response.casefold() == expected.casefold())
    elif method == "fuzzy_match":
        raw = SequenceMatcher(None, response.casefold(), expected.casefold()).ratio()
    elif method == "sequence_accuracy":
        exp, got = _tokens(expected), _tokens(response)
        raw = sum(a == b for a, b in zip(exp, got)) / max(len(exp), 1)
    elif method == "keyword_coverage":
        expected_set, actual = set(_tokens(expected)), set(_tokens(response))
        raw = len(expected_set & actual) / max(len(expected_set), 1)
    elif method == "completion":
        raw = 1.0 if response.casefold() == "completed" else 0.0
    else:
        if llm_evaluator:
            result: EvaluationSchema = llm_evaluator(exercise, response)
            return ScoreResult(result.score, round(result.score * 100, 1), result.feedback,
                               "llm_structured", EVALUATION_PROMPT_VERSION, result.evaluation_tags)
        result, method, version = evaluate_open_ended(exercise, response)
        return ScoreResult(result.score, round(result.score * 100, 1), result.feedback,
                           method, version, result.evaluation_tags)
    normalized = round(max(0, min(100, raw * 100)), 1)
    feedback = "Answer is correct." if normalized >= 85 else "Review the hint and try again." if normalized >= 55 else "A lower difficulty may be more appropriate for the next activity."
    return ScoreResult(raw, normalized, feedback, method, "scoring-rules-v1",
                       ["strong" if normalized >= 85 else "developing"])
