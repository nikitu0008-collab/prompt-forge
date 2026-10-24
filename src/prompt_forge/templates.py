"""Управление пользовательскими шаблонами Prompt Forge."""
from __future__ import annotations
import json
import re
from pathlib import Path
from prompt_forge.models import Detail, Profile, PromptSpec


def templates_dir() -> Path:
    return Path.home() / ("AppData/Roaming/prompt-forge" if __import__("os").name == "nt" else ".config/prompt-forge") / "templates"

def _slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9а-яА-Я_-]+", "-", name.strip()).strip("-_")
    if not slug:
        raise ValueError("Название шаблона не должно быть пустым")
    return slug[:80]

def save_template(name: str, spec: PromptSpec, directory: Path | None = None) -> Path:
    root = Path(directory) if directory else templates_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{_slug(name)}.json"
    payload = {"name": name.strip(), "spec": spec.to_dict()}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def list_templates(directory: Path | None = None) -> list[dict[str, str]]:
    root = Path(directory) if directory else templates_dir()
    if not root.exists(): return []
    result = []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            result.append({"name": str(data.get("name", path.stem)), "path": str(path)})
        except (OSError, ValueError):
            continue
    return result

def load_template(name: str, directory: Path | None = None) -> PromptSpec:
    root = Path(directory) if directory else templates_dir()
    direct = root / f"{_slug(name)}.json"
    path = direct if direct.exists() else next((Path(x["path"]) for x in list_templates(root) if x["name"] == name), None)
    if path is None or not path.is_file(): raise FileNotFoundError(f"Шаблон не найден: {name}")
    data = json.loads(path.read_text(encoding="utf-8"))["spec"]
    data["profile"] = Profile(data.get("profile", "code"))
    data["detail"] = Detail(data.get("detail", "standard"))
    return PromptSpec(**data)

def delete_template(name: str, directory: Path | None = None) -> bool:
    root = Path(directory) if directory else templates_dir()
    path = root / f"{_slug(name)}.json"
    if not path.exists():
        found = next((Path(x["path"]) for x in list_templates(root) if x["name"] == name), None)
        if found is None: return False
        path = found
    path.unlink()
    return True
