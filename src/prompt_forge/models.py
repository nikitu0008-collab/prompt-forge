"""Модели данных, описывающие запрос на генерацию промпта."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class Detail(str, Enum):
    """Уровень детализации сгенерированного промпта."""

    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"


class OutputFormat(str, Enum):
    """Формат вывода результата."""

    MD = "md"
    PLAIN = "plain"
    JSON = "json"


class Lang(str, Enum):
    """Язык сгенерированного промпта."""

    RU = "ru"
    EN = "en"


class Profile(str, Enum):
    """Тип задачи. Определяет роль ассистента и структуру промпта."""

    CODE = "code"
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    TEST = "test"
    ARCHITECTURE = "architecture"
    REVIEW = "review"
    LEARN = "learn"
    TEXT = "text"
    DATA = "data"
    AUTOMATION = "automation"


@dataclass
class PromptSpec:
    """Полное описание того, что пользователь хочет получить от ИИ."""

    task: str
    profile: Profile = Profile.CODE
    stack: str = ""
    context: str = ""
    requirements: list[str] = field(default_factory=list)
    input_spec: str = ""
    output_format: str = ""
    acceptance: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    audience: str = ""
    detail: Detail = Detail.STANDARD
    lang: str = "ru"
    allow_questions: bool = True

    def to_dict(self) -> dict:
        data = asdict(self)
        data["profile"] = self.profile.value
        data["detail"] = self.detail.value
        return data
