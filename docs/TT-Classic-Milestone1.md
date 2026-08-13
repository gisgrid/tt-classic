# TT Classic - Milestone 1 Specification

## Objective

This project is **NOT** intended to fully recreate the original DOS TT
Typing Tutor in the first iteration.

The goal of **Milestone 1** is to build a small, clean, working
prototype that captures the core typing experience while keeping the
implementation simple enough for an AI coding agent to complete in 1--2
days.

------------------------------------------------------------------------

# Scope

Only implement the following features.

## 1. DOS-style UI

-   Black background
-   Green text
-   Keyboard-only interaction
-   Fast terminal interface
-   No mouse support required

Suggested libraries:

-   textual
-   rich

------------------------------------------------------------------------

## 2. Practice Modes

### Home Row

Examples:

    asdf jkl;
    fjdk
    aksl

### Letter Practice

Random letters with configurable length.

### Word Practice

Use approximately 200 common English words.

No sentence practice.

No articles.

No games.

------------------------------------------------------------------------

## 3. Typing Engine

Required:

-   highlight current character
-   instant correctness feedback
-   optional Backspace
-   restart current lesson
-   next lesson

No animations.

No sound effects.

------------------------------------------------------------------------

## 4. Statistics

Display after each lesson:

-   WPM
-   Accuracy
-   Total keystrokes
-   Errors
-   Time spent

------------------------------------------------------------------------

## 5. Local Progress

Save locally as JSON.

Store:

-   Best WPM
-   Average WPM
-   Average Accuracy
-   Total Practice Time
-   Lessons Completed

No cloud sync.

No login.

------------------------------------------------------------------------

## 6. Project Structure

    tt-classic/
    │
    ├── app.py
    ├── requirements.txt
    ├── README.md
    │
    ├── ui/
    ├── engine/
    ├── storage/
    ├── content/
    │   └── words/
    └── data/

------------------------------------------------------------------------

# Out of Scope

Do NOT implement these features in Milestone 1:

-   English articles
-   Sentence practice
-   Parent dashboard
-   Multiple users
-   AI-generated content
-   Online features
-   Themes
-   Finger diagrams
-   Typing games
-   Sound effects
-   Plugin system

------------------------------------------------------------------------

# Development Principles

-   Keep the architecture simple.
-   Prefer readable code over clever code.
-   Avoid overengineering.
-   Minimize dependencies.
-   Build a stable MVP first.

Estimated implementation size:

-   Approximately **1,000--2,000 lines of Python code**.

The application should be fully usable after Milestone 1, even if many
advanced features are postponed to later milestones.
