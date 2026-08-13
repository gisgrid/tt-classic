# tt-classic

TT Classic is a small DOS-style typing tutor prototype for the terminal.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Controls

- `1`: home row practice
- `2`: choose Letter Practice: Easy (24 letters) or Medium (72 letters)
- `3`: choose Word Practice: Easy (8 words) or Medium (24 words)
- `4`: view the latest 10 Letter and Word history records
- `Backspace`: delete one typed character
- after a lesson ends, `Enter`: start the next lesson
- `Ctrl+R`: restart the current lesson
- `Ctrl+N`: load the next lesson in the current mode
- `Esc`: return to the main menu
- `Ctrl+Q`: quit

## Saved progress

Progress is stored locally in `data/progress.json`.

After completing a Letter or Word lesson, type a name and press `Enter` to save
the result. Select `4` from the main menu to view the latest 10 records per mode.

## Scores

Each Letter and Word lesson receives a score out of 100: up to 70 points for
speed and up to 30 points for accuracy. Easy and Medium each have separate Top
10 leaderboards. Medium has a slightly higher speed target, so a strong score
there represents more typing in the same time.
