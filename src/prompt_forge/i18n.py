"""Строки интерфейса и промптов на русском и английском."""

from __future__ import annotations

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "app_name": "Prompt Forge",
        "app_tagline": "Генератор структурированных промптов для ИИ",
        "preamble": (
            "Ниже описана задача. Отвечай строго в указанном формате, "
            "не добавляй лишних объяснений и не отклоняйся от требований."
        ),
        "preamble_questions": (
            "Если условия противоречат друг другу или чего-то критически не хватает - "
            "сначала задай не больше 3 уточняющих вопросов, затем выполни задачу."
        ),
        "s_task": "Задача",
        "s_role": "Роль",
        "s_context": "Контекст",
        "s_requirements": "Требования",
        "s_input": "Входные данные",
        "s_output": "Формат ответа",
        "s_acceptance": "Критерии готовности",
        "s_examples": "Примеры и краевые случаи",
        "s_constraints": "Ограничения",
        "s_audience": "Аудитория",
        "q_task": "Опишите задачу своими словами",
        "q_task_hint": "Например: программа на Python, которая считает статистику по CSV-файлу",
        "q_profile": "Что нужно сделать?",
        "q_stack": "Язык, библиотека или стек",
        "q_stack_hint": "Например: Python 3.11 + pandas + pytest",
        "q_context": "Контекст: что уже есть и где это будет использоваться",
        "q_requirements": "Требования (через запятую)",
        "q_input": "Входные данные или интерфейс",
        "q_output": "Формат ответа",
        "q_acceptance": "Критерии готовности (через запятую)",
        "q_examples": "Примеры и краевые случаи (через запятую)",
        "q_constraints": "Ограничения: чего избегать (через запятую)",
        "q_audience": "Для кого результат",
        "q_detail": "Насколько подробный промпт",
        "q_lang": "Язык промпта",
        "d_brief": "brief",
        "d_standard": "standard",
        "d_detailed": "detailed",
        "default_hint": "по умолчанию",
        "yes": "да",
        "copied": "Промпт скопирован в буфер обмена",
        "copy_failed": "Не удалось скопировать в буфер обмена",
        "saved": "Сохранено в {path}",
        "saved_failed": "Не удалось сохранить файл: {error}",
        "task_required": "Нужно описать задачу: используйте --task или запустите интерактивно.",
        "unknown_profile": "Неизвестный профиль: {key}",
        "usage_hint": "Подсказка: prompt-forge build --task \"калькулятор на Python\"",
    },
    "en": {
        "app_name": "Prompt Forge",
        "app_tagline": "Structured prompt generator for AI",
        "preamble": (
            "The task is described below. Follow the requested output format exactly, "
            "skip unnecessary explanations and do not violate the requirements."
        ),
        "preamble_questions": (
            "If the requirements contradict each other or something critical is missing - "
            "ask at most 3 clarifying questions first, then do the task."
        ),
        "s_task": "Task",
        "s_role": "Role",
        "s_context": "Context",
        "s_requirements": "Requirements",
        "s_input": "Input",
        "s_output": "Output format",
        "s_acceptance": "Acceptance criteria",
        "s_examples": "Examples and edge cases",
        "s_constraints": "Constraints",
        "s_audience": "Audience",
        "q_task": "Describe the task in your own words",
        "q_task_hint": "For example: a Python program that computes stats over a CSV file",
        "q_profile": "What needs to be done?",
        "q_stack": "Language, library or stack",
        "q_stack_hint": "For example: Python 3.11 + pandas + pytest",
        "q_context": "Context: what already exists and where the result will be used",
        "q_requirements": "Requirements (comma separated)",
        "q_input": "Input data or interface",
        "q_output": "Output format",
        "q_acceptance": "Acceptance criteria (comma separated)",
        "q_examples": "Examples and edge cases (comma separated)",
        "q_constraints": "Constraints: what to avoid (comma separated)",
        "q_audience": "Who is the result for",
        "q_detail": "How detailed should the prompt be",
        "q_lang": "Prompt language",
        "d_brief": "brief",
        "d_standard": "standard",
        "d_detailed": "detailed",
        "default_hint": "default",
        "yes": "yes",
        "copied": "Prompt copied to clipboard",
        "copy_failed": "Failed to copy to clipboard",
        "saved": "Saved to {path}",
        "saved_failed": "Failed to save file: {error}",
        "task_required": "A task description is required: use --task or run interactively.",
        "unknown_profile": "Unknown profile: {key}",
        "usage_hint": "Hint: prompt-forge build --task \"a Python calculator\"",
    },
}

DEFAULT_LANG = "ru"


def t(key: str, lang: str = DEFAULT_LANG, **kwargs: object) -> str:
    """Возвращает локализованную строку с подстановкой аргументов."""
    table = TEXTS.get(lang) or TEXTS[DEFAULT_LANG]
    text = table.get(key) or TEXTS[DEFAULT_LANG].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
