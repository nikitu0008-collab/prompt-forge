"""Анализ полноты и качества спецификации промпта."""

from __future__ import annotations

from dataclasses import dataclass

from prompt_forge.models import PromptSpec


@dataclass(frozen=True)
class AnalysisResult:
    """Результат анализа спецификации промпта."""

    score: int
    warnings: list[str]
    suggestions: list[str]
    completed_fields: int
    total_fields: int

    def to_dict(self) -> dict[str, object]:
        """Преобразует результат в словарь."""
        return {
            "score": self.score,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "completed_fields": self.completed_fields,
            "total_fields": self.total_fields,
        }


def _has_value(value: object) -> bool:
    """Проверяет, содержит ли поле полезное значение."""
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)

    return True


def analyze_spec(spec: PromptSpec) -> AnalysisResult:
    """Анализирует заполненность и качество PromptSpec."""
    fields = {
        "task": spec.task,
        "stack": spec.stack,
        "context": spec.context,
        "requirements": spec.requirements,
        "input_spec": spec.input_spec,
        "output_format": spec.output_format,
        "acceptance": spec.acceptance,
        "examples": spec.examples,
        "constraints": spec.constraints,
        "audience": spec.audience,
    }

    completed_fields = sum(
        _has_value(value) for value in fields.values()
    )
    total_fields = len(fields)
    score = round(completed_fields / total_fields * 100)

    warnings: list[str] = []
    suggestions: list[str] = []

    if not spec.task.strip():
        warnings.append("Не указана основная задача.")

    if len(spec.task.strip()) < 15:
        warnings.append(
            "Описание задачи слишком короткое и может быть неоднозначным."
        )

    if not _has_value(spec.requirements):
        suggestions.append(
            "Добавьте требования, чтобы точнее определить ожидаемый результат."
        )

    if not _has_value(spec.acceptance):
        suggestions.append(
            "Добавьте критерии готовности для проверки результата."
        )

    if not _has_value(spec.constraints):
        suggestions.append(
            "Укажите ограничения, если результат должен соответствовать "
            "определённым условиям."
        )

    if not _has_value(spec.context):
        suggestions.append(
            "Добавьте контекст проекта, если он важен для выполнения задачи."
        )

    if not _has_value(spec.output_format):
        suggestions.append(
            "Укажите желаемый формат ответа."
        )

    return AnalysisResult(
        score=score,
        warnings=warnings,
        suggestions=suggestions,
        completed_fields=completed_fields,
        total_fields=total_fields,
    )
