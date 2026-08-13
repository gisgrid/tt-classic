from __future__ import annotations

import random
from pathlib import Path


HOME_ROW_LESSONS = [
    "asdf jkl;",
    "fjdk as;l",
    "asdfg hjkl;",
    "a sad flask",
    "fall ask; dad",
    "jkl; fdsa",
    "lad; fad; salsa",
    "all falls; glass",
]

LETTER_ALPHABET = "abcdefghijklmnopqrstuvwxyz"


class LessonFactory:
    def __init__(self, words_path: Path) -> None:
        self._random = random.Random()
        self._words = self._load_words(words_path)

    @staticmethod
    def _load_words(words_path: Path) -> list[str]:
        return [
            line.strip()
            for line in words_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def create_home_row(self) -> str:
        return self._random.choice(HOME_ROW_LESSONS)

    def create_letters(self, length: int) -> str:
        chars = [self._random.choice(LETTER_ALPHABET) for _ in range(max(8, length))]
        grouped = ["".join(chars[index:index + 4]) for index in range(0, len(chars), 4)]
        return " ".join(grouped)

    def create_words(self, word_count: int) -> str:
        count = max(4, word_count)
        return " ".join(self._random.choice(self._words) for _ in range(count))
