"""Вывод результата: терминал, буфер обмена, файл."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from prompt_forge.builder import build_bundle
from prompt_forge.models import OutputFormat, PromptSpec


def copy_to_clipboard(text: str) -> bool:
    """Копирует текст в буфер обмена. Возвращает True при успехе."""
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except Exception:
        pass

    try:
        if sys.platform.startswith("win"):
            command = ["clip"]
        elif sys.platform == "darwin":
            command = ["pbcopy"]
        else:
            command = ["xclip", "-selection", "clipboard"]
        if not shutil.which(command[0]):
            return False
        subprocess.run(command, input=text.encode("utf-8"), check=True)
        return True
    except Exception:
        return False


def save_to_file(path: Path, text: str) -> Path:
    """Сохраняет текст в файл в UTF-8, создавая недостающие каталоги."""
    path = Path(path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def render(spec: PromptSpec, fmt: OutputFormat) -> str:
    """Готовит итоговый текст в нужном формате."""
    bundle = build_bundle(spec)
    if fmt == OutputFormat.JSON:
        return json.dumps(bundle, ensure_ascii=False, indent=2)
    if fmt == OutputFormat.PLAIN:
        return bundle["plain"]
    return bundle["prompt"]
