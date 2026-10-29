"""Tests for AI provider request/response handling."""
import io
import json
import urllib.error
import urllib.request

import pytest

from prompt_forge.providers import ProviderConfig, ProviderError, enhance_prompt


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_unknown_provider_is_rejected():
    with pytest.raises(ProviderError, match="Неизвестный провайдер"):
        enhance_prompt("hello", ProviderConfig(provider="not-a-provider"))


def test_openai_compatible_requires_api_key(monkeypatch):
    monkeypatch.delenv("PROMPT_FORGE_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="API-ключ"):
        enhance_prompt("hello", ProviderConfig(provider="openai-compatible", api_key=None))


def test_openai_compatible_parses_response(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse({"choices": [{"message": {"content": "Improved prompt"}}]}))
    result = enhance_prompt("hello", ProviderConfig(api_key="secret", base_url="https://example.test/v1"))
    assert result == "Improved prompt\n"


def test_openai_response_preserves_trailing_newline(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse({"choices": [{"message": {"content": "Improved\n"}}]}))
    assert enhance_prompt("hello", ProviderConfig(provider="openai", api_key="secret")) == "Improved\n"


def test_ollama_uses_chat_endpoint_and_no_api_key(monkeypatch):
    calls = {}
    def fake_urlopen(request, timeout):
        calls["url"] = request.full_url
        calls["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"message": {"content": "Улучшенный промпт"}})
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    result = enhance_prompt("Привет", ProviderConfig(provider="ollama", model="llama3", base_url="http://localhost:11434"))
    assert result == "Улучшенный промпт\n"
    assert calls["url"] == "http://localhost:11434/api/chat"
    assert calls["body"]["model"] == "llama3"


def test_openrouter_adds_referer(monkeypatch):
    calls = {}
    def fake_urlopen(request, timeout):
        calls["referer"] = request.get_header("Http-referer")
        return FakeResponse({"choices": [{"message": {"content": "result"}}]})
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    enhance_prompt("hello", ProviderConfig(provider="openrouter", api_key="secret"))
    assert calls["referer"] == "https://github.com/nikitu0008-collab/prompt-forge"


def test_http_error_becomes_provider_error(monkeypatch):
    error = urllib.error.HTTPError("https://example.test", 401, "Unauthorized", {}, io.BytesIO(b"Unauthorized"))
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(error))
    with pytest.raises(ProviderError, match="HTTP 401"):
        enhance_prompt("hello", ProviderConfig(api_key="secret"))


def test_url_error_becomes_provider_error(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(urllib.error.URLError("offline")))
    with pytest.raises(ProviderError, match="Не удалось получить ответ"):
        enhance_prompt("hello", ProviderConfig(provider="ollama"))


def test_invalid_json_becomes_provider_error(monkeypatch):
    class BadJson(FakeResponse):
        def read(self):
            return b"not json"
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: BadJson(None))
    with pytest.raises(ProviderError, match="Не удалось получить ответ"):
        enhance_prompt("hello", ProviderConfig(provider="ollama"))


def test_unexpected_response_shape_becomes_provider_error(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse({"choices": []}))
    with pytest.raises(ProviderError, match="неожиданном формате"):
        enhance_prompt("hello", ProviderConfig(api_key="secret"))


def test_empty_response_becomes_provider_error(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse({"choices": [{"message": {"content": "  "}}]}))
    with pytest.raises(ProviderError, match="пустой промпт"):
        enhance_prompt("hello", ProviderConfig(api_key="secret"))
