# Prompt Forge

**Генератор структурированных промптов для ИИ — из вашего описания задачи.**

Думаете, как сформулировать запрос для ChatGPT / Claude / Copilot / Cursor?
Prompt Forge задаёт несколько уточняющих вопросов и собирает из них готовый,
грамотно оформленный промпт: с ролью, контекстом, требованиями, форматом ответа
и критериями готовности.

Работает полностью **офлайн**: никаких API-ключей, никаких запросов к внешним сервисам.

```bash
# самый быстрый способ (из исходников)
git clone https://github.com/nikitu0008-collab/prompt-forge.git
cd prompt-forge
python -m venv .venv
.venv\Scripts\activate          # Windows (cmd / PowerShell)
pip install -e .
prompt-forge --version          # проверка: должно вывести prompt-forge 0.1.0
```

> Если команда `prompt-forge` не найдена — загляните в раздел
> [«Команда не найдена»](#команда-не-найдена).
> В любом случае работает запасной вариант: `python -m prompt_forge ...` (PATH не нужен).

---

## Зачем это нужно

Формулизация «сделай мне калькулятор» — это не промпт. Это пожелание.
Модель додумает сама: какая логика, какие ошибки, какой формат вывода, какие тесты.

Prompt Forge превращает пожелание в **техническое задание для модели**:

| Вместо этого | Prompt Forge сделает так |
|---|---|
| «калькулятор на питоне» | Задача, роль, стек, обработка ошибок, формат ответа, критерии готовности |
| «почини баг» | Диагноз → первопричина → минимальный фикс → регрессионный тест → проверка |
| «напиши тесты» | Перечень покрытых сценариев: happy path, границы, краевые случаи, что каждый тест ловит |

Проект сделан для «вайбкодеров» — тех, кто пишет код с помощью ИИ и хочет,
чтобы каждый запрос попадал в цель с первого раза.

---

## Установка

Требования: **Python 3.10+**. Проверить: `python --version`.

### Вариант A. Из репозитория (рекомендуется)

```bash
git clone https://github.com/nikitu0008-collab/prompt-forge.git
cd prompt-forge

# 1. виртуальное окружение (обязательно: без него скрипт попадёт
#    в общие Scripts-каталоги и может не оказаться в PATH)
python -m venv .venv
.venv\Scripts\activate          # Windows (cmd / PowerShell)
source .venv/Scripts/activate   # Windows (Git Bash)
source .venv/bin/activate       # Linux / macOS

# 2. установка
pip install -e .

# 3. проверка
prompt-forge --version          # -> prompt-forge 0.1.0
```

### Вариант B. Из PyPI

> Пакет ещё не опубликован — следите за [#1](https://github.com/nikitu0008-collab/prompt-forge/issues/1).
> Как только выйдет релиз, установка будет такой:

```bash
pip install prompt-forge
prompt-forge --version
```

### Проверка установки

```bash
prompt-forge --version            # -> prompt-forge 0.1.0
python -m prompt_forge --version  # то же самое, но не зависит от PATH
```

Если обе команды отработали — всё в порядке, можно переходить к
[использованию](#использование).

### Команда не найдена

`CommandNotFoundException`, «не является именем cmdlet», `command not found` —
почти всегда означает одно: **скрипт установлен, но его каталог не в PATH**.

**Способ 1 (самый быстрый).** Запускайте через модуль — путь к скрипту не нужен:

```bash
python -m prompt_forge build --task "программа-калькулятор на Python, которая считает выражения"
```

**Способ 2. Windows: добавьте каталог скриптов в PATH.**

Узнать, где лежит скрипт:

```bash
python -c "import sysconfig, os; print(os.path.join(sysconfig.get_path('scripts')))"
```

Типичные варианты:

| Каталог | Когда появляется |
|---|---|
| `%APPDATA%\Python\Python3XX\Scripts` | `pip install --user` / установка в системный Python |
| `C:\Program Files\Python3XX\Scripts` | `pip install` в системный Python (обычно уже в PATH) |
| `venv\Scripts` | установка в виртуальное окружение (достаточно активации) |

Добавить в PATH (один раз, навсегда):

```powershell
[Environment]::SetEnvironmentVariable(
  'Path',
  [Environment]::GetEnvironmentVariable('Path','User') + ';C:\Users\<USER>\AppData\Roaming\Python\Python313\Scripts',
  'User'
)
```

После этого **закройте и откройте терминал заново** (PATH обновляется только в новых процессах) и проверьте:

```bash
where prompt-forge        # Windows
which prompt-forge        # Linux / macOS
prompt-forge --version
```

**Способ 3. Убедитесь, что активировано нужное окружение.**

```bash
# должно указывать на путь внутри проекта
python -c "import sys; print(sys.prefix)"
```

Если выводится путь к системному Python, а `.venv` в проекте пустой —
установите зависимости ещё раз:

```bash
.venv\Scripts\activate
pip install -e ".[dev]"
```

**Способ 4. Запуск прямо из скачанной папки, вообще без установки.**

```bash
# Linux / macOS
PYTHONPATH=src python -m prompt_forge build --task "..."

# Windows (PowerShell)
$env:PYTHONPATH="src"; python -m prompt_forge build --task "..."
```

### Заметки для Windows

- Кириллица в терминале: пакет сам переключает консоль на UTF-8
  (`SetConsoleOutputCP(65001)`). Если в вашем терминале всё равно «кракозябры» —
  выполните `chcp 65001` вручную или используйте Windows Terminal.
- Копирование в буфер обмена использует `clip.exe` (входит в состав Windows).
  Если буфер не заполняется, отключите копирование флагом `--no-copy`
  и используйте `--save prompt.md`.
- Служебные сообщения (`OK`, `!`) печатаются в stderr, сам промпт — в stdout.
  Если вы перенаправляете stderr (`2>nul`), вывод будет пустым.

---

## Использование

> Любую команду `prompt-forge ...` можно запустить как `python -m prompt_forge ...` —
> результат тот же, но не зависит от PATH.

### 1. Интерактивный режим

```bash
prompt-forge
```

Программа задаёт серию вопросов (описание задачи, тип, стек, контекст,
требования, формат ответа, критерии готовности, ограничения) и на выходе
даёт готовый промпт в терминале + в буфере обмена.

### 2. Неинтерактивный режим

```bash
prompt-forge build --task "программа-калькулятор на Python, которая считает выражения"
```

С параметрами:

```bash
prompt-forge build \
  --task "Калькулятор, вычисляющий выражения вида 2 + 2 * 3" \
  --profile code \
  --stack "Python 3.11, только стандартная библиотека" \
  --context "Пустой проект, запуск: python calculator.py" \
  --require "Не падать на некорректном вводе" \
  --accept "Есть тесты на деление на ноль" \
  --constraint "Без сторонних зависимостей" \
  --detail detailed \
  --save prompt.md
```

### 3. Форматы вывода

```bash
prompt-forge build --task "..." --format md      # markdown (по умолчанию)
prompt-forge build --task "..." --format plain   # обычный текст без разметки
prompt-forge build --task "..." --format json    # JSON со всей структурой
```

Флаг `--copy/--no-copy` управляет копированием в буфер обмена,
`--save путь` — сохранением в файл (UTF-8).

### 4. Профили задач

```bash
prompt-forge profiles              # список всех профилей
prompt-forge profiles --show code  # пример готового промпта для профиля
```

| Профиль | Для чего |
|---|---|
| `code` | Написать код с нуля |
| `feature` | Сделать фичу или доработку |
| `bugfix` | Найти первопричину и исправить баг |
| `refactor` | Упростить код без изменения поведения |
| `test` | Написать тесты |
| `architecture` | Спроектировать архитектуру и сравнить варианты |
| `review` | Провести код-ревью |
| `learn` | Разобраться в теме |
| `text` | Написать текст, статью, README |
| `data` | SQL и работа с данными |
| `automation` | Автоматизировать процесс |

### 5. Детализация и язык

```bash
prompt-forge build --task "..." --detail brief     # только суть
prompt-forge build --task "..." --detail standard  # по умолчанию
prompt-forge build --task "..." --detail detailed  # максимум деталей
prompt-forge build --task "..." --lang en          # промпт на английском
```

---

## Как выглядит результат

```markdown
Ниже описана задача. Отвечай строго в указанном формате, не добавляй лишних
объяснений и не отклоняйся от требований. Если условия противоречат друг другу
или чего-то критически не хватает - сначала задай не больше 3 уточняющих
вопросов, затем выполни задачу.

## Задача
Консольный калькулятор на Python: принимает выражение вида 2 + 2 * 3 и печатает результат

## Роль
Ты - опытный senior-разработчик, который пишет надёжный, идиоматичный и тестируемый код. Стек: Python 3.11, только стандартная библиотека.

## Контекст
Пустой проект, запускается как `python calculator.py`

## Требования
- Код должен быть корректным и сразу запускаемым
- Следуй идиомам выбранного стека, не тащи лишние зависимости
- Обрабатывай ошибки там, где это действительно нужно
- Добавь пример использования

## Формат ответа
Верни готовый код одним блоком с указанием языка, затем кратко: как это работает, как запустить, какие краевые случаи учтены.

## Критерии готовности
- Не падает на некорректном вводе
- Есть режим вычисления по цепочке `calc 1 + 2`
```

---

## Как устроен проект

```
src/prompt_forge/
├── __init__.py     версия пакета
├── __main__.py     python -m prompt_forge
├── cli.py          команды CLI (typer)
├── models.py       PromptSpec, Profile, Detail, OutputFormat
├── profiles.py     роли, требования и форматы ответа для каждого профиля
├── builder.py      сборка промпта из спецификации
├── wizard.py       интерактивные вопросы
├── examples.py     примеры спецификаций
├── output.py       буфер обмена, файл, форматы вывода
└── i18n.py         строки ru/en
```

## Разработка

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (cmd / PowerShell)
source .venv/Scripts/activate   # Windows (Git Bash)
source .venv/bin/activate       # Linux / macOS

pip install -e ".[dev]"
pytest
```

После активации `.venv` команда `prompt-forge` доступна сразу — в каталоге
`venv\Scripts` появляется `prompt-forge.exe`. Проверьте, что активено именно
нужное окружение: `python -c "import sys; print(sys.prefix)"`.

## Дорожная карта

Текущая цель — релиз **[v0.2.0](https://github.com/nikitu0008-collab/prompt-forge/milestone/1/overview)**
(декабрь 2026). Задачи ведутся в отдельных issue, чтобы было видно, над чем идёт работа.

- [x] **v0.1** — CLI, интерактивный визард, 11 профилей, ru/en
- [ ] **v0.2** — в работе:
  - [#1 Публикация пакета на PyPI](https://github.com/nikitu0008-collab/prompt-forge/issues/1)
  - [#2 Веб-версия (FastAPI + фронтенд)](https://github.com/nikitu0008-collab/prompt-forge/issues/2)
  - [#3 Пользовательские шаблоны промптов](https://github.com/nikitu0008-collab/prompt-forge/issues/3)
  - [#4 Экспорт промптов в JSON / YAML](https://github.com/nikitu0008-collab/prompt-forge/issues/4)
  - [#5 Режим `--enhance`: доработка промпта моделью](https://github.com/nikitu0008-collab/prompt-forge/issues/5)
  - Команда `doctor`: проверка окружения (PATH, версия Python, кодировка, буфер обмена)
  - Гайд по установке на Windows: PATH, `chcp 65001`, типичные ошибки
- [ ] **v0.3+** — плагины под конкретные модели и IDE, расширение для VS Code / Cursor

## Лицензия

MIT — см. [LICENSE](LICENSE).
