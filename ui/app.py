from __future__ import annotations

from pathlib import Path

from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.widgets import Footer, Header, Static

from engine.lessons import LessonFactory
from engine.scoring import calculate_score, score_message
from engine.session import LessonResult, TypingSession
from storage.progress import Progress, ProgressStore


class TTClassicApp(App[None]):
    CSS = """
    Screen {
        background: black;
        color: #00ff66;
    }

    #layout {
        height: 1fr;
        padding: 1 2;
    }

    #body {
        height: 1fr;
        border: round #00aa44;
        padding: 1 2;
    }

    #status {
        height: auto;
        border: round #007722;
        padding: 1 2;
        margin-top: 1;
    }

    #progress {
        width: 40%;
        border: round #007722;
        padding: 1 2;
    }

    #lesson {
        width: 1fr;
        border: round #007722;
        padding: 1 2;
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("1", "choose_one", "Choice 1"),
        ("2", "choose_two", "Choice 2"),
        ("3", "choose_three", "Choice 3"),
        ("4", "choose_four", "History"),
        ("ctrl+r", "restart_lesson", "Restart"),
        ("ctrl+n", "next_lesson", "Next"),
        ("escape", "show_menu", "Menu"),
        ("plus", "increase_length", "Longer"),
        ("minus", "decrease_length", "Shorter"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        root = Path(__file__).resolve().parent.parent
        self.lesson_factory = LessonFactory(root / "content" / "words" / "common_words.txt")
        self.progress_store = ProgressStore(root / "data" / "progress.json")
        self.progress = self.progress_store.load()
        self.mode = "menu"
        self.length = 24
        self.word_count = 8
        self.difficulty = "Easy"
        self.session: TypingSession | None = None
        self.last_result: LessonResult | None = None
        self.feedback_message = "Ready."
        self.name_entry = ""
        self.history_view: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="layout"):
            with Horizontal(id="body"):
                yield Static(id="lesson")
                yield Static(id="progress")
            yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "TT Classic"
        self.sub_title = "Milestone 1"
        self._refresh_all()

    def action_choose_one(self) -> None:
        if self.mode == "menu":
            self._start_practice("home", 0, "Home Row")
        elif self.mode == "letter_difficulty":
            self._start_practice("letters", 24, "Easy")
        elif self.mode == "word_difficulty":
            self._start_practice("words", 8, "Easy")
        elif self.mode == "history":
            self.history_view = "letter_easy"
            self._refresh_all()

    def action_choose_two(self) -> None:
        if self.mode == "menu":
            self.mode = "letter_difficulty"
            self.feedback_message = "Choose Letter Practice difficulty."
            self._refresh_all()
        elif self.mode == "letter_difficulty":
            self._start_practice("letters", 72, "Medium")
        elif self.mode == "word_difficulty":
            self._start_practice("words", 24, "Medium")
        elif self.mode == "history":
            self.history_view = "letter_medium"
            self._refresh_all()

    def action_choose_three(self) -> None:
        if self.mode == "menu":
            self.mode = "word_difficulty"
            self.feedback_message = "Choose Word Practice difficulty."
            self._refresh_all()
        elif self.mode == "history":
            self.history_view = "word_easy"
            self._refresh_all()

    def action_choose_four(self) -> None:
        if self.mode == "menu":
            self.mode = "history"
            self.session = None
            self.last_result = None
            self.name_entry = ""
            self.history_view = None
            self.feedback_message = "Choose a leaderboard."
            self._refresh_all()
        elif self.mode == "history":
            self.history_view = "word_medium"
            self._refresh_all()

    def _start_practice(self, mode: str, size: int, difficulty: str) -> None:
        if mode == "home":
            text = self.lesson_factory.create_home_row()
        elif mode == "letters":
            self.length = size
            text = self.lesson_factory.create_letters(size)
        else:
            self.word_count = size
            text = self.lesson_factory.create_words(size)

        self.mode = mode
        self.difficulty = difficulty
        self.last_result = None
        self.session = TypingSession(text)
        self.feedback_message = "Lesson started."
        self.name_entry = ""
        self.history_view = None
        self._refresh_all()

    def action_restart_lesson(self) -> None:
        if self.session is None:
            return
        self.session = TypingSession(self.session.target_text)
        self.last_result = None
        self.feedback_message = "Lesson restarted."
        self.name_entry = ""
        self.history_view = None
        self._refresh_all()

    def action_next_lesson(self) -> None:
        if self.mode not in {"home", "letters", "words"}:
            return
        if self.mode == "home":
            self._start_practice("home", 0, "Home Row")
        elif self.mode == "letters":
            self._start_practice("letters", self.length, self.difficulty)
        else:
            self._start_practice("words", self.word_count, self.difficulty)

    def action_show_menu(self) -> None:
        self.mode = "menu"
        self.session = None
        self.last_result = None
        self.feedback_message = "Back at menu."
        self.name_entry = ""
        self.history_view = None
        self._refresh_all()

    def action_increase_length(self) -> None:
        return

    def action_decrease_length(self) -> None:
        return

    def on_key(self, event: events.Key) -> None:
        if self.session is None or self.mode in {"menu", "letter_difficulty", "word_difficulty", "history"}:
            return

        key = event.character if event.is_printable and event.character else event.key
        if key == "space":
            key = " "

        if self.session.is_complete:
            if self.mode in {"letters", "words"} and key == "enter":
                self._save_named_result()
            elif self.mode == "home" and key == "enter":
                self.action_next_lesson()
            elif key == "escape":
                self.action_show_menu()
            elif key == "backspace":
                if self.mode in {"letters", "words"} and self.name_entry:
                    self.name_entry = self.name_entry[:-1]
                    self._refresh_all()
                else:
                    self.action_restart_lesson()
            elif self.mode in {"letters", "words"} and len(key) == 1:
                if len(self.name_entry) < 16 and (key.isalnum() or key in " -_"):
                    self.name_entry += key
                    self._refresh_all()
            else:
                self.feedback_message = "Lesson already complete. Enter a name, then press Enter."
                self._refresh_all()
            return

        before = self.session.is_complete
        handled = self.session.process_key(key)
        if key == "backspace":
            self.feedback_message = "Deleted last character."
        elif handled:
            self.feedback_message = "Correct."
        elif len(key) == 1:
            expected = self.session.target_text[self.session.current_index]
            self.feedback_message = f"Incorrect: expected {expected!r}."

        if handled or key == "backspace" or len(key) == 1:
            self._refresh_all()

        if not before and self.session.is_complete:
            self.last_result = self.session.build_result()
            if self.mode == "home":
                self.progress = self.progress_store.save_result(self.last_result, None, "Player")
                self.feedback_message = "Lesson complete. Progress saved."
            else:
                self.feedback_message = "Lesson complete. Enter your name, then press Enter to save."
            self._refresh_all()

    def _save_named_result(self) -> None:
        if self.last_result is None:
            return
        self.progress = self.progress_store.save_result(
            self.last_result,
            self.mode,
            self.name_entry.strip() or "Player",
            self.difficulty,
        )
        self.feedback_message = "Record saved. Starting next lesson."
        self.action_next_lesson()

    def _refresh_all(self) -> None:
        try:
            self.query_one("#lesson", Static).update(self._render_lesson())
            self.query_one("#progress", Static).update(self._render_progress())
            self.query_one("#status", Static).update(self._render_status())
        except NoMatches:
            return

    def _render_lesson(self) -> Text:
        if self.mode == "menu":
            text = Text()
            text.append("TT Classic\n\n", style="bold #00ff66")
            text.append("1  Home Row\n")
            text.append("2  Letter Practice\n")
            text.append("3  Word Practice\n")
            text.append("4  History Records\n\n")
            text.append("Letter and Word practice each offer Easy and Medium levels.\n")
            text.append("Use keyboard only. Press Ctrl+Q to quit.")
            return text

        if self.mode == "letter_difficulty":
            return Text(
                "Letter Practice\n\n"
                "1  Easy   24 letters\n"
                "2  Medium 72 letters\n\n"
                "Press Esc to return to the main menu."
            )

        if self.mode == "word_difficulty":
            return Text(
                "Word Practice\n\n"
                "1  Easy   8 words\n"
                "2  Medium 24 words\n\n"
                "Press Esc to return to the main menu."
            )

        if self.mode == "history":
            text = Text()
            text.append("History Records\n\n", style="bold #00ff66")
            if self.history_view is None:
                text.append("1  Letter Easy - Top 10\n")
                text.append("2  Letter Medium - Top 10\n")
                text.append("3  Word Easy - Top 10\n")
                text.append("4  Word Medium - Top 10\n\n")
                text.append("Press a number to open a leaderboard. Press Esc for menu.")
                return text

            history = getattr(self.progress, f"{self.history_view}_history")
            title = self.history_view.replace("_", " ").title()
            text.append(f"{title} - Top 10\n\n", style="bold #00ff66")
            text.append(self._format_history(history))
            text.append("\n\nPress 1-4 for another board. Press Esc for menu.")
            return text

        assert self.session is not None
        prompt = Text()
        prompt.append(f"Mode: {self.mode} - {self.difficulty}\n\n", style="bold #00ff66")
        prompt.append(self._build_target_text())
        prompt.append("\n\n")
        prompt.append(f"Typed: {self.session.typed or '_'}")
        if self.session.is_complete and self.last_result is not None:
            prompt.append("\n\nLesson complete.", style="bold #00ff66")
            if self.mode in {"letters", "words"}:
                score = calculate_score(self.last_result, self.mode, self.difficulty)
                prompt.append(f"\nScore: {score}/100 - {score_message(score)}", style="bold #00ff66")
                prompt.append("\nName: ")
                prompt.append(self.name_entry or "_", style="black on #00ff66")
                prompt.append("\nType your name, then press Enter to save and continue.")
            else:
                prompt.append("\nPress Enter for next lesson or Esc for menu.")
        return prompt

    def _build_target_text(self) -> Text:
        assert self.session is not None
        text = Text()
        for index, char in enumerate(self.session.target_text):
            if index < self.session.current_index:
                text.append(char, style="#00ff66")
            elif index == self.session.current_index and not self.session.is_complete:
                text.append(char, style="black on #00ff66")
            else:
                text.append(char, style="#007722")
        return text

    def _render_progress(self) -> Text:
        text = Text()
        text.append("Progress\n\n", style="bold #00ff66")
        text.append(self._format_progress(self.progress))
        if self.last_result is not None:
            text.append("\n\nLast Lesson\n\n", style="bold #00ff66")
            text.append(self._format_result(self.last_result))
        return text

    def _render_status(self) -> Text:
        if self.mode == "menu":
            return Text("Pick a mode with 1, 2, 3, or view records with 4.")
        if self.mode in {"letter_difficulty", "word_difficulty"}:
            return Text("Press 1 for Easy, 2 for Medium, or Esc to return.")
        if self.mode == "history":
            return Text("Choose a leaderboard with 1-4. Press Esc to return.")

        assert self.session is not None
        if self.session.is_complete:
            if self.mode in {"letters", "words"}:
                status = Text("Lesson done | type name | Enter save + next | Backspace edit | Esc menu")
            else:
                status = Text("Lesson done | Enter next lesson | Backspace restart | Esc menu")
        else:
            status = Text(
                "Keys: type text | backspace | Ctrl+R restart | Ctrl+N next | Esc menu"
            )
        status.append(
            f" | typed {self.session.current_index}/{len(self.session.target_text)} | errors {self.session.errors}"
        )
        status.append(f" | {self.feedback_message}")
        if self.last_result is not None:
            status.append(" | lesson saved", style="bold #00ff66")
        return status

    @staticmethod
    def _format_result(result: LessonResult) -> str:
        return (
            f"WPM: {result.wpm:.1f}\n"
            f"Accuracy: {result.accuracy:.1f}%\n"
            f"Keystrokes: {result.total_keystrokes}\n"
            f"Errors: {result.errors}\n"
            f"Time: {result.time_spent:.1f}s"
        )

    @staticmethod
    def _format_progress(progress: Progress) -> str:
        return (
            f"Best WPM: {progress.best_wpm:.1f}\n"
            f"Average WPM: {progress.average_wpm:.1f}\n"
            f"Average Accuracy: {progress.average_accuracy:.1f}%\n"
            f"Total Practice Time: {progress.total_practice_time:.1f}s\n"
            f"Lessons Completed: {progress.lessons_completed}"
        )

    @staticmethod
    def _format_history(history: list[dict[str, str | float | int]] | None) -> str:
        if not history:
            return "No records yet."

        lines = []
        for record in history:
            name = str(record["name"])
            wpm = float(record["wpm"])
            accuracy = float(record["accuracy"])
            completed_at = str(record["completed_at"])
            score = int(record.get("score", 0))
            lines.append(
                f"{name[:10]:10} {score:>3}/100 {wpm:>5.1f} WPM {accuracy:>5.1f}%\n"
                f"  {completed_at}"
            )
        return "\n".join(lines)
