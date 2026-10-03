from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np

from src.ai.schemas import Difficulty
from src.ml.inference import CompletionPredictor
from src.recommendation.difficulty import adapt_difficulty
from src.recommendation.explainability import explain

CATEGORIES = ["Memory", "Attention", "Reasoning", "Language"]


@dataclass
class RecommendationResult:
    category: str
    difficulty: Difficulty
    duration: int
    movement_activity: str | None
    personalization_priority: float
    completion_probability: float
    final_score: float
    completion_model: str
    explanation: str

    @property
    def score(self) -> float:
        """Backward-compatible percentage used by existing callers."""
        return round(self.final_score * 100, 1)


class RecommendationEngine:
    """Rank training candidates using learning priority and estimated completion."""

    def __init__(self, predictor: CompletionPredictor | None = None):
        self.predictor = predictor or CompletionPredictor()

    def recommend(self, user, attempts, checkin=None, sessions=None) -> RecommendationResult:
        now = datetime.now(timezone.utc)
        overall = np.mean([a.normalized_score for a in attempts]) if attempts else None
        preferences = set(user.preferred_training_types or [])
        completed = [s for s in (sessions or []) if s.completion_status == "completed"]
        completion_rate = len(completed) / len(sessions) if sessions else 0.5
        duration = max(5, min(user.preferred_session_length,
                              checkin.available_training_time if checkin else user.preferred_session_length))
        candidates = []

        for category in CATEGORIES:
            rows = [attempt for attempt in attempts if attempt.category == category][:7]
            average = float(np.mean([row.normalized_score for row in rows])) if rows else None
            weakness = (100 - average) / 100 if average is not None else 0.55
            if rows:
                last = rows[0].created_at
                last = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
                days_since = max(0, (now - last).days)
                recency = min(days_since / 7, 1)
            else:
                days_since, recency = None, 0.70
            preference = 1.0 if category in preferences else 0.35
            energy = ((checkin.energy_level if checkin else 3) - 1) / 4
            exploration = 1 - min(len(rows) / 5, 1)
            priority = 0.35 * weakness + 0.25 * recency + 0.20 * preference + 0.10 * energy + 0.10 * exploration
            current = Difficulty(rows[0].difficulty) if rows else Difficulty.easy
            difficulty = adapt_difficulty(current, [row.normalized_score for row in rows])
            probability, model = self.predictor.predict_probability({
                "recent_score": rows[0].normalized_score if rows else 70,
                "rolling_average_score": average if average is not None else 70,
                "energy_level": checkin.energy_level if checkin else 3,
                "sleep_quality": checkin.sleep_quality if checkin else 3,
                "category": category,
                "current_difficulty": difficulty.value,
                "recent_completion_rate": completion_rate,
                "session_length": duration,
                "time_since_last_session": days_since if days_since is not None else 7,
            })
            final_score = 0.75 * priority + 0.25 * probability
            candidates.append((final_score, priority, probability, model, category,
                               difficulty, average, days_since))

        final_score, priority, probability, model, category, difficulty, average, days_since = max(candidates)
        explanation = explain(category, average, overall, days_since, category in preferences)
        explanation += f" The proposed {duration}-minute session has an estimated {probability:.0%} completion probability ({model.replace('_', ' ')})."
        movement = "Optional 3-minute seated mobility break" if not checkin or checkin.energy_level >= 2 else None
        return RecommendationResult(category, difficulty, duration, movement, priority,
                                    probability, final_score, model, explanation)
