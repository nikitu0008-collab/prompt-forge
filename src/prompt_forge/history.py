"""Локальная история сгенерированных промптов."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_HISTORY_LIMIT = 50


def history_path() -> Path:
    """Возвращает путь к файлу истории."""
    import os

    if os.name == "nt":
        root = Path.home() / "AppData" / "Roaming" / "prompt-forge"
    else:
        root = Path.home() / ".config" / "prompt-forge"

    return root / "history.json"


def load_history(path: Path | None = None) -> list[dict[str, Any]]:
    """Загружает историю генераций."""
    target = Path(path) if path else history_path()

    if not target.exists():
        return []

    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    return data if isinstance(data, list) else []


def add_history_entry(
    task: str,
    prompt: str,
    profile: str,
    path: Path | None = None,
    limit: int = DEFAULT_HISTORY_LIMIT,
) -> dict[str, Any]:
    """Добавляет новую запись в историю."""
    target = Path(path) if path else history_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    history = load_history(target)

    entry = {
        "task": task,
        "prompt": prompt,
        "profile": profile,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    history.append(entry)

    if limit > 0:
        history = history[-limit:]

    target.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return entry


def clear_history(path: Path | None = None) -> bool:
    """Удаляет всю историю генераций."""
    target = Path(path) if path else history_path()

    if not target.exists():
        return False

    target.unlink()
    return True
