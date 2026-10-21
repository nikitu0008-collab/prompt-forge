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
