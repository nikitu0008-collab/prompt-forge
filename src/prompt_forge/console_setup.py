"""Приведение консоли к UTF-8: на Windows без этого кириллица ломается (cp1252)."""

from __future__ import annotations

import sys


def setup_console_encoding() -> None:
    """Переключает консоль на UTF-8 и настраивает кодировку потоков."""
    if sys.platform.startswith("win"):
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception:  # pragma: no cover - зависит от окружения
            pass

    for stream, encoding in ((sys.stdout, "utf-8"), (sys.stderr, "utf-8"), (sys.stdin, "utf-8-sig")):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding=encoding, errors="replace")
        except Exception:  # pragma: no cover - поток может быть подменён тестом
            pass
