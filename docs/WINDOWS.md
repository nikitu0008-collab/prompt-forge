# Установка Prompt Forge в Windows

## 1. Установите Python

Установите Python 3.10 или новее с официального сайта https://www.python.org/downloads/windows/. В установщике включите **Add python.exe to PATH**. Откройте новое окно PowerShell и проверьте:

```powershell
py --version
python --version
```

Если `python` не найден, используйте `py -m pip` или повторно запустите установщик Python и включите PATH.

## 2. Установите пакет

```powershell
py -m pip install --upgrade pip
py -m pip install prompt-forge
prompt-forge --version
```

Если команда `prompt-forge` не найдена, закройте и снова откройте терминал. Убедитесь, что каталог Scripts вашей установки Python находится в PATH. Его можно узнать так:

```powershell
py -c "import sysconfig; print(sysconfig.get_path('scripts'))"
```

## 3. Кодировка консоли

Prompt Forge настраивает UTF-8 при запуске. Если в старом терминале русские символы отображаются некорректно, выполните:

```powershell
chcp 65001
$env:PYTHONUTF8 = "1"
```

Windows Terminal и актуальный PowerShell обычно лучше обрабатывают UTF-8, чем старый `cmd.exe`.

## 4. Проверка окружения

```powershell
prompt-forge doctor
prompt-forge profiles
prompt-forge build --task "Создать REST API" --stack "Python, FastAPI" --format md --no-copy
```

## 5. Улучшение промптов через AI

Для облачного OpenAI-compatible API задайте ключ в текущем окне PowerShell:

```powershell
$env:PROMPT_FORGE_API_KEY = "ваш-api-ключ"
$env:PROMPT_FORGE_PROVIDER = "openai-compatible"
$env:PROMPT_FORGE_MODEL = "gpt-4o-mini"
prompt-forge build --task "Создать REST API" --enhance --no-copy
```

Не вставляйте ключ в публичные репозитории и не добавляйте его в исходники. Для OpenRouter используйте `--provider openrouter`, для локальной Ollama — `--provider ollama --model llama3.2`; при необходимости укажите `--base-url`.

## 6. Веб-приложение из репозитория

```powershell
py -m pip install -e ".[web]"
uvicorn prompt_forge.web:app --reload
```

В другом окне терминала:

```powershell
cd web/frontend
npm install
npm run dev
```

Откройте адрес, который напечатает Vite (обычно http://localhost:5173). Vite проксирует `/api` на FastAPI по адресу `http://127.0.0.1:8000`.

## Частые проблемы

- **`No module named prompt_forge`**: в каталоге репозитория выполните `py -m pip install -e ".[dev,web]"`.
- **`prompt-forge` не найден**: откройте новый терминал, проверьте каталог Scripts и PATH.
- **Ошибка ключа при `--enhance`**: установите `PROMPT_FORGE_API_KEY`; для локальной Ollama ключ не нужен.
- **Ошибка подключения к Ollama**: запустите Ollama и проверьте `http://localhost:11434`.
- **Копирование не работает**: проверьте доступность системного буфера обмена; используйте `--no-copy`.
- **Порт занят**: запустите `uvicorn prompt_forge.web:app --port 8001` и настройте proxy Vite на этот порт.
