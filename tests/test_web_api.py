"""HTTP-level tests for the optional FastAPI application."""
import pytest
from fastapi.testclient import TestClient

import prompt_forge.web as web_module
from prompt_forge.web import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    original_save = web_module.save_template
    original_load = web_module.load_template
    original_list = web_module.list_templates
    monkeypatch.setattr(web_module, "save_template", lambda name, spec: original_save(name, spec, tmp_path))
    monkeypatch.setattr(web_module, "load_template", lambda name: original_load(name, tmp_path))
    monkeypatch.setattr(web_module, "list_templates", lambda: original_list(tmp_path))
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_profiles_endpoint_returns_profiles(client):
    response = client.get("/api/profiles")
    assert response.status_code == 200
    assert any(item["key"] == "code" for item in response.json())


def test_build_endpoint_returns_prompt(client):
    response = client.post("/api/build", json={"task": "Сделать API"})
    assert response.status_code == 200
    assert "Сделать API" in response.json()["prompt"]


def test_build_endpoint_rejects_empty_task(client):
    response = client.post("/api/build", json={"task": "   "})
    assert response.status_code == 422


def test_build_endpoint_rejects_missing_task(client):
    assert client.post("/api/build", json={}).status_code == 422


def test_build_endpoint_rejects_oversized_task(client):
    assert client.post("/api/build", json={"task": "x" * 20001}).status_code == 422


@pytest.mark.parametrize("fmt", ["md", "plain", "json", "yaml"])
def test_export_endpoint_supports_formats(client, fmt):
    response = client.post(f"/api/export/{fmt}", json={"task": "Export test"})
    assert response.status_code == 200
    assert response.json()["format"] == fmt
    assert response.json()["content"]


def test_export_endpoint_rejects_unknown_format(client):
    response = client.post("/api/export/xml", json={"task": "test"})
    assert response.status_code == 400


def test_create_and_get_template(client):
    created = client.post("/api/templates", json={"name": "api-template", "task": "Template task"})
    assert created.status_code == 200
    loaded = client.get("/api/templates/api-template")
    assert loaded.status_code == 200
    assert loaded.json()["task"] == "Template task"


def test_list_templates_endpoint(client):
    client.post("/api/templates", json={"name": "listed-template", "task": "Task"})
    response = client.get("/api/templates")
    assert response.status_code == 200
    assert any(item["name"] == "listed-template" for item in response.json())


def test_get_missing_template_returns_404(client):
    assert client.get("/api/templates/does-not-exist").status_code == 404


def test_create_template_rejects_missing_name(client):
    assert client.post("/api/templates", json={"task": "Task"}).status_code == 422


def test_create_template_rejects_empty_name(client):
    assert client.post("/api/templates", json={"name": "", "task": "Task"}).status_code == 422


def test_enhance_endpoint_maps_provider_error_to_502(client, monkeypatch):
    from prompt_forge.providers import ProviderError
    def fail(*args, **kwargs):
        raise ProviderError("provider unavailable")
    monkeypatch.setattr(web_module, "enhance_prompt", fail)
    response = client.post("/api/enhance", json={"prompt": "test"})
    assert response.status_code == 502
    assert "provider unavailable" in response.json()["detail"]


def test_enhance_endpoint_success(client, monkeypatch):
    monkeypatch.setattr(web_module, "enhance_prompt", lambda prompt, config: prompt + " improved")
    response = client.post("/api/enhance", json={"prompt": "test"})
    assert response.status_code == 200
    assert response.json() == {"prompt": "test improved"}


def test_enhance_endpoint_rejects_empty_prompt(client):
    assert client.post("/api/enhance", json={"prompt": ""}).status_code == 422


def test_enhance_endpoint_rejects_oversized_prompt(client):
    assert client.post("/api/enhance", json={"prompt": "x" * 50001}).status_code == 422


def test_build_endpoint_accepts_optional_fields(client):
    response = client.post("/api/build", json={"task": "Build", "requirements": ["One", "Two"], "lang": "en"})
    assert response.status_code == 200
    assert "Build" in response.json()["prompt"]


def test_export_endpoint_handles_invalid_spec(client):
    response = client.post("/api/export/md", json={"task": "Valid", "profile": "not-a-profile"})
    assert response.status_code == 422
