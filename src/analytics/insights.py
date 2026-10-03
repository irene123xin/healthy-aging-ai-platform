from __future__ import annotations

import pandas as pd


def generate_insights(frame: pd.DataFrame, recommended_focus: str = "Build a baseline") -> dict[str, str]:
    if frame.empty: return {"strongest": "Not enough data", "weakest": "Not enough data", "focus": recommended_focus, "improvement": "Complete a few activities to reveal a trend", "decline": "No decline detected"}
    averages = frame.groupby("category")["score"].mean().sort_values()
    ordered = frame.sort_values("date")
    changes = ordered.groupby("category")["score"].apply(lambda x: x.tail(3).mean()-x.head(3).mean()).sort_values()
    return {"strongest": f"{averages.index[-1]} · {averages.iloc[-1]:.0f}", "weakest": f"{averages.index[0]} · {averages.iloc[0]:.0f}",
            "focus": recommended_focus, "improvement": f"{changes.index[-1]} · {changes.iloc[-1]:+.0f} points",
            "decline": f"{changes.index[0]} · {changes.iloc[0]:+.0f} points" if changes.iloc[0] < 0 else "No recent decline detected"}

