"""Tests for Prompt Forge generation history."""

import json

from prompt_forge.history import (
    add_history_entry,
    clear_history,
    load_history,
)


def test_load_history_returns_empty_for_missing_file(tmp_path):
    path = tmp_path / "history.json"

    assert load_history(path) == []


def test_add_history_entry_creates_file(tmp_path):
    path = tmp_path / "history.json"

    entry = add_history_entry(
        task="Create an API",
        prompt="Generated prompt",
        profile="code",
        path=path,
    )

    assert path.exists()
    assert entry["task"] == "Create an API"
    assert entry["profile"] == "code"
    assert "created_at" in entry


def test_history_entries_are_saved(tmp_path):
    path = tmp_path / "history.json"

    add_history_entry("First task", "First prompt", "code", path)
    add_history_entry("Second task", "Second prompt", "bugfix", path)

    history = load_history(path)

    assert len(history) == 2
    assert history[0]["task"] == "First task"
    assert history[1]["task"] == "Second task"


def test_history_respects_limit(tmp_path):
    path = tmp_path / "history.json"

    for index in range(5):
        add_history_entry(
            f"Task {index}",
            f"Prompt {index}",
            "code",
            path,
            limit=3,
        )

    history = load_history(path)

    assert len(history) == 3
    assert history[0]["task"] == "Task 2"
    assert history[-1]["task"] == "Task 4"


def test_load_history_handles_invalid_json(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("{invalid json", encoding="utf-8")

    assert load_history(path) == []


def test_clear_history_removes_existing_file(tmp_path):
    path = tmp_path / "history.json"
    path.write_text(json.dumps([]), encoding="utf-8")

    assert clear_history(path) is True
    assert not path.exists()


def test_clear_history_returns_false_for_missing_file(tmp_path):
    path = tmp_path / "history.json"

    assert clear_history(path) is False
