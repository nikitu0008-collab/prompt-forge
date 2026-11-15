"""Tests for Prompt Forge specification analysis."""

from prompt_forge.analysis import analyze_spec
from prompt_forge.models import PromptSpec


def test_analyze_empty_spec_reports_warnings():
    result = analyze_spec(PromptSpec(task=""))

    assert result.score < 100
    assert result.warnings
    assert any(
        "Не указана основная задача" in warning
        for warning in result.warnings
    )


def test_analyze_short_task_reports_warning():
    result = analyze_spec(PromptSpec(task="API"))

    assert any(
        "слишком короткое" in warning
        for warning in result.warnings
    )


def test_analyze_complete_spec_has_high_score():
    spec = PromptSpec(
        task="Создать REST API для управления задачами",
        stack="Python 3.11, FastAPI",
        context="Backend-сервис для веб-приложения",
        requirements=["Использовать REST API"],
        input_spec="JSON-запрос",
        output_format="JSON",
        acceptance=["Все endpoints должны работать"],
        examples=["POST /tasks"],
        constraints=["Не использовать внешнюю базу данных"],
        audience="Backend-разработчики",
    )

    result = analyze_spec(spec)

    assert result.score == 100
    assert result.completed_fields == result.total_fields
    assert not result.warnings


def test_analyze_returns_recommendations_for_missing_fields():
    result = analyze_spec(
        PromptSpec(task="Создать приложение для управления задачами")
    )

    assert result.suggestions


def test_analysis_result_can_be_converted_to_dict():
    result = analyze_spec(
        PromptSpec(task="Создать API для пользователей")
    )

    data = result.to_dict()

    assert data["score"] == result.score
    assert "warnings" in data
    assert "suggestions" in data
    assert data["completed_fields"] == result.completed_fields
