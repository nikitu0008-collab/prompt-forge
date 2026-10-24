import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from prompt_forge.cli import app
from prompt_forge.models import Detail, Profile, PromptSpec, OutputFormat
from prompt_forge.output import render
from prompt_forge.providers import ProviderConfig, ProviderError, enhance_prompt
from prompt_forge.templates import delete_template, list_templates, load_template, save_template

runner = CliRunner()

def test_yaml_render_has_prompt_key():
    spec = PromptSpec(task="Проверка YAML", profile=Profile.CODE)
    rendered = render(spec, OutputFormat.YAML)
    assert "prompt:" in rendered
    assert "Проверка YAML" in rendered

def test_template_round_trip(tmp_path: Path):
    spec = PromptSpec(task="Сохранённая задача", profile=Profile.BUGFIX, detail=Detail.DETAILED, requirements=["Тесты"])
    save_template("my-template", spec, tmp_path)
    loaded = load_template("my-template", tmp_path)
    assert loaded.task == spec.task
    assert loaded.profile == Profile.BUGFIX
    assert loaded.detail == Detail.DETAILED
    assert loaded.requirements == ["Тесты"]
    assert list_templates(tmp_path)[0]["name"] == "my-template"
    assert delete_template("my-template", tmp_path) is True
    assert delete_template("my-template", tmp_path) is False

def test_cli_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "диагностика" in result.output.lower()

def test_cli_yaml_export():
    result = runner.invoke(app, ["build", "--task", "YAML задача", "--format", "yaml", "--no-copy"])
    assert result.exit_code == 0
    assert "prompt:" in result.output

def test_enhance_requires_api_key(monkeypatch):
    monkeypatch.delenv("PROMPT_FORGE_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="API-ключ"):
        enhance_prompt("Test", ProviderConfig(provider="openai-compatible", model="test"))

def test_cli_enhance_without_key_fails_cleanly(monkeypatch):
    monkeypatch.delenv("PROMPT_FORGE_API_KEY", raising=False)
    result = runner.invoke(app, ["build", "--task", "test", "--enhance", "--no-copy"])
    assert result.exit_code == 2
    assert "API-ключ" in result.output

def test_web_api_health_and_build(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    import prompt_forge.web as web_module
    from prompt_forge.web import app as web_app
    original_save, original_load = web_module.save_template, web_module.load_template
    monkeypatch.setattr(web_module, "save_template", lambda name, spec: original_save(name, spec, tmp_path))
    monkeypatch.setattr(web_module, "load_template", lambda name: original_load(name, tmp_path))
    client = TestClient(web_app)
    assert client.get("/api/health").json()["version"] == "0.2.0"
    response = client.post("/api/build", json={"task":"Сделать API", "profile":"code", "detail":"standard"})
    assert response.status_code == 200
    assert "Сделать API" in response.json()["prompt"]
    yaml_response = client.post("/api/export/yaml", json={"task":"YAML API", "profile":"code", "detail":"standard"})
    assert yaml_response.status_code == 200
    assert "prompt:" in yaml_response.json()["content"]
    saved = client.post("/api/templates", json={"name":"api-test", "task":"Template API", "profile":"code", "detail":"standard"})
    assert saved.status_code == 200
    loaded = client.get("/api/templates/api-test")
    assert loaded.status_code == 200 and loaded.json()["task"] == "Template API"


def test_cli_saves_selected_format(tmp_path):
    target = tmp_path / "prompt.yaml"
    result = runner.invoke(app, ["build", "--task", "Файл YAML", "--format", "yaml", "--save", str(target), "--no-copy"])
    assert result.exit_code == 0
    assert target.read_text(encoding="utf-8").startswith("prompt:")
