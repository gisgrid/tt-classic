from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from engine.session import LessonResult
from engine.scoring import calculate_score


@dataclass
class Progress:
    best_wpm: float = 0.0
    average_wpm: float = 0.0
    average_accuracy: float = 0.0
    total_practice_time: float = 0.0
    lessons_completed: int = 0
    letter_history: list[dict[str, str | float | int]] | None = None
    word_history: list[dict[str, str | float | int]] | None = None
    letter_easy_history: list[dict[str, str | float | int]] | None = None
    letter_medium_history: list[dict[str, str | float | int]] | None = None
    word_easy_history: list[dict[str, str | float | int]] | None = None
    word_medium_history: list[dict[str, str | float | int]] | None = None

    def __post_init__(self) -> None:
        if self.letter_history is None:
            self.letter_history = []
        if self.word_history is None:
            self.word_history = []
        if self.letter_easy_history is None:
            self.letter_easy_history = self._migrate_history(self.letter_history, "letters")
        if self.letter_medium_history is None:
            self.letter_medium_history = []
        if self.word_easy_history is None:
            self.word_easy_history = self._migrate_history(self.word_history, "words")
        if self.word_medium_history is None:
            self.word_medium_history = []

    @staticmethod
    def _migrate_history(
        history: list[dict[str, str | float | int]], mode: str
    ) -> list[dict[str, str | float | int]]:
        migrated = []
        for record in history:
            item = dict(record)
            item["difficulty"] = "Easy"
            target_wpm = 60 if mode == "letters" else 70
            item["score"] = round(
                min(float(item["wpm"]) / target_wpm, 1.0) * 70
                + max(float(item["accuracy"]) - 70, 0) / 30 * 30
            )
            migrated.append(item)
        return sorted(migrated, key=lambda item: int(item["score"]), reverse=True)[:10]


class ProgressStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Progress:
        if not self.path.exists():
            return Progress()

        data = json.loads(self.path.read_text(encoding="utf-8"))
        progress = Progress(**data)
        if self._refresh_scores(progress):
            self.path.write_text(json.dumps(asdict(progress), indent=2), encoding="utf-8")
        return progress

    @staticmethod
    def _refresh_scores(progress: Progress) -> bool:
        changed = False
        for mode in ("letters", "words"):
            for difficulty in ("Easy", "Medium"):
                history = getattr(progress, f"{mode[:-1]}_{difficulty.lower()}_history")
                if history is None:
                    continue
                for record in history:
                    result = LessonResult(
                        wpm=float(record["wpm"]),
                        accuracy=float(record["accuracy"]),
                        total_keystrokes=0,
                        errors=int(record["errors"]),
                        time_spent=0.0,
                    )
                    score = calculate_score(result, mode, difficulty)
                    if record.get("score") != score:
                        record["score"] = score
                        changed = True
                history.sort(key=lambda item: int(item["score"]), reverse=True)
        return changed

    def save_result(
        self,
        result: LessonResult,
        mode: str | None,
        player_name: str,
        difficulty: str = "Easy",
    ) -> Progress:
        progress = self.load()
        previous_count = progress.lessons_completed
        new_count = previous_count + 1

        progress.best_wpm = max(progress.best_wpm, result.wpm)
        progress.average_wpm = self._roll_average(progress.average_wpm, previous_count, result.wpm)
        progress.average_accuracy = self._roll_average(
            progress.average_accuracy,
            previous_count,
            result.accuracy,
        )
        progress.total_practice_time += result.time_spent
        progress.lessons_completed = new_count
        if mode in {"letters", "words"}:
            self._add_history_record(progress, result, mode, player_name, difficulty)

        self.path.write_text(json.dumps(asdict(progress), indent=2), encoding="utf-8")
        return progress

    @staticmethod
    def _add_history_record(
        progress: Progress,
        result: LessonResult,
        mode: str,
        player_name: str,
        difficulty: str,
    ) -> None:
        history = getattr(progress, f"{mode[:-1]}_{difficulty.lower()}_history")
        if history is None:
            return

        history.append(
            {
                "name": player_name or "Player",
                "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "wpm": round(result.wpm, 1),
                "accuracy": round(result.accuracy, 1),
                "errors": result.errors,
                "difficulty": difficulty,
                "score": calculate_score(result, mode, difficulty),
            }
        )
        history.sort(key=lambda item: int(item["score"]), reverse=True)
        del history[10:]

    @staticmethod
    def _roll_average(current_average: float, count: int, new_value: float) -> float:
        if count <= 0:
            return new_value
        return ((current_average * count) + new_value) / (count + 1)
