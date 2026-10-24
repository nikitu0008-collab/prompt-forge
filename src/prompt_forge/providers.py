"""Минимальный универсальный слой для AI-провайдеров без тяжёлых зависимостей."""
from __future__ import annotations
import json, os, urllib.error, urllib.request
from dataclasses import dataclass

class ProviderError(RuntimeError):
    """Понятная ошибка вызова AI-провайдера."""

@dataclass(frozen=True)
class ProviderConfig:
    provider: str = "openai-compatible"
    model: str = "gpt-4o-mini"
    api_key: str | None = None
    base_url: str | None = None
    timeout: float = 45.0

def enhance_prompt(prompt: str, config: ProviderConfig | None = None) -> str:
    """Улучшает промпт через OpenAI-compatible API или Ollama chat API.

    Настройки по умолчанию читаются из PROMPT_FORGE_PROVIDER,
    PROMPT_FORGE_MODEL, PROMPT_FORGE_API_KEY и PROMPT_FORGE_BASE_URL.
    """
    if config is None:
        cfg = ProviderConfig(
            provider=os.getenv("PROMPT_FORGE_PROVIDER", "openai-compatible"),
            model=os.getenv("PROMPT_FORGE_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("PROMPT_FORGE_API_KEY"),
            base_url=os.getenv("PROMPT_FORGE_BASE_URL"),
        )
    else:
        cfg = ProviderConfig(
            provider=config.provider or os.getenv("PROMPT_FORGE_PROVIDER", "openai-compatible"),
            model=config.model or os.getenv("PROMPT_FORGE_MODEL", "gpt-4o-mini"),
            api_key=config.api_key or os.getenv("PROMPT_FORGE_API_KEY"),
            base_url=config.base_url or os.getenv("PROMPT_FORGE_BASE_URL"),
            timeout=config.timeout,
        )
    provider = cfg.provider.lower().strip()
    if provider not in {"openai-compatible", "openai", "openrouter", "ollama"}:
        raise ProviderError(f"Неизвестный провайдер: {cfg.provider}")
    if provider == "ollama":
        url = (cfg.base_url or "http://localhost:11434").rstrip("/") + "/api/chat"
        payload = {"model": cfg.model or "llama3.2", "stream": False, "messages": [
            {"role": "system", "content": "Ты эксперт по prompt engineering. Улучши пользовательский промпт: сделай его конкретным, структурированным, проверяемым. Сохрани исходную цель и язык. Верни только улучшенный промпт."},
            {"role": "user", "content": prompt}
        ]}
    else:
        defaults = {"openai": "https://api.openai.com/v1", "openrouter": "https://openrouter.ai/api/v1", "openai-compatible": "https://api.openai.com/v1"}
        url = (cfg.base_url or defaults[provider]).rstrip("/") + "/chat/completions"
        payload = {"model": cfg.model or "gpt-4o-mini", "temperature": 0.2, "messages": [
            {"role": "system", "content": "You are an expert prompt engineer. Improve the user's prompt to be clear, specific, structured, and testable. Preserve the original intent and language. Return only the improved prompt."},
            {"role": "user", "content": prompt}
        ]}
    headers = {"Content-Type": "application/json", "User-Agent": "Prompt-Forge/0.2.0"}
    if provider != "ollama":
        if not cfg.api_key: raise ProviderError("Не задан API-ключ. Установите PROMPT_FORGE_API_KEY или используйте Ollama.")
        headers["Authorization"] = f"Bearer {cfg.api_key}"
    if provider == "openrouter": headers["HTTP-Referer"] = "https://github.com/nikitu0008-collab/prompt-forge"
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=cfg.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise ProviderError(f"AI API вернул HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ProviderError(f"Не удалось получить ответ от AI-провайдера: {exc}") from exc
    try:
        content = data["message"]["content"] if provider == "ollama" else data["choices"][0]["message"]["content"]
        result = str(content).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("AI-провайдер вернул ответ в неожиданном формате") from exc
    if not result: raise ProviderError("AI-провайдер вернул пустой промпт")
    return result + ("\n" if not result.endswith("\n") else "")
