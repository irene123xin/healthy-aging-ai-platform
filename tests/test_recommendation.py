from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
from src.recommendation.engine import RecommendationEngine


def test_recommendation_ranks_weak_stale_category(user):
    now=datetime.now(timezone.utc)
    attempts=[SimpleNamespace(category="Memory",normalized_score=42,difficulty="easy",created_at=now-timedelta(days=5)),
              SimpleNamespace(category="Attention",normalized_score=92,difficulty="medium",created_at=now)]
    result=RecommendationEngine().recommend(user,attempts)
    assert result.category == "Memory"
    assert "because" in result.explanation


def test_ml_probability_contributes_without_overriding_priority(user):
    class Predictor:
        def predict_probability(self, features):
            return (0.95 if features["category"] == "Language" else 0.20), "test_model"

    now = datetime.now(timezone.utc)
    attempts = [SimpleNamespace(category="Memory", normalized_score=25, difficulty="easy",
                                created_at=now-timedelta(days=7)),
                SimpleNamespace(category="Language", normalized_score=95, difficulty="easy",
                                created_at=now)]
    result = RecommendationEngine(Predictor()).recommend(user, attempts)
    assert result.category == "Memory"
    assert result.completion_model == "test_model"
    assert result.final_score == pytest.approx(.75 * result.personalization_priority + .25 * result.completion_probability)
