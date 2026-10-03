from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_repository
from api.schemas import InsightsResponse
from src.analytics.insights import generate_insights
from src.analytics.metrics import attempts_frame
from src.database.repository import Repository
from src.recommendation.engine import RecommendationEngine

router = APIRouter(tags=["insights"])


@router.get("/users/{user_id}/insights", response_model=InsightsResponse)
def get_insights(user_id: int, repo: Repository = Depends(get_repository)):
    user = repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    attempts = repo.attempts(user_id)
    recommendation = RecommendationEngine().recommend(user, attempts, repo.latest_checkin(user_id),
                                                      repo.sessions(user_id))
    return generate_insights(attempts_frame(attempts), recommendation.category)

