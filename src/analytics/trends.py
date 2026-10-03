import pandas as pd


def performance_trend(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty: return frame
    data = frame.copy().sort_values("date")
    data["rolling_score"] = data.groupby("category")["score"].transform(lambda x: x.rolling(5, min_periods=1).mean())
    return data


def difficulty_trend(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty: return frame
    data = frame.copy(); data["difficulty_value"] = data["difficulty"].map({"easy": 1, "medium": 2, "hard": 3})
    return data.sort_values("date")

