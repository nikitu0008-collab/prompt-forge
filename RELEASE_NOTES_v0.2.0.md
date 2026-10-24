# Prompt Forge v0.2.0 — Release notes

Prompt Forge 0.2.0 расширяет исходный CLI до набора инструментов для создания структурированных промптов: новые форматы экспорта, пользовательские шаблоны, диагностика окружения, опциональное улучшение промпта через AI-провайдера и первая веб-версия.

## Добавлено

- `prompt-forge doctor` для базовой проверки окружения.
- Экспорт в YAML через `--format yaml`.
- Пользовательские шаблоны: `templates save`, `templates list`, `templates show`, `templates delete`.
- `--enhance` и слой провайдеров: OpenAI, OpenRouter, OpenAI-compatible API и Ollama.
- FastAPI endpoints для генерации, экспорта, шаблонов и AI-улучшения.
- Веб-интерфейс React + TypeScript + Vite.
- Руководство для Windows и GitHub Actions workflow для Python-тестов и frontend build.

## Совместимость и требования

- Python 3.10+.
- CLI и базовая генерация не требуют API-ключа.
- Облачное AI-улучшение требует собственного API-ключа и может тарифицироваться провайдером; Ollama может работать локально.
- Для запуска frontend в режиме разработки нужны Node.js и npm. Обычный CLI не зависит от Node.js.

## Установка из исходников

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,web]"
python -m pytest
```

## Известные ограничения

- Перед публикацией на PyPI необходимо отдельно проверить сборку wheel и sdist.
- Frontend и FastAPI запускаются отдельно; production-развёртывание требует настроить раздачу собранной frontend-статики или разнести frontend и API.
