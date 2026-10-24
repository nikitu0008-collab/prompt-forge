# Prompt Forge

**Генератор структурированных промптов для ИИ — из описания задачи в готовое техническое задание для модели.**

Prompt Forge помогает формулировать точные запросы для ChatGPT, Claude, Copilot, Cursor и других ИИ-инструментов. Он собирает задачу, роль, контекст, требования, формат ответа и критерии готовности в один структурированный промпт.

**Версия:** `0.2.0` · **Язык интерфейса:** русский и английский · **Лицензия:** MIT

> Обычная генерация работает локально и не требует API-ключа. ИИ-улучшение (`--enhance`) отправляет промпт выбранному провайдеру и требует его API-доступа, кроме локальной Ollama.

## Что нового в 0.2.0

- **Веб-API на FastAPI** и интерфейс на React + TypeScript.
- **`--enhance`** — улучшение готового промпта через OpenAI, OpenRouter, OpenAI-compatible API или Ollama.
- **Пользовательские шаблоны** — сохраняйте, просматривайте, используйте и удаляйте шаблоны.
- **Экспорт YAML** наряду с Markdown, обычным текстом и JSON.
- **`doctor`** — базовая диагностика окружения.
- **Руководство для Windows** и CI workflow для тестов Python и сборки фронтенда.

## Возможности

- Интерактивный визард и неинтерактивная CLI-команда.
- 11 профилей задач: `code`, `feature`, `bugfix`, `refactor`, `test`, `architecture`, `review`, `learn`, `text`, `data`, `automation`.
- Уровни детализации `brief`, `standard`, `detailed`.
- Русский и английский языки.
- Копирование в буфер обмена и сохранение результата в файл.
- Форматы вывода: `md`, `plain`, `json`, `yaml`.
- CLI и веб-API используют общую логику генерации.

## Требования

- Python 3.10 или новее.
- Для веб-интерфейса в режиме разработки: Node.js и npm.
- Для `--enhance` с облачной моделью: API-ключ и доступ к выбранному провайдеру. Ollama требует установленного и запущенного локального сервера и скачанной модели.

## Установка из GitHub

### Windows (PowerShell)

```powershell
git clone https://github.com/nikitu0008-collab/prompt-forge.git
cd prompt-forge
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,web]"
prompt-forge --version
```

Если PowerShell сообщает, что выполнение скриптов запрещено, можно не менять Execution Policy, а запускать npm через `npm.cmd` (см. раздел «Веб-интерфейс»). Для Python-команд при необходимости используйте `python -m prompt_forge` вместо `prompt-forge`.

### Linux / macOS

```bash
git clone https://github.com/nikitu0008-collab/prompt-forge.git
cd prompt-forge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,web]"
prompt-forge --version
```

## Использование CLI

### Интерактивный режим

```bash
prompt-forge
```

### Сгенерировать промпт

```bash
prompt-forge build --task "Создать музыкальный плеер на Rust" --profile code
```

### Форматы экспорта

```bash
prompt-forge build --task "Создать REST API" --format md --save prompt.md
prompt-forge build --task "Создать REST API" --format plain --save prompt.txt
prompt-forge build --task "Создать REST API" --format json --save prompt.json
prompt-forge build --task "Создать REST API" --format yaml --save prompt.yaml
```

### Более подробное описание задачи

```powershell
prompt-forge build `
  --task "Создать музыкальный плеер на Rust" `
  --profile code `
  --stack "Rust, Cargo" `
  --context "Windows 11, существующий проект" `
  --require "Обрабатывать ошибки чтения файлов" `
  --accept "Есть unit-тесты" `
  --detail detailed `
  --save prompt.md
```

В PowerShell символ продолжения строки — обратный апостроф `` ` ``. В CMD или Bash многострочный пример нужно адаптировать под соответствующую оболочку; проще запускать команду одной строкой.

### Профили и диагностика

```bash
prompt-forge profiles
prompt-forge profiles --show code
prompt-forge doctor
```

### Пользовательские шаблоны

```bash
prompt-forge templates save rust-app --task "Создать приложение на Rust" --profile code --stack "Rust, Cargo"
prompt-forge templates list
prompt-forge templates show rust-app
prompt-forge templates delete rust-app
```

## ИИ-улучшение промптов

Без флага `--enhance` проект не вызывает внешние ИИ-сервисы. Для улучшения через облачный провайдер настройте переменные окружения. Не записывайте секреты в исходный код и не коммитьте их в Git.

### OpenAI

PowerShell (только для текущего окна терминала):

```powershell
$env:PROMPT_FORGE_PROVIDER = "openai"
$env:PROMPT_FORGE_MODEL = "gpt-4o-mini"
$env:PROMPT_FORGE_API_KEY = "YOUR_API_KEY"
prompt-forge build --task "Создать CLI на Python" --enhance
```

### OpenRouter

```powershell
$env:PROMPT_FORGE_PROVIDER = "openrouter"
$env:PROMPT_FORGE_MODEL = "openai/gpt-4o-mini"
$env:PROMPT_FORGE_API_KEY = "YOUR_API_KEY"
prompt-forge build --task "Создать CLI на Python" --enhance
```

### OpenAI-compatible API

Укажите провайдера, базовый URL, модель и ключ:

```powershell
$env:PROMPT_FORGE_PROVIDER = "openai-compatible"
$env:PROMPT_FORGE_BASE_URL = "https://your-provider.example/v1"
$env:PROMPT_FORGE_MODEL = "your-model"
$env:PROMPT_FORGE_API_KEY = "YOUR_API_KEY"
prompt-forge build --task "Создать CLI на Python" --enhance
```

Универсальный адаптер ожидает совместимый с OpenAI Chat Completions API endpoint. Адрес и название модели зависят от выбранного провайдера.

### Ollama (локальная модель)

Установите Ollama, скачайте модель и запустите локальный сервер. Затем настройте, например:

```powershell
$env:PROMPT_FORGE_PROVIDER = "ollama"
$env:PROMPT_FORGE_BASE_URL = "http://localhost:11434"
$env:PROMPT_FORGE_MODEL = "llama3.2"
prompt-forge build --task "Создать CLI на Python" --enhance
```

Для облачных провайдеров может взиматься плата согласно тарифам провайдера. Prompt Forge не включает API-кредиты. В текущей веб-версии ключ для ИИ читается сервером из переменной окружения `PROMPT_FORGE_API_KEY`; не помещайте ключ в frontend-код или публичные файлы.

## Веб-интерфейс

Установите Python-зависимости проекта командой `python -m pip install -e ".[web]"`, затем запустите API из корня репозитория:

```powershell
python -m uvicorn prompt_forge.web:app --reload
```

API будет доступно по адресу `http://127.0.0.1:8000`, документация API — `http://127.0.0.1:8000/docs`.

Для запуска React-интерфейса в режиме разработки откройте **второе** окно терминала:

```powershell
cd web/frontend
npm.cmd install
npm.cmd run dev
```

Откройте адрес, который напечатает Vite (обычно `http://localhost:5173`). На Windows `npm.cmd` можно использовать вместо `npm`, если PowerShell блокирует файл `npm.ps1` политикой выполнения скриптов.

Для проверки production-сборки фронтенда:

```powershell
npm.cmd run build
```

Сборка создаётся в `web/frontend/dist`. В текущей конфигурации frontend и FastAPI запускаются отдельно; production-развёртывание веб-версии требует настроить отдачу собранной статики или разместить frontend и API отдельно. Обычный CLI от Node.js/npm не зависит.

## Разработка и тесты

```bash
python -m pip install -e ".[dev,web]"
python -m pytest
```

Для фронтенда:

```bash
cd web/frontend
npm install
npm run build
```

CI workflow запускает Python-тесты на Python 3.10–3.13 и проверяет сборку фронтенда.

## Структура проекта

```text
src/prompt_forge/   ядро, CLI, шаблоны, провайдеры и FastAPI
web/frontend/      React + TypeScript + Vite
 tests/             тесты Python
 docs/WINDOWS.md    инструкция для Windows
 .github/workflows/ GitHub Actions CI
```

## Статус проекта

`0.2.0` — версия с расширением CLI и первой веб-реализацией. Перед публикацией пакета на PyPI необходимо подтвердить сборку wheel/sdist и установку из артефактов. До появления опубликованного релиза устанавливайте проект из GitHub.

## Безопасность

- Не добавляйте реальные API-ключи, токены или `.env` в коммиты.
- Для облачного `--enhance` текст промпта отправляется выбранному AI-провайдеру. Не передавайте конфиденциальные данные, если это не разрешено политикой вашей организации.
- Локальная генерация без `--enhance` не требует передачи промпта внешней модели.

## Лицензия

MIT. См. [`LICENSE`](LICENSE).
