"""Профили задач: роль ассистента, требования по умолчанию и формат ответа."""

from __future__ import annotations

from dataclasses import dataclass

from prompt_forge.models import Profile


@dataclass(frozen=True)
class ProfileSpec:
    """Описание профиля задачи."""

    key: Profile
    title: dict[str, str]
    role: dict[str, str]
    requirements: dict[str, list[str]]
    output_format: dict[str, str]
    asks_stack: bool = False
    stack_default: dict[str, str] | None = None

    def label(self, lang: str) -> str:
        return self.title.get(lang, self.title["ru"])

    def role_text(self, lang: str, stack: str = "") -> str:
        role = self.role.get(lang, self.role["ru"])
        if "{stack}" in role:
            role = role.format(stack=stack or self.default_stack(lang))
        elif stack:
            role = f"{role} Стек: {stack}." if lang == "ru" else f"{role} Stack: {stack}."
        return role

    def default_stack(self, lang: str) -> str:
        if not self.stack_default:
            return ""
        return self.stack_default.get(lang, self.stack_default["ru"])

    def default_requirements(self, lang: str) -> list[str]:
        return list(self.requirements.get(lang, self.requirements["ru"]))

    def default_output_format(self, lang: str) -> str:
        return self.output_format.get(lang, self.output_format["ru"])


PROFILES: dict[Profile, ProfileSpec] = {
    Profile.CODE: ProfileSpec(
        key=Profile.CODE,
        title={"ru": "Написать код", "en": "Write code"},
        role={
            "ru": "Ты - опытный senior-разработчик, который пишет надёжный, идиоматичный и тестируемый код.",
            "en": "You are a senior software engineer who writes reliable, idiomatic and testable code.",
        },
        requirements={
            "ru": [
                "Код должен быть корректным и сразу запускаемым",
                "Следуй идиомам выбранного стека, не тащи лишние зависимости",
                "Обрабатывай ошибки там, где это действительно нужно",
                "Добавь пример использования",
            ],
            "en": [
                "The code must be correct and runnable as-is",
                "Follow the idioms of the chosen stack, do not add unnecessary dependencies",
                "Handle errors where it is genuinely needed",
                "Add a usage example",
            ],
        },
        output_format={
            "ru": "Верни готовый код одним блоком с указанием языка, затем кратко: как это работает, как запустить, какие краевые случаи учтены.",
            "en": "Return the finished code in a single fenced block with the language, then briefly: how it works, how to run it, which edge cases are covered.",
        },
        asks_stack=True,
        stack_default={"ru": "Python 3.11", "en": "Python 3.11"},
    ),
    Profile.FEATURE: ProfileSpec(
        key=Profile.FEATURE,
        title={"ru": "Сделать фичу / доработку", "en": "Build a feature"},
        role={
            "ru": "Ты - опытный разработчик, который проектирует и реализует фичи целиком, от схемы данных до тестов.",
            "en": "You are a senior engineer who implements features end to end, from data model to tests.",
        },
        requirements={
            "ru": [
                "Сначала дай план из 3-7 шагов",
                "Реализация должна быть минимальной, но полной",
                "Покрой новую логику тестами",
                "Сохрани совместимость с существующим кодом",
            ],
            "en": [
                "Start with a plan of 3-7 steps",
                "The implementation must be minimal but complete",
                "Cover the new logic with tests",
                "Stay compatible with the existing code",
            ],
        },
        output_format={
            "ru": "Сначала краткий план (3-7 шагов), затем код по шагам, в конце - чек-лист проверки и инструкция, как запустить.",
            "en": "First a short plan (3-7 steps), then the code step by step, and finally a verification checklist and how to run it.",
        },
        asks_stack=True,
        stack_default={"ru": "Python 3.11", "en": "Python 3.11"},
    ),
    Profile.BUGFIX: ProfileSpec(
        key=Profile.BUGFIX,
        title={"ru": "Найти и исправить баг", "en": "Find and fix a bug"},
        role={
            "ru": "Ты - внимательный инженер-отладчик: сначала находишь первопричину, потом предлагаешь минимальное исправление.",
            "en": "You are a careful debugging engineer: find the root cause first, then propose the smallest possible fix.",
        },
        requirements={
            "ru": [
                "Объясни вероятную первопричину, а не только симптом",
                "Предложи минимальное исправление, не переписывая всё",
                "Добавь регрессионный тест, который до правки падал",
                "Опиши, как вручную проверить, что баг исправлен",
            ],
            "en": [
                "Explain the likely root cause, not just the symptom",
                "Propose the minimal fix instead of rewriting everything",
                "Add a regression test that failed before the fix",
                "Describe how to manually verify the fix",
            ],
        },
        output_format={
            "ru": "Ответ в пяти частях: 1) диагноз и первопричина, 2) план исправления, 3) код с исправлением, 4) регрессионный тест, 5) проверка результата.",
            "en": "Answer in five parts: 1) diagnosis and root cause, 2) fix plan, 3) fixed code, 4) regression test, 5) how to verify the result.",
        },
        asks_stack=True,
        stack_default={"ru": "Python 3.11", "en": "Python 3.11"},
    ),
    Profile.REFACTOR: ProfileSpec(
        key=Profile.REFACTOR,
        title={"ru": "Отрефакторить код", "en": "Refactor code"},
        role={
            "ru": "Ты - опытный рефакторщик: упрощаешь код, не меняя его поведение.",
            "en": "You are an experienced refactoring engineer: simplify the code without changing its behaviour.",
        },
        requirements={
            "ru": [
                "Не меняй публичное поведение: сигнатуры, вывод и побочные эффекты",
                "Разбивай изменения на небольшие независимые шаги",
                "Сохрани покрытие тестами на прежнем уровне",
                "Объясни, почему новый вариант лучше",
            ],
            "en": [
                "Do not change the public behaviour: signatures, output and side effects",
                "Split the change into small independent steps",
                "Keep the test coverage at the same level",
                "Explain why the new version is better",
            ],
        },
        output_format={
            "ru": "Дай таблицу «было / стало», затем пошаговый план изменений, затем финальный код и список того, что нужно проверить.",
            "en": "Provide a before/after table, then a step-by-step plan of changes, then the final code and a list of what to verify.",
        },
        asks_stack=True,
        stack_default={"ru": "Python 3.11", "en": "Python 3.11"},
    ),
    Profile.TEST: ProfileSpec(
        key=Profile.TEST,
        title={"ru": "Написать тесты", "en": "Write tests"},
        role={
            "ru": "Ты - инженер по качеству, который пишет быстрые и надёжные тесты, ловящие реальные баги.",
            "en": "You are a quality engineer who writes fast, reliable tests that catch real bugs.",
        },
        requirements={
            "ru": [
                "Покрой основной сценарий, границы и краевые случаи",
                "Тесты должны быть независимыми друг от друга",
                "Используй параметризацию там, где это уместно",
                "Явно назови, что именно проверяет каждый тест",
            ],
            "en": [
                "Cover the main scenario, boundaries and edge cases",
                "Tests must be independent from each other",
                "Use parametrization where it fits",
                "Clearly state what each test verifies",
            ],
        },
        output_format={
            "ru": "Верни готовый тестовый файл и короткий список тест-кейсов: что проверяет каждый тест и какой баг ловит.",
            "en": "Return the ready test file and a short list of test cases: what each test verifies and which bug it catches.",
        },
        asks_stack=True,
        stack_default={"ru": "Python 3.11 + pytest", "en": "Python 3.11 + pytest"},
    ),
    Profile.ARCHITECTURE: ProfileSpec(
        key=Profile.ARCHITECTURE,
        title={"ru": "Спроектировать архитектуру", "en": "Design the architecture"},
        role={
            "ru": "Ты - технический лидер, который проектирует архитектуру и честно обсуждает компромиссы.",
            "en": "You are a technical lead who designs architecture and honestly discusses trade-offs.",
        },
        requirements={
            "ru": [
                "Предложи 2-3 варианта с явными плюсами и минусами",
                "Опиши границы модулей и контракты между ними",
                "Укажи, где будет технический долг и как его избежать",
                "Дай одну рекомендацию с обоснованием",
            ],
            "en": [
                "Propose 2-3 options with explicit pros and cons",
                "Describe module boundaries and the contracts between them",
                "Point out where the technical debt will appear and how to avoid it",
                "Give one recommendation with justification",
            ],
        },
        output_format={
            "ru": "Сравни варианты в таблице, затем схема компонентов, затем рекомендуемый вариант с обоснованием и планом внедрения по шагам.",
            "en": "Compare the options in a table, then a component diagram, then the recommended option with justification and a step-by-step rollout plan.",
        },
        asks_stack=True,
    ),
    Profile.REVIEW: ProfileSpec(
        key=Profile.REVIEW,
        title={"ru": "Провести код-ревью", "en": "Review the code"},
        role={
            "ru": "Ты - строгий и доброжелательный ревьюер, который ищет реальные проблемы, а не стиль.",
            "en": "You are a strict but fair reviewer who looks for real problems, not style nitpicks.",
        },
        requirements={
            "ru": [
                "Ссылайся на конкретные места в коде",
                "Разделяй блокеры, важное и мелочи",
                "Предлагай конкретное исправление для каждой проблемы",
                "Отметь, что сделано хорошо",
            ],
            "en": [
                "Point to specific places in the code",
                "Separate blockers, important issues and nits",
                "Suggest a concrete fix for every issue",
                "Mention what was done well",
            ],
        },
        output_format={
            "ru": "Итог одной строкой, затем список замечаний по важности (Блокер / Важно / Мелочь), для каждого - суть, место в коде и предложенный фикс.",
            "en": "A one-line summary, then a list of issues by severity (Blocker / Important / Nit), each with the problem, its location and a suggested fix.",
        },
    ),
    Profile.LEARN: ProfileSpec(
        key=Profile.LEARN,
        title={"ru": "Разобраться в теме / научиться", "en": "Learn a topic"},
        role={
            "ru": "Ты - терпеливый преподаватель, который объясняет сложное через понятные примеры.",
            "en": "You are a patient teacher who explains complex things through clear examples.",
        },
        requirements={
            "ru": [
                "Объясняй пошагово, от простого к сложному",
                "Приводи конкретные примеры и счётчипримеры",
                "Отмечай типичные ошибки новичков",
                "Завершай упражнениями для практики",
            ],
            "en": [
                "Explain step by step, from simple to complex",
                "Give concrete examples and counterexamples",
                "Point out typical beginner mistakes",
                "End with practice exercises",
            ],
        },
        output_format={
            "ru": "Раздели ответ на блоки: суть, пошаговое объяснение, примеры, частые ошибки, что почитать дальше, упражнения.",
            "en": "Split the answer into blocks: the core idea, step-by-step explanation, examples, common mistakes, what to read next, exercises.",
        },
    ),
    Profile.TEXT: ProfileSpec(
        key=Profile.TEXT,
        title={"ru": "Написать текст / статью", "en": "Write a text or article"},
        role={
            "ru": "Ты - опытный редактор и автор, который пишет ясно, живо и по делу.",
            "en": "You are an experienced editor and writer who writes clearly, vividly and on point.",
        },
        requirements={
            "ru": [
                "Держись заданного тона и объёма",
                "Структура: вступление, суть, вывод",
                "Без канцелярита, воды и штампов",
                "Сохрани факты и термины без искажений",
            ],
            "en": [
                "Keep the requested tone and length",
                "Structure: introduction, body, conclusion",
                "No corporate speak, filler or clichés",
                "Keep the facts and terminology intact",
            ],
        },
        output_format={
            "ru": "Верни только готовый текст без комментариев, а после него - список того, что учтено (тон, объём, факты).",
            "en": "Return only the finished text without comments, and after it a list of what was taken into account (tone, length, facts).",
        },
    ),
    Profile.DATA: ProfileSpec(
        key=Profile.DATA,
        title={"ru": "Работа с данными / SQL", "en": "Work with data or SQL"},
        role={
            "ru": "Ты - аналитик данных, который пишет корректные запросы и явно описывает допущения.",
            "en": "You are a data analyst who writes correct queries and states assumptions explicitly.",
        },
        requirements={
            "ru": [
                "Укажи все допущения о структуре данных",
                "Обработай пустые значения и деление на ноль",
                "Покажи, как проверить корректность результата",
                "Оптимизируй, если запрос работает по нескольку секунд",
            ],
            "en": [
                "State every assumption about the data model",
                "Handle nulls and division by zero",
                "Show how to verify the result is correct",
                "Optimise if the query takes seconds to run",
            ],
        },
        output_format={
            "ru": "Сначала допущения о данных, затем готовый запрос, затем пример входных данных и ожидаемый результат.",
            "en": "First the data assumptions, then the finished query, then sample input data and the expected result.",
        },
        asks_stack=True,
        stack_default={"ru": "PostgreSQL", "en": "PostgreSQL"},
    ),
    Profile.AUTOMATION: ProfileSpec(
        key=Profile.AUTOMATION,
        title={"ru": "Автоматизировать процесс", "en": "Automate a process"},
        role={
            "ru": "Ты - инженер по автоматизации, который делает процессы надёжными и идемпотентными.",
            "en": "You are an automation engineer who makes processes reliable and idempotent.",
        },
        requirements={
            "ru": [
                "Сделай скрипт идемпотентным и безопасным для повторного запуска",
                "Добавь логирование и понятные сообщения об ошибках",
                "Предусмотри таймауты и обработку сбоев",
                "Укажи, как запускать по расписанию",
            ],
            "en": [
                "Make the script idempotent and safe to re-run",
                "Add logging and clear error messages",
                "Handle timeouts and failures",
                "Explain how to schedule it",
            ],
        },
        output_format={
            "ru": "Сначала схема работы (что на входе, что на выходе), затем готовый скрипт, затем инструкция по запуску и пример вывода.",
            "en": "First the flow (inputs, outputs), then the finished script, then the run instructions and sample output.",
        },
        asks_stack=True,
        stack_default={"ru": "Python 3.11", "en": "Python 3.11"},
    ),
}


def get_profile(key: str | Profile) -> ProfileSpec | None:
    """Возвращает профиль по ключу или None, если ключ неизвестен."""
    if isinstance(key, ProfileSpec):
        return key
    if isinstance(key, Profile):
        return PROFILES[key]
    try:
        return PROFILES[Profile(key.strip().lower())]
    except (ValueError, AttributeError):
        return None
