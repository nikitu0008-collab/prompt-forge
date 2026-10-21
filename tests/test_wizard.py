import pytest

from prompt_forge.models import Detail, Profile, PromptSpec
from prompt_forge.wizard import PromptForgeError, collect_spec, split_list


class FakePrompter:
    """Подставной ввод: отдаёт заранее заданные ответы по порядку."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.asked = []

    def text(self, message, default=""):
        self.asked.append(message)
        if self.answers:
            return self.answers.pop(0)
        return default

    def choice(self, message, choices, default):
        self.asked.append(message)
        if self.answers:
            return self.answers.pop(0)
        return default


def test_split_list_handles_commas_semicolons_and_newlines():
    assert split_list("а, б; в\nг") == ["а", "б", "в", "г"]
    assert split_list("  ") == []
    assert split_list("") == []


def test_collect_spec_fills_every_field():
    prompter = FakePrompter(
        [
            "ru",
            "Написать калькулятор",
            "Написать код",
            "Python 3.11",
            "Пустой проект",
            "Требование один, Требование два",
            "args: list[str]",
            "Только код",
            "Не падает, Есть тест",
            "пустая строка",
            "Без зависимостей",
            "Новички",
            "detailed",
        ]
    )
    spec = collect_spec(prompter)

    assert spec.task == "Написать калькулятор"
    assert spec.profile is Profile.CODE
    assert spec.stack == "Python 3.11"
    assert spec.context == "Пустой проект"
    assert spec.requirements == ["Требование один", "Требование два"]
    assert spec.input_spec == "args: list[str]"
    assert spec.output_format == "Только код"
    assert spec.acceptance == ["Не падает", "Есть тест"]
    assert spec.examples == ["пустая строка"]
    assert spec.constraints == ["Без зависимостей"]
    assert spec.audience == "Новички"
    assert spec.detail is Detail.DETAILED
    assert spec.lang == "ru"


def test_collect_spec_keeps_defaults_when_answers_are_empty():
    initial = PromptSpec(task="preset task")
    prompter = FakePrompter([])
    spec = collect_spec(prompter, initial)
    assert spec.task == "preset task"
    assert spec.profile is Profile.CODE
    assert spec.requirements


def test_collect_spec_requires_task():
    prompter = FakePrompter(["ru", ""])
    with pytest.raises(PromptForgeError):
        collect_spec(prompter)


def test_collect_spec_switches_language():
    prompter = FakePrompter(["en", "Write a calculator", "Write code"])
    spec = collect_spec(prompter)
    assert spec.lang == "en"
    assert spec.profile is Profile.CODE
    assert spec.task == "Write a calculator"


def test_collect_spec_keeps_initial_spec_values():
    initial = PromptSpec(task="preset task", profile=Profile.BUGFIX, lang="ru")
    prompter = FakePrompter([])
    spec = collect_spec(prompter, initial)
    assert spec.profile is Profile.BUGFIX
