from __future__ import annotations

import pandas as pd

FEATURE_COLUMNS = ["recent_score", "rolling_average_score", "energy_level", "sleep_quality", "category", "current_difficulty", "recent_completion_rate", "session_length", "time_since_last_session"]
NUMERIC_FEATURES = ["recent_score", "rolling_average_score", "energy_level", "sleep_quality", "recent_completion_rate", "session_length", "time_since_last_session"]
CATEGORICAL_FEATURES = ["category", "current_difficulty"]


def prepare_features(data) -> pd.DataFrame:
    frame = pd.DataFrame(data)
    for column in FEATURE_COLUMNS:
        if column not in frame: frame[column] = 0 if column in NUMERIC_FEATURES else "unknown"
    return frame[FEATURE_COLUMNS]

