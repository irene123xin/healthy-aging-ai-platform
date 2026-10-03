from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, prepare_features
from src.utils.config import ROOT, settings


def synthetic_data(rows: int = 1200, seed: int = 42) -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(seed); categories = np.array(["Memory", "Attention", "Reasoning", "Language"]); difficulties = np.array(["easy", "medium", "hard"])
    frame = pd.DataFrame({"recent_score": rng.normal(70, 17, rows).clip(0,100), "rolling_average_score": rng.normal(72,12,rows).clip(0,100),
        "energy_level": rng.integers(1,6,rows), "sleep_quality": rng.integers(1,6,rows), "category": rng.choice(categories,rows),
        "current_difficulty": rng.choice(difficulties,rows,p=[.4,.4,.2]), "recent_completion_rate": rng.uniform(0,1,rows),
        "session_length": rng.choice([5,10,15,20,30],rows), "time_since_last_session": rng.exponential(3,rows).clip(0,30)})
    logits = -2.2 + .018*frame.recent_score + .28*frame.energy_level + .25*frame.sleep_quality + 1.2*frame.recent_completion_rate - .025*frame.session_length - .035*frame.time_since_last_session
    probability = 1/(1+np.exp(-logits)); target = pd.Series(rng.binomial(1, probability), name="completed")
    return frame, target


def train(output_path: Path = settings.model_path, metrics_path: Path | None = None) -> dict:
    x, y = synthetic_data(); x_train, x_test, y_train, y_test = train_test_split(prepare_features(x), y, test_size=.25, stratify=y, random_state=42)
    preprocess = ColumnTransformer([("num", StandardScaler(), NUMERIC_FEATURES), ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)])
    models = {"logistic_regression": LogisticRegression(max_iter=1000), "random_forest": RandomForestClassifier(n_estimators=180, max_depth=8, random_state=42), "gradient_boosting": GradientBoostingClassifier(random_state=42)}
    results, fitted = {}, {}
    for name, model in models.items():
        pipe = Pipeline([("features", preprocess), ("model", model)]); pipe.fit(x_train,y_train); pred=pipe.predict(x_test); prob=pipe.predict_proba(x_test)[:,1]
        results[name] = {"accuracy": accuracy_score(y_test,pred), "precision": precision_score(y_test,pred,zero_division=0), "recall": recall_score(y_test,pred,zero_division=0), "f1": f1_score(y_test,pred,zero_division=0), "roc_auc": roc_auc_score(y_test,prob)}; fitted[name]=pipe
    best = max(results, key=lambda name: results[name]["roc_auc"]); output_path.parent.mkdir(parents=True, exist_ok=True); joblib.dump({"pipeline": fitted[best], "model_name": best, "metrics": results}, output_path)
    metrics_path = metrics_path or output_path.with_suffix(".json"); metrics_path.write_text(json.dumps({"selected_model": best, "models": results}, indent=2))
    return {"selected_model": best, "models": results}


if __name__ == "__main__": print(json.dumps(train(), indent=2))

