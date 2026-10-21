"""Готовые примеры спецификаций - используются в `prompt-forge profiles --show`."""

from __future__ import annotations

from prompt_forge.models import Detail, Profile, PromptSpec

_EXAMPLES: dict[Profile, dict[str, dict]] = {
    Profile.CODE: {
        "ru": {
            "task": "Консольный калькулятор на Python: принимает выражение вида 2 + 2 * 3 и печатает результат",
            "stack": "Python 3.11, только стандартная библиотека",
            "context": "Пустой проект, запускается как `python calculator.py`",
            "acceptance": ["Не падает на некорректном вводе", "Есть режим вычисления по цепочке `calc 1 + 2`"],
        },
        "en": {
            "task": "A console calculator in Python: accepts an expression like 2 + 2 * 3 and prints the result",
            "stack": "Python 3.11, standard library only",
            "context": "Empty project, runs as `python calculator.py`",
            "acceptance": ["Does not crash on invalid input", "Supports chained evaluation `calc 1 + 2`"],
        },
    },
    Profile.FEATURE: {
        "ru": {
            "task": "Добавить в CLI команду `export`, которая выгружает текущий список задач в JSON",
            "stack": "Python 3.11 + Typer",
            "context": "Уже есть команды `add`, `list`, `done` на Typer",
            "acceptance": ["Файл export.json создаётся в рабочей директории", "Пустой список тоже выгружается"],
        },
        "en": {
            "task": "Add an `export` command to the CLI that dumps the current task list to JSON",
            "stack": "Python 3.11 + Typer",
            "context": "There are already `add`, `list` and `done` commands built with Typer",
            "acceptance": ["export.json is created in the working directory", "An empty list is still exported"],
        },
    },
    Profile.BUGFIX: {
        "ru": {
            "task": "В списке задач неверно считается общее время: задачи перекрываются и сумма завышена",
            "stack": "Python 3.11",
            "context": "Расчёт в функции `total_hours(tasks)`, пересечение интервалов не обрабатывается",
            "acceptance": ["Перекрывающиеся интервалы считаются один раз", "Есть тест на пересечение"],
        },
        "en": {
            "task": "Total time in the task list is miscalculated: overlapping tasks inflate the sum",
            "stack": "Python 3.11",
            "context": "Calculated in `total_hours(tasks)`, overlapping intervals are not handled",
            "acceptance": ["Overlapping intervals are counted once", "There is a test for the overlap case"],
        },
    },
    Profile.REFACTOR: {
        "ru": {
            "task": "Разбить монолитный модуль `report.py` (800 строк) на пакет с логикой, рендерером и CLI",
            "stack": "Python 3.11",
            "context": "Публичные функции используются в трёх других модулях",
            "acceptance": ["Публичный API не изменился", "Каждый новый модуль меньше 300 строк"],
        },
        "en": {
            "task": "Split the 800-line `report.py` monolith into a package with logic, renderer and CLI",
            "stack": "Python 3.11",
            "context": "Public functions are used in three other modules",
            "acceptance": ["The public API is unchanged", "Every new module is under 300 lines"],
        },
    },
    Profile.TEST: {
        "ru": {
            "task": "Покрыть тестами модуль парсинга конфигурации: YAML, TOML и JSON",
            "stack": "Python 3.11 + pytest",
            "context": "Модуль `config_loader.py`, тестов пока нет",
            "acceptance": ["Есть happy path, ошибочный формат и пустой файл", "Тесты не зависят от реальной файловой системы"],
        },
        "en": {
            "task": "Cover the config parsing module with tests: YAML, TOML and JSON",
            "stack": "Python 3.11 + pytest",
            "context": "Module `config_loader.py`, there are no tests yet",
            "acceptance": ["Happy path, broken format and empty file are covered", "Tests do not depend on the real file system"],
        },
    },
    Profile.ARCHITECTURE: {
        "ru": {
            "task": "Спроектировать систему сбора метрик с приложений: агенты, очередь, хранилище",
            "stack": "Python 3.11, Kubernetes",
            "context": "Ожидаем до 50 000 событий в секунду, нужны дашборды и ретенция 30 дней",
            "acceptance": ["Схема компонентов и их контракты", "Обоснование выбора хранилища"],
        },
        "en": {
            "task": "Design a metrics collection system for applications: agents, queue, storage",
            "stack": "Python 3.11, Kubernetes",
            "context": "Up to 50,000 events per second, dashboards and 30 days retention required",
            "acceptance": ["Component schema and their contracts", "Justified choice of the storage engine"],
        },
    },
    Profile.REVIEW: {
        "ru": {
            "task": "Провести ревью модуля оплаты перед релизом",
            "stack": "Python 3.11 + FastAPI",
            "context": "PR меняет логику списания денег и добавляет вебхуки",
            "acceptance": ["Блокеры отделены от мелочей", "Для каждого замечания есть предложенный фикс"],
        },
        "en": {
            "task": "Review the payments module before the release",
            "stack": "Python 3.11 + FastAPI",
            "context": "The PR changes the money charging logic and adds webhooks",
            "acceptance": ["Blockers are separated from nits", "Every issue comes with a suggested fix"],
        },
    },
    Profile.LEARN: {
        "ru": {
            "task": "Объяснить, как работает async/await в Python и чем отличается от потоков",
            "stack": "Python 3.11",
            "context": "Ученик знает обычные функции, но не знает про event loop",
            "acceptance": ["Есть пример кода и объяснение каждой строки", "Есть упражнения для практики"],
        },
        "en": {
            "task": "Explain how async/await works in Python and how it differs from threads",
            "stack": "Python 3.11",
            "context": "The learner knows regular functions but not the event loop",
            "acceptance": ["There is a code example with every line explained", "There are practice exercises"],
        },
    },
    Profile.TEXT: {
        "ru": {
            "task": "Написать README для open-source CLI-утилиты на Python",
            "stack": "",
            "context": "Аудитория - новички, тон дружелюбный, без маркетинговых формулировок",
            "acceptance": ["Есть пример установки и запуска", "Объём до 1200 слов"],
        },
        "en": {
            "task": "Write a README for an open-source Python CLI tool",
            "stack": "",
            "context": "The audience is beginners, the tone is friendly and free of marketing wording",
            "acceptance": ["There is an install and run example", "Under 1200 words"],
        },
    },
    Profile.DATA: {
        "ru": {
            "task": "Собрать SQL-запрос: топ-10 клиентов по выручке за последний месяц",
            "stack": "PostgreSQL",
            "context": "Таблицы `orders(id, client_id, amount, created_at)` и `clients(id, name)`",
            "acceptance": ["Учтены возвраты и пустые заказы", "Запрос работает на PostgreSQL 14"],
        },
        "en": {
            "task": "Build an SQL query: top-10 clients by revenue for the last month",
            "stack": "PostgreSQL",
            "context": "Tables `orders(id, client_id, amount, created_at)` and `clients(id, name)`",
            "acceptance": ["Refunds and empty orders are taken into account", "The query runs on PostgreSQL 14"],
        },
    },
    Profile.AUTOMATION: {
        "ru": {
            "task": "Скрипт, который каждую ночь выгружает бэкап PostgreSQL в S3 и удаляет старые копии",
            "stack": "Python 3.11",
            "context": "Нужно запускать по расписанию в 3:00, хранить копии 7 дней",
            "acceptance": ["Повторный запуск в тот же день не ломает выгрузку", "Есть логирование и коды возврата"],
        },
        "en": {
            "task": "A script that dumps a PostgreSQL backup to S3 every night and prunes old copies",
            "stack": "Python 3.11",
            "context": "It must run on a schedule at 3:00 and keep copies for 7 days",
            "acceptance": ["A second run on the same day does not break the export", "There is logging and exit codes"],
        },
    },
}


def example_spec(profile: Profile, lang: str = "ru") -> PromptSpec:
    """Возвращает готовую спецификацию-пример для профиля."""
    data = _EXAMPLES.get(profile, {}).get(lang) or _EXAMPLES.get(profile, {}).get("ru") or {}
    return PromptSpec(
        task=data.get("task", ""),
        profile=profile,
        stack=data.get("stack", ""),
        context=data.get("context", ""),
        acceptance=data.get("acceptance", []),
        detail=Detail.DETAILED,
        lang=lang,
    )
