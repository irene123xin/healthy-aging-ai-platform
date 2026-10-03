from pathlib import Path
from src.ml.inference import CompletionPredictor


def test_ml_inference_fallback(tmp_path: Path):
    probability,method=CompletionPredictor(tmp_path/"missing.joblib").predict_probability({"energy_level":3,"recent_completion_rate":.5,"session_length":15})
    assert 0 <= probability <= 1
    assert method == "rule_based_fallback"
