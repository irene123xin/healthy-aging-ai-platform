from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.ai.schemas import ExerciseSchema


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    display_name: str
    age_range: str
    preferred_language: str
    cognitive_goals: list[str]
    preferred_session_length: int
    preferred_training_types: list[str]
    activity_comfort_level: str
    accessibility_preferences: list[str]
    created_at: datetime


class CheckinCreate(BaseModel):
    user_id: int
    energy_level: int = Field(ge=1, le=5)
    mood: int = Field(ge=1, le=5)
    sleep_quality: int = Field(ge=1, le=5)
    available_training_time: int = Field(ge=5, le=60)
    perceived_readiness: int = Field(ge=1, le=5)


class CheckinResponse(BaseModel):
    checkin_id: int
    user_id: int
    created_at: datetime


class RecommendationRequest(BaseModel):
    user_id: int


class RecommendationResponse(BaseModel):
    category: str
    difficulty: str
    duration: int
    movement_activity: str | None
    personalization_priority: float
    completion_probability: float
    final_score: float
    completion_model: str
    explanation: str


class SessionCreate(BaseModel):
    user_id: int


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: int
    user_id: int
    completion_status: str
    start_time: datetime


class ScoreRequest(BaseModel):
    exercise: ExerciseSchema
    response: str = Field(min_length=1, max_length=4000)
    user_id: int | None = None
    session_id: int | None = None


class ScoreResponse(BaseModel):
    normalized_score: float
    feedback: str
    evaluation_method: str
    evaluator_version: str
    evaluation_tags: list[str]


class InsightsResponse(BaseModel):
    strongest: str
    weakest: str
    focus: str
    improvement: str
    decline: str
