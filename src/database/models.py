from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(80))
    age_range: Mapped[str] = mapped_column(String(20))
    preferred_language: Mapped[str] = mapped_column(String(30), default="English")
    cognitive_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_session_length: Mapped[int] = mapped_column(Integer, default=15)
    preferred_training_types: Mapped[list[str]] = mapped_column(JSON, default=list)
    activity_comfort_level: Mapped[str] = mapped_column(String(20), default="Seated")
    accessibility_preferences: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DailyCheckin(Base):
    __tablename__ = "daily_checkins"
    checkin_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    energy_level: Mapped[int] = mapped_column(Integer)
    mood: Mapped[int] = mapped_column(Integer)
    sleep_quality: Mapped[int] = mapped_column(Integer)
    available_training_time: Mapped[int] = mapped_column(Integer)
    perceived_readiness: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class Session(Base):
    __tablename__ = "sessions"
    session_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration: Mapped[float | None] = mapped_column(Float)
    completion_status: Mapped[str] = mapped_column(String(20), default="started")


class ExerciseAttempt(Base):
    __tablename__ = "exercise_attempts"
    attempt_id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("sessions.session_id", ondelete="SET NULL"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(30), index=True)
    exercise_type: Mapped[str] = mapped_column(String(50))
    difficulty: Mapped[str] = mapped_column(String(10))
    prompt_content: Mapped[dict[str, Any]] = mapped_column(JSON)
    response: Mapped[str] = mapped_column(Text, default="")
    raw_score: Mapped[float] = mapped_column(Float)
    normalized_score: Mapped[float] = mapped_column(Float, index=True)
    scoring_method: Mapped[str] = mapped_column(String(50))
    evaluator_version: Mapped[str] = mapped_column(String(40), default="scoring-rules-v1")
    feedback: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class Recommendation(Base):
    __tablename__ = "recommendations"
    recommendation_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(30))
    difficulty: Mapped[str] = mapped_column(String(10))
    duration: Mapped[int] = mapped_column(Integer)
    movement_activity: Mapped[str | None] = mapped_column(String(100))
    personalization_priority: Mapped[float] = mapped_column(Float)
    completion_probability: Mapped[float] = mapped_column(Float)
    final_score: Mapped[float] = mapped_column(Float)
    completion_model: Mapped[str] = mapped_column(String(80))
    explanation: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AIGeneration(Base):
    __tablename__ = "ai_generations"
    generation_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"))
    provider: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(80))
    success: Mapped[bool] = mapped_column(Boolean)
    validation_failure: Mapped[bool] = mapped_column(Boolean, default=False)
    schema_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    prompt_version: Mapped[str] = mapped_column(String(40), default="exercise-v1")
    generation_source: Mapped[str] = mapped_column(String(20), default="fallback")
    latency_ms: Mapped[float] = mapped_column(Float)
    estimated_tokens: Mapped[int | None] = mapped_column(Integer)
    error_type: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    metric_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(30))
    metric_name: Mapped[str] = mapped_column(String(50))
    metric_value: Mapped[float] = mapped_column(Float)
    window_days: Mapped[int] = mapped_column(Integer)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"
    feedback_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    attempt_id: Mapped[int | None] = mapped_column(ForeignKey("exercise_attempts.attempt_id", ondelete="SET NULL"))
    event_type: Mapped[str] = mapped_column(String(30))
    value: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
