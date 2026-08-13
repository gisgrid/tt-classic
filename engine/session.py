from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter


@dataclass
class LessonResult:
    wpm: float
    accuracy: float
    total_keystrokes: int
    errors: int
    time_spent: float


class TypingSession:
    def __init__(self, target_text: str) -> None:
        self.target_text = target_text
        self.typed = ""
        self.total_keystrokes = 0
        self.errors = 0
        self.started_at = perf_counter()
        self.completed_at: float | None = None

    @property
    def is_complete(self) -> bool:
        return self.typed == self.target_text

    @property
    def current_index(self) -> int:
        return len(self.typed)

    def process_key(self, key: str) -> bool:
        if self.is_complete:
            return False

        if key == "backspace":
            if self.typed:
                self.typed = self.typed[:-1]
                self.total_keystrokes += 1
            return False

        if len(key) != 1:
            return False

        expected = self.target_text[self.current_index]
        self.total_keystrokes += 1
        if key != expected:
            self.errors += 1
            return False

        self.typed += key
        if self.is_complete:
            self.completed_at = perf_counter()
        return True

    def build_result(self) -> LessonResult:
        finished_at = self.completed_at or perf_counter()
        elapsed = max(finished_at - self.started_at, 0.001)
        correct_keystrokes = len(self.typed)
        wpm = (correct_keystrokes / 5) / (elapsed / 60)
        accuracy = 100.0
        if self.total_keystrokes:
            accuracy = (correct_keystrokes / self.total_keystrokes) * 100

        return LessonResult(
            wpm=wpm,
            accuracy=accuracy,
            total_keystrokes=self.total_keystrokes,
            errors=self.errors,
            time_spent=elapsed,
        )
