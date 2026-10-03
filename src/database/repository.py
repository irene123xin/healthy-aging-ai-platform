from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import sessionmaker

from src.database.init_db import init_db
from src.database.models import AIGeneration, DailyCheckin, ExerciseAttempt, Recommendation, Session, User


class Repository:
    def __init__(self, engine=None):
        self.engine = init_db(engine)
        self.SessionLocal = sessionmaker(self.engine, expire_on_commit=False)

    def create_user(self, **data) -> User:
        with self.SessionLocal() as db:
            user = User(**data)
            db.add(user); db.commit(); db.refresh(user)
            return user

    def update_user(self, user_id: int, **data) -> User:
        with self.SessionLocal() as db:
            user = db.get(User, user_id)
            if not user: raise ValueError("User not found")
            for key, value in data.items(): setattr(user, key, value)
            db.commit(); db.refresh(user); return user

    def get_user(self, user_id: int) -> User | None:
        with self.SessionLocal() as db: return db.get(User, user_id)

    def list_users(self) -> list[User]:
        with self.SessionLocal() as db: return list(db.scalars(select(User).order_by(User.created_at)))

    def save_checkin(self, user_id: int, **data) -> DailyCheckin:
        with self.SessionLocal() as db:
            item = DailyCheckin(user_id=user_id, **data); db.add(item); db.commit(); db.refresh(item); return item

    def latest_checkin(self, user_id: int) -> DailyCheckin | None:
        with self.SessionLocal() as db:
            return db.scalar(select(DailyCheckin).where(DailyCheckin.user_id == user_id).order_by(desc(DailyCheckin.created_at)).limit(1))

    def start_session(self, user_id: int) -> Session:
        with self.SessionLocal() as db:
            item = Session(user_id=user_id); db.add(item); db.commit(); db.refresh(item); return item

    def complete_session(self, session_id: int, status: str = "completed") -> Session:
        with self.SessionLocal() as db:
            item = db.get(Session, session_id)
            if not item: raise ValueError("Session not found")
            item.end_time = datetime.now(timezone.utc)
            start = item.start_time if item.start_time.tzinfo else item.start_time.replace(tzinfo=timezone.utc)
            item.duration = max(0, (item.end_time - start).total_seconds() / 60)
            item.completion_status = status; db.commit(); db.refresh(item); return item

    def save_attempt(self, **data) -> ExerciseAttempt:
        with self.SessionLocal() as db:
            item = ExerciseAttempt(**data); db.add(item); db.commit(); db.refresh(item); return item

    def attempts(self, user_id: int, category: str | None = None, limit: int | None = None) -> list[ExerciseAttempt]:
        query = select(ExerciseAttempt).where(ExerciseAttempt.user_id == user_id)
        if category: query = query.where(ExerciseAttempt.category == category)
        query = query.order_by(desc(ExerciseAttempt.created_at))
        if limit: query = query.limit(limit)
        with self.SessionLocal() as db: return list(db.scalars(query))

    def sessions(self, user_id: int) -> list[Session]:
        with self.SessionLocal() as db:
            return list(db.scalars(select(Session).where(Session.user_id == user_id).order_by(desc(Session.start_time))))

    def save_recommendation(self, **data) -> Recommendation:
        with self.SessionLocal() as db:
            item = Recommendation(**data); db.add(item); db.commit(); db.refresh(item); return item

    def log_ai_generation(self, **data) -> AIGeneration:
        with self.SessionLocal() as db:
            item = AIGeneration(**data); db.add(item); db.commit(); db.refresh(item); return item

    def ai_diagnostics(self) -> dict[str, float]:
        with self.SessionLocal() as db:
            rows = list(db.scalars(select(AIGeneration)))
        count = len(rows)
        return {
            "requests": count,
            "success_rate": 100 * sum(x.success for x in rows) / count if count else 0,
            "validation_failures": sum(x.validation_failure for x in rows),
            "schema_valid_rate": 100 * sum(x.schema_valid for x in rows) / count if count else 0,
            "fallback_rate": 100 * sum(x.fallback_used for x in rows) / count if count else 0,
            "average_latency_ms": sum(x.latency_ms for x in rows) / count if count else 0,
            "api_errors": sum(bool(x.error_type) for x in rows),
            "estimated_tokens": sum(x.estimated_tokens or 0 for x in rows),
        }
