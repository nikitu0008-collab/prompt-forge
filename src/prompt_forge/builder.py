"""Сборка готового промпта из описания задачи."""

from __future__ import annotations

from prompt_forge.i18n import t
from prompt_forge.models import Detail, PromptSpec
from prompt_forge.profiles import get_profile

# Уровень детализации, начиная с которого раздел попадает в промпт.
_SECTION_MIN_DETAIL = {
    "task": Detail.BRIEF,
    "role": Detail.BRIEF,
    "requirements": Detail.BRIEF,
    "output": Detail.BRIEF,
    "context": Detail.STANDARD,
    "input": Detail.STANDARD,
    "constraints": Detail.STANDARD,
    "acceptance": Detail.DETAILED,
    "examples": Detail.DETAILED,
    "audience": Detail.DETAILED,
}

_DETAIL_ORDER = {
    Detail.BRIEF: 0,
    Detail.STANDARD: 1,
    Detail.DETAILED: 2,
}


def _bullets(items: list[str]) -> list[str]:
    return [f"- {item.strip()}" for item in items if item and item.strip()]


def _sections(spec: PromptSpec) -> list[tuple[str, str]]:
    """Возвращает список пар (ключ секции, содержимое) с учётом детализации."""
    profile = get_profile(spec.profile)
    lang = spec.lang
    sections: list[tuple[str, str]] = []

    sections.append(("task", spec.task.strip()))

    if profile:
        sections.append(("role", profile.role_text(lang, spec.stack)))

    if spec.context.strip():
        sections.append(("context", spec.context.strip()))

    requirements = spec.requirements or (profile.default_requirements(lang) if profile else [])
    requirements_md = "\n".join(_bullets(requirements))
    if requirements_md:
        sections.append(("requirements", requirements_md))

    if spec.input_spec.strip():
        sections.append(("input", spec.input_spec.strip()))

    output_format = spec.output_format.strip() or (profile.default_output_format(lang) if profile else "")
    if output_format.strip():
        sections.append(("output", output_format.strip()))

    acceptance_md = "\n".join(_bullets(spec.acceptance))
    if acceptance_md:
        sections.append(("acceptance", acceptance_md))

    examples_md = "\n".join(_bullets(spec.examples))
    if examples_md:
        sections.append(("examples", examples_md))

    constraints_md = "\n".join(_bullets(spec.constraints))
    if constraints_md:
        sections.append(("constraints", constraints_md))

    if spec.audience.strip():
        sections.append(("audience", spec.audience.strip()))

    return sections


def build_prompt(spec: PromptSpec) -> str:
    """Собирает промпт в Markdown."""
    lang = spec.lang
    threshold = _DETAIL_ORDER[spec.detail]
    blocks: list[str] = []

    preamble = t("preamble", lang)
    if spec.allow_questions:
        preamble = f"{preamble} {t('preamble_questions', lang)}"
    blocks.append(preamble)

    for key, body in _sections(spec):
        if _DETAIL_ORDER[_SECTION_MIN_DETAIL[key]] > threshold:
            continue
        heading = t(f"s_{key}", lang)
        blocks.append(f"## {heading}\n{body}")

    return "\n\n".join(blocks).strip() + "\n"


def to_plain(markdown: str) -> str:
    """Убирает markdown-заголовки, оставляя читаемый обычный текст."""
    lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            lines.append(f"{line[3:].strip().upper()}:")
        else:
            lines.append(line)
    return "\n".join(lines).strip() + "\n"


def build_bundle(spec: PromptSpec) -> dict:
    """Готовит структуру со всеми представлениями промпта."""
    markdown = build_prompt(spec)
    profile = get_profile(spec.profile)
    return {
        "prompt": markdown,
        "plain": to_plain(markdown),
        "profile": spec.profile.value,
        "profile_title": profile.label(spec.lang) if profile else "",
        "detail": spec.detail.value,
        "lang": spec.lang,
        "spec": spec.to_dict(),
    }
