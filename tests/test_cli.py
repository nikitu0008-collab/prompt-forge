import json

from typer.testing import CliRunner

from prompt_forge.cli import app

runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "prompt-forge" in result.output


def test_build_prints_markdown_prompt():
    result = runner.invoke(
        app,
        ["build", "--task", "Калькулятор на Python", "--no-copy"],
    )
    assert result.exit_code == 0
    assert "## Задача" in result.output
    assert "Калькулятор на Python" in result.output


def test_build_accepts_all_fields():
    result = runner.invoke(
        app,
        [
            "build",
            "--task",
            "Калькулятор",
            "--profile",
            "bugfix",
            "--stack",
            "Python 3.11",
            "--context",
            "Пустой проект",
            "--require",
            "Без зависимостей",
            "--input",
            "args",
            "--output-format",
            "Только код",
            "--accept",
            "Не падает",
            "--example",
            "пустая строка",
            "--constraint",
            "Без сети",
            "--audience",
            "Новички",
            "--detail",
            "detailed",
            "--no-copy",
        ],
    )
    assert result.exit_code == 0
    output = result.output
    assert "## Контекст" in output
    assert "## Входные данные" in output
    assert "## Критерии готовности" in output
    assert "## Примеры и краевые случаи" in output
    assert "## Ограничения" in output
    assert "## Аудитория" in output
    assert "- Без зависимостей" in output


def test_build_json_format_is_valid_json():
    result = runner.invoke(
        app,
        ["build", "--task", "Калькулятор", "--format", "json", "--no-copy"],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["profile"] == "code"
    assert "## Задача" in payload["prompt"]


def test_build_plain_format_has_no_markdown():
    result = runner.invoke(
        app,
        ["build", "--task", "Калькулятор", "--format", "plain", "--no-copy"],
    )
    assert result.exit_code == 0
    assert "##" not in result.output
    assert "ЗАДАЧА:" in result.output


def test_build_english_output():
    result = runner.invoke(
        app,
        ["build", "--task", "Calculator", "--lang", "en", "--no-copy"],
    )
    assert result.exit_code == 0
    assert "## Task" in result.output


def test_build_requires_task():
    result = runner.invoke(app, ["build", "--no-copy"])
    assert result.exit_code != 0


def test_build_saves_file(tmp_path):
    target = tmp_path / "out" / "prompt.md"
    result = runner.invoke(
        app,
        ["build", "--task", "Калькулятор", "--save", str(target), "--no-copy"],
    )
    assert result.exit_code == 0
    assert target.exists()
    assert "## Задача" in target.read_text(encoding="utf-8")


def test_profiles_lists_all_profiles():
    result = runner.invoke(app, ["profiles"])
    assert result.exit_code == 0
    assert "code" in result.output
    assert "bugfix" in result.output


def test_profiles_show_example():
    result = runner.invoke(app, ["profiles", "--show", "code"])
    assert result.exit_code == 0
    assert "## Задача" in result.output
    assert "Калькулятор" in result.output or "калькулятор" in result.output


def test_profiles_show_unknown_profile():
    result = runner.invoke(app, ["profiles", "--show", "nope"])
    assert result.exit_code == 1


def test_json_command_returns_bundle():
    result = runner.invoke(app, ["json", "--task", "Калькулятор"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["spec"]["task"] == "Калькулятор"

from pathlib import Path

from prompt_forge import cli as cli_module


def test_build_rejects_whitespace_task():
    result = runner.invoke(
        app,
        ["build", "--task", "   ", "--no-copy"],
    )

    assert result.exit_code == 1
    assert "Задача" in result.output or "задач" in result.output.lower()


def test_build_copy_success(monkeypatch):
    copied = []

    monkeypatch.setattr(
        cli_module,
        "copy_to_clipboard",
        lambda text: copied.append(text) or True,
    )

    result = runner.invoke(
        app,
        ["build", "--task", "Clipboard test"],
    )

    assert result.exit_code == 0
    assert len(copied) == 1
    assert "Clipboard test" in copied[0]


def test_build_copy_failure(monkeypatch):
    monkeypatch.setattr(
        cli_module,
        "copy_to_clipboard",
        lambda text: False,
    )

    result = runner.invoke(
        app,
        ["build", "--task", "Clipboard failure", "--copy"],
    )

    assert result.exit_code == 0
    assert "Clipboard failure" in result.output


def test_build_save_failure_is_reported(monkeypatch, tmp_path):
    def fail_save(path, content):
        raise OSError("Disk is full")

    monkeypatch.setattr(cli_module, "save_to_file", fail_save)

    result = runner.invoke(
        app,
        [
            "build",
            "--task",
            "Save failure",
            "--save",
            str(tmp_path / "prompt.md"),
            "--no-copy",
        ],
    )

    # Текущая реализация сообщает об ошибке,
    # но не завершает команду с ненулевым кодом.
    assert result.exit_code == 0
    assert "Disk is full" in result.output


def test_build_enhance_success(monkeypatch):
    monkeypatch.setattr(
        cli_module,
        "enhance_prompt",
        lambda prompt, config: "Enhanced prompt result",
    )
    monkeypatch.setattr(
        cli_module,
        "copy_to_clipboard",
        lambda text: True,
    )

    result = runner.invoke(
        app,
        [
            "build",
            "--task",
            "Improve this task",
            "--enhance",
        ],
    )

    assert result.exit_code == 0
    assert "Enhanced prompt result" in result.output


def test_build_enhance_save_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cli_module,
        "enhance_prompt",
        lambda prompt, config: "Enhanced prompt",
    )

    def fail_save(path, content):
        raise OSError("Cannot write file")

    monkeypatch.setattr(cli_module, "save_to_file", fail_save)

    result = runner.invoke(
        app,
        [
            "build",
            "--task",
            "Enhance and save",
            "--enhance",
            "--save",
            str(tmp_path / "prompt.md"),
            "--no-copy",
        ],
    )

    assert result.exit_code == 1


def test_profiles_show_english_example():
    result = runner.invoke(
        app,
        ["profiles", "--show", "code", "--lang", "en"],
    )

    assert result.exit_code == 0
    assert "## Task" in result.output


def test_doctor_command_runs():
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Python" in result.output or "диагностика" in result.output.lower()


def test_templates_list_empty(monkeypatch):
    monkeypatch.setattr(
        cli_module,
        "list_templates",
        lambda: [],
    )

    result = runner.invoke(app, ["templates", "list"])

    assert result.exit_code == 0
    assert "шаблон" in result.output.lower()


def test_templates_list_with_items(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cli_module,
        "list_templates",
        lambda: [
            {"name": "example", "path": tmp_path / "example.json"}
        ],
    )

    result = runner.invoke(app, ["templates", "list"])

    assert result.exit_code == 0
    assert "example" in result.output


def test_templates_show_missing():
    result = runner.invoke(
        app,
        ["templates", "show", "missing-template"],
    )

    assert result.exit_code == 1


def test_templates_delete_missing(monkeypatch):
    monkeypatch.setattr(
        cli_module,
        "delete_template",
        lambda name: False,
    )

    result = runner.invoke(
        app,
        ["templates", "delete", "missing-template"],
    )

    assert result.exit_code == 1
    assert "missing-template" in result.output
def test_templates_save(monkeypatch, tmp_path):
    from unittest.mock import Mock

    expected_path = tmp_path / "example.json"
    save_mock = Mock(return_value=expected_path)

    monkeypatch.setattr(
        cli_module,
        "save_template",
        save_mock,
    )

    result = runner.invoke(
        app,
        [
            "templates",
            "save",
            "example",
            "--task",
            "Create an API",
        ],
    )

    assert result.exit_code == 0
    assert "Шаблон сохранён:" in result.output
    save_mock.assert_called_once()
