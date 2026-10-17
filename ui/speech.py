from __future__ import annotations

from queue import Queue
from threading import Thread


class SpeechService:
    def __init__(self) -> None:
        self._words: Queue[str | None] = Queue()
        self._worker = Thread(target=self._speak_words, daemon=True)
        self._worker.start()

    def say(self, word: str) -> None:
        self._words.put(word)

    def close(self) -> None:
        self._words.put(None)

    def _speak_words(self) -> None:
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        try:
            voice = win32com.client.Dispatch("SAPI.SpVoice")
            while (word := self._words.get()) is not None:
                voice.Speak(word)
            del voice
        finally:
            pythoncom.CoUninitialize()
