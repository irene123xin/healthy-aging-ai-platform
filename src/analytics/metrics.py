from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd


def attempts_frame(attempts) -> pd.DataFrame:
    rows = [{"date": a.created_at, "category": a.category, "score": a.normalized_score, "difficulty": a.difficulty} for a in attempts]
    frame = pd.DataFrame(rows)
    if not frame.empty: frame["date"] = pd.to_datetime(frame["date"], utc=True)
    return frame


def engagement_metrics(sessions) -> dict:
    now = datetime.now(timezone.utc); completed = [s for s in sessions if s.completion_status == "completed"]
    this_week = [s for s in completed if now - _aware(s.start_time) <= timedelta(days=7)]
    durations = [s.duration for s in completed if s.duration is not None]
    dates = sorted({_aware(s.start_time).date() for s in completed}, reverse=True)
    streak = 0; cursor = now.date()
    if dates and dates[0] < cursor: cursor = dates[0]
    while cursor in dates: streak += 1; cursor -= timedelta(days=1)
    return {"sessions_this_week": len(this_week), "total_sessions": len(sessions),
            "average_duration": round(sum(durations)/len(durations), 1) if durations else 0,
            "completion_rate": round(100*len(completed)/len(sessions), 1) if sessions else 0, "current_streak": streak}


def _aware(value): return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

