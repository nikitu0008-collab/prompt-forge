"""Интерактивный визард: превращает ответы пользователя в описание задачи."""

from __future__ import annotations

from typing import Protocol, Sequence

from prompt_forge.i18n import t
from prompt_forge.models import Detail, Profile, PromptSpec
from prompt_forge.profiles import PROFILES, get_profile


class PromptForgeError(Exception):
    """Ошибка, из-за которой нельзя собрать промпт."""


class Prompter(Protocol):
    """Минимальный интерфейс ввода данных (реальный или подставной в тестах)."""

    def text(self, message: str, default: str = "") -> str: ...

    def choice(self, message: str, choices: Sequence[str], default: str) -> str: ...


class RichPrompter:
    """Реализация поверх rich.prompt."""

    @staticmethod
    def _clean(value: str) -> str:
        return str(value).replace("\ufeff", "").strip()

    def text(self, message: str, default: str = "") -> str:
        from rich.prompt import Prompt

        answer = Prompt.ask(message, default=default if default else None)
        return "" if answer is None else self._clean(answer)

    def choice(self, message: str, choices: Sequence[str], default: str) -> str:
        from rich.prompt import Prompt

        answer = Prompt.ask(message, choices=list(choices), default=default)
        return self._clean(answer)


def split_list(raw: str) -> list[str]:
    """Разбивает строку со списком по запятым, точкам с запятой и переносам строк."""
    if not raw:
        return []
    parts: list[str] = []
    for chunk in raw.replace(";", "\n").replace(",", "\n").split("\n"):
        item = chunk.strip(" .")
        if item:
            parts.append(item)
    return parts


def _with_hint(question: str, hint: str, lang: str) -> str:
    """Добавляет к вопросу подсказку со значением по умолчанию."""
    if not hint:
        return question
    return f"{question} [{t('default_hint', lang)}: {hint}]"


def _profile_by_label(lang: str) -> dict[str, Profile]:
    mapping: dict[str, Profile] = {}
    for profile in PROFILES:
        spec = get_profile(profile)
        if spec:
            mapping[spec.label(lang)] = profile
    return mapping


def _label_of(profile: Profile, lang: str) -> str:
    spec = get_profile(profile)
    return spec.label(lang) if spec else profile.value


def collect_spec(prompter: Prompter, spec: PromptSpec | None = None) -> PromptSpec:
    """Задаёт пользователю серию вопросов и возвращает заполненный PromptSpec."""
    spec = spec or PromptSpec(task="")

    lang = prompter.choice(t("q_lang", spec.lang), ["ru", "en"], default=spec.lang)
    spec.lang = lang if lang in ("ru", "en") else "ru"

    task = prompter.text(t("q_task", spec.lang), default=spec.task).strip()
    if not task:
        raise PromptForgeError(t("task_required", spec.lang))
    spec.task = task

    labels = _profile_by_label(spec.lang)
    default_label = _label_of(spec.profile, spec.lang)
    chosen_label = prompter.choice(t("q_profile", spec.lang), list(labels), default=default_label)
    spec.profile = labels.get(chosen_label, spec.profile)

    profile = get_profile(spec.profile)
    if profile is None:  # pragma: no cover - защита от неконсистентных данных
        raise PromptForgeError(t("unknown_profile", spec.lang, key=spec.profile.value))

    if profile.asks_stack:
        default_stack = spec.stack or profile.default_stack(spec.lang)
        stack = prompter.text(t("q_stack", spec.lang), default=default_stack).strip()
        spec.stack = stack

    context = prompter.text(t("q_context", spec.lang), default=spec.context).strip()
    if context:
        spec.context = context

    default_requirements = profile.default_requirements(spec.lang)
    requirements_raw = prompter.text(
        _with_hint(t("q_requirements", spec.lang), ", ".join(default_requirements), spec.lang),
        default="",
    ).strip()
    if requirements_raw:
        spec.requirements = split_list(requirements_raw)
    else:
        spec.requirements = default_requirements

    input_spec = prompter.text(t("q_input", spec.lang), default=spec.input_spec).strip()
    if input_spec:
        spec.input_spec = input_spec

    default_output = spec.output_format or profile.default_output_format(spec.lang)
    output_format = prompter.text(
        _with_hint(t("q_output", spec.lang), default_output, spec.lang),
        default="",
    ).strip()
    spec.output_format = output_format or default_output

    acceptance_raw = prompter.text(
        _with_hint(t("q_acceptance", spec.lang), ", ".join(spec.acceptance), spec.lang),
        default="",
    ).strip()
    if acceptance_raw:
        spec.acceptance = split_list(acceptance_raw)

    examples_raw = prompter.text(
        _with_hint(t("q_examples", spec.lang), ", ".join(spec.examples), spec.lang),
        default="",
    ).strip()
    if examples_raw:
        spec.examples = split_list(examples_raw)

    constraints_raw = prompter.text(
        _with_hint(t("q_constraints", spec.lang), ", ".join(spec.constraints), spec.lang),
        default="",
    ).strip()
    if constraints_raw:
        spec.constraints = split_list(constraints_raw)

    audience = prompter.text(t("q_audience", spec.lang), default=spec.audience).strip()
    if audience:
        spec.audience = audience

    detail_labels = [t("d_brief", spec.lang), t("d_standard", spec.lang), t("d_detailed", spec.lang)]
    detail = prompter.choice(t("q_detail", spec.lang), detail_labels, default=spec.detail.value)
    mapping = {
        t("d_brief", spec.lang): Detail.BRIEF,
        t("d_standard", spec.lang): Detail.STANDARD,
        t("d_detailed", spec.lang): Detail.DETAILED,
    }
    spec.detail = mapping.get(detail, Detail.STANDARD)

    return spec
