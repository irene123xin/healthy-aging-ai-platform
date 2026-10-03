from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_repository
from api.schemas import ScoreRequest, ScoreResponse, SessionCreate, SessionResponse
from src.ai.evaluator import score_exercise
from src.database.repository import Repository

router = APIRouter(tags=["sessions"])


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate, repo: Repository = Depends(get_repository)):
    if not repo.get_user(payload.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session = repo.start_session(payload.user_id)
    return session


@router.post("/score", response_model=ScoreResponse)
def score(payload: ScoreRequest, repo: Repository = Depends(get_repository)):
    result = score_exercise(payload.exercise, payload.response)
    if payload.user_id is not None:
        if not repo.get_user(payload.user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        repo.save_attempt(session_id=payload.session_id, user_id=payload.user_id,
                          category=payload.exercise.category,
                          exercise_type=payload.exercise.exercise_type,
                          difficulty=payload.exercise.difficulty.value,
                          prompt_content=payload.exercise.model_dump(mode="json"),
                          response=payload.response, raw_score=result.raw_score,
                          normalized_score=result.normalized_score,
                          scoring_method=result.scoring_method,
                          evaluator_version=result.evaluator_version,
                          feedback=result.feedback)
    return ScoreResponse(normalized_score=result.normalized_score, feedback=result.feedback,
                         evaluation_method=result.scoring_method,
                         evaluator_version=result.evaluator_version,
                         evaluation_tags=result.tags)

