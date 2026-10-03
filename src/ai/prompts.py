import json

EXERCISE_PROMPT_VERSION = "exercise-v2"
EVALUATION_PROMPT_VERSION = "evaluation-v1"


def build_exercise_prompt(profile: dict, category: str, difficulty: str) -> str:
    safe_profile = {k: profile.get(k) for k in ["age_range", "preferred_language", "cognitive_goals", "accessibility_preferences"]}
    return f"""Create one safe, encouraging wellness exercise for an older adult.
Profile: {json.dumps(safe_profile)}
Category: {category}; difficulty: {difficulty}.
Return only JSON matching: exercise_type, category, difficulty, instruction, content (object), expected_answer, hint, estimated_seconds, scoring_type.
Allowed scoring_type: exact_match, fuzzy_match, sequence_accuracy, keyword_coverage, open_ended, completion.
Never diagnose, treat, shame, or request medical information. Movement must be optional and conservative."""


def build_evaluation_prompt(instruction: str, expected: str, response: str) -> str:
    return f"""Evaluate the response to this wellness exercise. Return only JSON with score, relevance, coherence, task_completion, feedback, and evaluation_tags. All numeric fields must be between 0 and 1. Do not make medical claims.
Instruction: {instruction}
Rubric: {expected}
Response: {response}"""
