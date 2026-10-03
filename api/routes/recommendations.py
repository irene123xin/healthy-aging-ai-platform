from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_repository
from api.schemas import RecommendationRequest, RecommendationResponse
from src.database.repository import Repository
from src.recommendation.engine import RecommendationEngine

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def create_recommendation(payload: RecommendationRequest, repo: Repository = Depends(get_repository)):
    user = repo.get_user(payload.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = RecommendationEngine().recommend(user, repo.attempts(user.user_id),
                                              repo.latest_checkin(user.user_id), repo.sessions(user.user_id))
    repo.save_recommendation(user_id=user.user_id, category=result.category,
                             difficulty=result.difficulty.value, duration=result.duration,
                             movement_activity=result.movement_activity,
                             personalization_priority=result.personalization_priority,
                             completion_probability=result.completion_probability,
                             final_score=result.final_score,
                             completion_model=result.completion_model,
                             explanation=result.explanation)
    return RecommendationResponse(category=result.category, difficulty=result.difficulty.value,
                                  duration=result.duration, movement_activity=result.movement_activity,
                                  personalization_priority=result.personalization_priority,
                                  completion_probability=result.completion_probability,
                                  final_score=result.final_score,
                                  completion_model=result.completion_model,
                                  explanation=result.explanation)

