from __future__ import annotations

from pathlib import Path

import joblib

from src.ml.features import prepare_features
from src.utils.config import settings


class CompletionPredictor:
    def __init__(self, model_path: Path = settings.model_path):
        self.model_path = Path(model_path); self.bundle = None
        try: self.bundle = joblib.load(self.model_path) if self.model_path.exists() else None
        except Exception: self.bundle = None

    @property
    def available(self): return self.bundle is not None

    def predict_probability(self, features: dict) -> tuple[float, str]:
        if self.bundle:
            probability = float(self.bundle["pipeline"].predict_proba(prepare_features([features]))[0,1])
            return probability, self.bundle["model_name"]
        energy = float(features.get("energy_level",3)); completion = float(features.get("recent_completion_rate",.5)); duration=float(features.get("session_length",15))
        return max(.05,min(.95,.25+.09*energy+.35*completion-.008*max(duration-15,0))), "rule_based_fallback"
