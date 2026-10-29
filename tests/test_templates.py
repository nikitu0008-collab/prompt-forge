"""Tests for saving, listing, loading, and deleting templates."""
import json
from pathlib import Path

import pytest

from prompt_forge.models import Detail, Profile, PromptSpec
from prompt_forge.templates import delete_template, list_templates, load_template, save_template


def spec(**kwargs):
    values = {"task": "Написать тесты", "profile": Profile.TEST, "detail": Detail.DETAILED, "requirements": ["Проверить ошибки"]}
    values.update(kwargs)
    return PromptSpec(**values)


def test_save_template_creates_json_file(tmp_path):
    path = save_template("My Template", spec(), tmp_path)
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["name"] == "My Template"
    assert payload["spec"]["task"] == "Написать тесты"


def test_save_template_sanitizes_filename(tmp_path):
    path = save_template("my template / v1", spec(), tmp_path)
    assert path.parent == tmp_path
    assert path.name == "my-template-v1.json"


def test_save_template_rejects_empty_slug(tmp_path):
    with pytest.raises(ValueError, match="Название шаблона"):
        save_template(" !!! ", spec(), tmp_path)


def test_save_template_truncates_long_slug(tmp_path):
    path = save_template("x" * 100, spec(), tmp_path)
    assert len(path.stem) == 80


def test_load_template_round_trip(tmp_path):
    original = spec()
    save_template("sample", original, tmp_path)
    loaded = load_template("sample", tmp_path)
    assert loaded.task == original.task
    assert loaded.profile == Profile.TEST
    assert loaded.detail == Detail.DETAILED
    assert loaded.requirements == ["Проверить ошибки"]


def test_load_template_not_found(tmp_path):
    with pytest.raises(FileNotFoundError, match="Шаблон не найден"):
        load_template("missing", tmp_path)


def test_load_template_can_find_by_display_name(tmp_path):
    save_template("Display Name", spec(), tmp_path)
    loaded = load_template("Display Name", tmp_path)
    assert loaded.task == "Написать тесты"


def test_list_templates_sorts_by_filename(tmp_path):
    save_template("zulu", spec(task="z"), tmp_path)
    save_template("alpha", spec(task="a"), tmp_path)
    names = [item["name"] for item in list_templates(tmp_path)]
    assert names == ["alpha", "zulu"]


def test_list_templates_empty_directory(tmp_path):
    assert list_templates(tmp_path) == []


def test_list_templates_missing_directory(tmp_path):
    assert list_templates(tmp_path / "missing") == []


def test_list_templates_ignores_invalid_json(tmp_path):
    (tmp_path / "broken.json").write_text("{bad json", encoding="utf-8")
    assert list_templates(tmp_path) == []


def test_list_templates_ignores_non_json_files(tmp_path):
    (tmp_path / "notes.txt").write_text("not a template", encoding="utf-8")
    assert list_templates(tmp_path) == []


def test_delete_template_returns_false_when_missing(tmp_path):
    assert delete_template("absent", tmp_path) is False


def test_delete_template_removes_saved_template(tmp_path):
    save_template("remove-me", spec(), tmp_path)
    assert delete_template("remove-me", tmp_path) is True
    assert list_templates(tmp_path) == []


def test_load_template_rejects_invalid_enum(tmp_path):
    path = save_template("bad-enum", spec(), tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["spec"]["profile"] = "unknown-profile"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        load_template("bad-enum", tmp_path)
