"""FastAPI API для веб-интерфейса Prompt Forge. Установите extra: prompt-forge[web]."""
from __future__ import annotations
from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prompt_forge.builder import build_bundle
from prompt_forge.models import Detail, Profile, PromptSpec
from prompt_forge.profiles import PROFILES, get_profile
from prompt_forge.providers import ProviderConfig, ProviderError, enhance_prompt
from prompt_forge.output import render
from prompt_forge.templates import delete_template, list_templates, load_template, save_template
from prompt_forge.analysis import analyze_spec
from prompt_forge.history import add_history_entry, clear_history, load_history

app = FastAPI(title="Prompt Forge API", version="0.2.0", description="API для генерации и улучшения структурированных промптов")
class BuildRequest(BaseModel):
    task: str = Field(min_length=1, max_length=20000)
    profile: Profile = Profile.CODE
    stack: str = ""; context: str = ""; requirements: list[str] = Field(default_factory=list); input_spec: str = ""; output_format: str = ""
    acceptance: list[str] = Field(default_factory=list); examples: list[str] = Field(default_factory=list); constraints: list[str] = Field(default_factory=list); audience: str = ""
    detail: Detail = Detail.STANDARD; lang: str = "ru"; allow_questions: bool = True
class EnhanceRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=50000)
    provider: str = "openai-compatible"; model: str = "gpt-4o-mini"; base_url: str | None = None
class TemplateRequest(BuildRequest):
    name: str = Field(min_length=1, max_length=100)

@app.get("/api/health")
def health(): return {"status": "ok", "version": "0.2.0"}
@app.get("/api/info")
def info():
    return {
        "name": "Prompt Forge",
        "version": "0.3.0",
        "features": [
            "structured prompt generation",
            "multiple profiles",
            "prompt templates",
            "provider enhancement",
            "export formats",
        ],
    }
@app.get("/api/profiles")
def profiles(): return [{"key": p.value, "label": get_profile(p).label("ru")} for p in PROFILES if get_profile(p)]
@app.post("/api/build")
@app.post("/api/build")
def build(request: BuildRequest):
    data = request.model_dump()
    data["task"] = data["task"].strip()

    if not data["task"]:
        raise HTTPException(422, "task не должен быть пустым")

    bundle = build_bundle(PromptSpec(**data))

    add_history_entry(
        task=data["task"],
        prompt=bundle["prompt"],
        profile=data["profile"].value,
    )

    return bundle
@app.post("/api/analyze")
def analyze_prompt(request: BuildRequest):
    """Анализирует полноту спецификации промпта."""
    spec = PromptSpec(**request.model_dump())
    return analyze_spec(spec).to_dict()
@app.post("/api/export/{fmt}")
def export_prompt(fmt: str, request: BuildRequest):
    if fmt not in {"md", "plain", "json", "yaml"}:
        raise HTTPException(400, "Формат должен быть md, plain, json или yaml")
    try:
        output_format = {"md": "md", "plain": "plain", "json": "json", "yaml": "yaml"}[fmt]
        return {"format": fmt, "content": render(PromptSpec(**request.model_dump()), output_format)}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(400, str(exc)) from exc

@app.post("/api/enhance")
def enhance(request: EnhanceRequest):
    try: return {"prompt": enhance_prompt(request.prompt, ProviderConfig(provider=request.provider, model=request.model, base_url=request.base_url))}
    except ProviderError as exc: raise HTTPException(502, str(exc)) from exc
@app.get("/api/templates")
def templates(): return list_templates()
@app.post("/api/templates")
def create_template(request: TemplateRequest):
    data = request.model_dump(); name = data.pop("name")
    try: path = save_template(name, PromptSpec(**data))
    except (ValueError, OSError) as exc: raise HTTPException(400, str(exc)) from exc
    return {"name": name, "path": str(path)}
@app.get("/api/templates/{name}")
def get_template(name: str):
    try: return load_template(name).to_dict()
    except (FileNotFoundError, ValueError) as exc: raise HTTPException(404, str(exc)) from exc


@app.delete("/api/templates/{name}")
def remove_template(name: str):
    try:
        deleted = delete_template(name)
    except OSError as exc:
        raise HTTPException(500, f"Не удалось удалить шаблон: {exc}") from exc

    if not deleted:
        raise HTTPException(404, f"Шаблон не найден: {name}")

    return {
        "name": name,
        "deleted": True,
    }
@app.get("/api/history")
def history():
    return load_history()


@app.delete("/api/history")
def remove_history():
    deleted = clear_history()

    return {
        "cleared": deleted,
    }
