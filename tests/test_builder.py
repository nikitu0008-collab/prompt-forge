import pytest

from prompt_forge.builder import build_bundle, build_prompt, to_plain
from prompt_forge.models import Detail, Profile, PromptSpec


def make_spec(**kwargs) -> PromptSpec:
    defaults = dict(task="Написать калькулятор на Python", profile=Profile.CODE)
    defaults.update(kwargs)
    return PromptSpec(**defaults)


def test_task_and_role_are_always_present():
    prompt = build_prompt(make_spec(detail=Detail.BRIEF))
    assert "## Задача" in prompt
    assert "## Роль" in prompt
    assert "калькулятор" in prompt


def test_brief_hides_optional_sections():
    prompt = build_prompt(
        make_spec(
            detail=Detail.BRIEF,
            context="Пустой проект",
            input_spec="args: list[str]",
            acceptance=["Не падает на мусоре"],
            examples=["пустая строка"],
            constraints=["Без зависимостей"],
        )
    )
    assert "## Контекст" not in prompt
    assert "## Входные данные" not in prompt
    assert "## Критерии готовности" not in prompt
    assert "## Примеры" not in prompt
    assert "## Ограничения" not in prompt


def test_standard_shows_context_and_constraints():
    prompt = build_prompt(
        make_spec(
            detail=Detail.STANDARD,
            context="Пустой проект",
            constraints=["Без зависимостей"],
            acceptance=["Не падает"],
        )
    )
    assert "## Контекст" in prompt
    assert "## Ограничения" in prompt
    assert "## Критерии готовности" not in prompt


def test_detailed_shows_everything():
    prompt = build_prompt(
        make_spec(
            detail=Detail.DETAILED,
            context="Пустой проект",
            input_spec="args: list[str]",
            acceptance=["Не падает"],
            examples=["пустая строка"],
            constraints=["Без зависимостей"],
            audience="Новички",
        )
    )
    for section in (
        "## Задача",
        "## Роль",
        "## Контекст",
        "## Требования",
        "## Входные данные",
        "## Формат ответа",
        "## Критерии готовности",
        "## Примеры и краевые случаи",
        "## Ограничения",
        "## Аудитория",
    ):
        assert section in prompt


def test_requirements_are_rendered_as_bullets():
    prompt = build_prompt(make_spec(requirements=["Первое", "Второе"]))
    assert "- Первое" in prompt
    assert "- Второе" in prompt


def test_profile_defaults_are_used_when_requirements_empty():
    prompt = build_prompt(make_spec(requirements=[]))
    assert "## Требования" in prompt
    assert "- " in prompt


def test_stack_is_added_to_role():
    prompt = build_prompt(make_spec(stack="Python 3.11 + pytest"))
    assert "Python 3.11 + pytest" in prompt


def test_english_prompt_uses_english_headings():
    prompt = build_prompt(make_spec(lang="en", detail=Detail.DETAILED))
    assert "## Task" in prompt
    assert "## Role" in prompt
    assert "## Output format" in prompt


def test_questions_block_can_be_disabled():
    with_questions = build_prompt(make_spec(allow_questions=True))
    without_questions = build_prompt(make_spec(allow_questions=False))
    assert "уточняющих вопросов" in with_questions
    assert "уточняющих вопросов" not in without_questions


def test_to_plain_strips_markdown_headings():
    plain = to_plain(build_prompt(make_spec()))
    assert "##" not in plain
    assert "ЗАДАЧА:" in plain


def test_build_bundle_contains_all_representations():
    bundle = build_bundle(make_spec())
    assert set(bundle) == {"prompt", "plain", "profile", "profile_title", "detail", "lang", "spec"}
    assert bundle["profile"] == "code"
    assert bundle["lang"] == "ru"
    assert bundle["spec"]["profile"] == "code"


def test_empty_task_produces_empty_section():
    prompt = build_prompt(make_spec(task=""))
    assert "## Задача" in prompt


@pytest.mark.parametrize("profile", list(Profile))
def test_every_profile_produces_prompt(profile):
    prompt = build_prompt(make_spec(profile=profile, detail=Detail.DETAILED))
    assert "## Задача" in prompt
    assert "## Формат ответа" in prompt
