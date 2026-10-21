# Changelog

Все значимые изменения проекта будут описаны в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [0.1.0] - 2026-10-21

### Добавлено

- CLI-утилита `prompt-forge` на Typer + Rich.
- Интерактивный визард: серия вопросов превращается в готовый промпт.
- Неинтерактивный режим `prompt-forge build` с полным набором аргументов.
- 11 профилей задач: code, feature, bugfix, refactor, test, architecture,
  review, learn, text, data, automation.
- Три уровня детализации: brief, standard, detailed.
- Два языка промпта: русский и английский.
- Форматы вывода: markdown, plain, json.
- Копирование в буфер обмена и сохранение промпта в файл.
- Тесты на pytest и CI-пайплайн (Python 3.10-3.12, Linux/Windows/macOS).
