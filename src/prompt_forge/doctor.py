"""Диагностика окружения Prompt Forge."""
from __future__ import annotations
import os, shutil, sys
from dataclasses import dataclass

@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str

def run_checks() -> list[Check]:
    checks = [Check("Python", sys.version_info >= (3, 10), sys.version.split()[0]),
              Check("UTF-8 stdout", "utf" in (getattr(sys.stdout, "encoding", "") or "").lower(), str(getattr(sys.stdout, "encoding", None))),
              Check("PATH: python", shutil.which("python") is not None, shutil.which("python") or "не найден"),
              Check("Буфер обмена", _clipboard_available(), "доступен" if _clipboard_available() else "инструмент не найден; копирование может зависеть от окружения"),
              Check("API-ключ (необязательно)", bool(os.getenv("PROMPT_FORGE_API_KEY")) or os.getenv("PROMPT_FORGE_PROVIDER", "openai-compatible") == "ollama", "настроен" if (os.getenv("PROMPT_FORGE_API_KEY") or os.getenv("PROMPT_FORGE_PROVIDER") == "ollama") else "не настроен (нужен только для облачного --enhance)")]
    return checks

def _clipboard_available() -> bool:
    if sys.platform.startswith("win"): return shutil.which("clip") is not None
    if sys.platform == "darwin": return shutil.which("pbcopy") is not None
    return shutil.which("xclip") is not None or shutil.which("xsel") is not None or bool(os.getenv("WAYLAND_DISPLAY"))
