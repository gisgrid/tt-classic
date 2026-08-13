from __future__ import annotations

from engine.session import LessonResult


SPEED_TARGETS = {
    ("letters", "Easy"): 38.0,
    ("letters", "Medium"): 48.0,
    ("words", "Easy"): 52.0,
    ("words", "Medium"): 57.0,
}


def calculate_score(result: LessonResult, mode: str, difficulty: str) -> int:
    target_wpm = SPEED_TARGETS[(mode, difficulty)]
    speed_points = min(result.wpm / target_wpm, 1.0) * 70
    accuracy_points = max(result.accuracy - 70.0, 0.0) / 30.0 * 30
    return round(min(speed_points + accuracy_points, 100.0))


def score_message(score: int) -> str:
    if score >= 90:
        return "Excellent!"
    if score >= 75:
        return "Great work!"
    if score >= 60:
        return "Passed!"
    if score >= 40:
        return "Good start!"
    return "Keep practicing!"
