from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete

from src.database.models import DailyCheckin, ExerciseAttempt, Recommendation, Session, User
from src.database.repository import Repository


def generate(seed: int = 42):
    rng = random.Random(seed); repo = Repository()
    with repo.SessionLocal() as db:
        demo = db.query(User).filter(User.display_name == "Demo: Margaret").first()
        if demo:
            for model in [Recommendation, ExerciseAttempt, DailyCheckin, Session]: db.execute(delete(model).where(model.user_id == demo.user_id))
            db.delete(demo); db.commit()
    user = repo.create_user(display_name="Demo: Margaret", age_range="70–79", preferred_language="English",
        cognitive_goals=["Memory","Attention"], preferred_session_length=15,
        preferred_training_types=["Memory","Language","Movement"], activity_comfort_level="Seated",
        accessibility_preferences=["Larger text","Short instructions"])
    categories=["Memory","Attention","Reasoning","Language"]
    for day in range(34,-1,-1):
        when=datetime.now(timezone.utc)-timedelta(days=day,hours=rng.randint(0,6))
        if rng.random()<.72:
            check=repo.save_checkin(user.user_id,energy_level=rng.randint(2,5),mood=rng.randint(2,5),sleep_quality=rng.randint(2,5),available_training_time=rng.choice([10,15,20]),perceived_readiness=rng.randint(2,5))
            category=categories[(34-day)%len(categories)]; session=repo.start_session(user.user_id)
            baseline={"Memory":64,"Attention":76,"Reasoning":70,"Language":80}[category]; improvement=(34-day)*.32
            score=max(30,min(100,rng.gauss(baseline+improvement,8))); difficulty="easy" if score<65 else "medium" if score<88 else "hard"
            attempt=repo.save_attempt(session_id=session.session_id,user_id=user.user_id,category=category,exercise_type="demo_activity",difficulty=difficulty,
                prompt_content={"demo":True,"instruction":"Synthetic portfolio demonstration activity"},response="Synthetic demo response",raw_score=score/100,
                normalized_score=round(score,1),scoring_method="synthetic_demo",feedback="Synthetic progress record for dashboard demonstration.")
            completed=repo.complete_session(session.session_id,"completed" if rng.random()>.08 else "incomplete")
            with repo.SessionLocal() as db:
                for item, model in [(check,DailyCheckin),(attempt,ExerciseAttempt),(completed,Session)]:
                    stored=db.get(model,getattr(item,list(model.__table__.primary_key.columns)[0].name)); stored.created_at=when if hasattr(stored,"created_at") else None
                    if isinstance(stored,Session): stored.start_time=when; stored.end_time=when+timedelta(minutes=rng.randint(8,20)); stored.duration=(stored.end_time-stored.start_time).total_seconds()/60
                db.commit()
    print(f"Created demo profile #{user.user_id} with 5 weeks of synthetic activity.")


if __name__ == "__main__": generate()
