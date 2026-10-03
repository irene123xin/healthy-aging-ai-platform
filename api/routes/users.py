from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_repository
from api.schemas import CheckinCreate, CheckinResponse, UserResponse
from src.database.repository import Repository

router = APIRouter(tags=["users"])


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, repo: Repository = Depends(get_repository)):
    user = repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/checkins", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
def create_checkin(payload: CheckinCreate, repo: Repository = Depends(get_repository)):
    if not repo.get_user(payload.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    checkin = repo.save_checkin(**payload.model_dump())
    return CheckinResponse(checkin_id=checkin.checkin_id, user_id=checkin.user_id,
                           created_at=checkin.created_at)

