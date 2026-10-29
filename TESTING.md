# Testing Prompt Forge

## Install development and web dependencies

```bash
python -m pip install -e ".[dev,web]"
```

## Run the full test suite

```bash
python -m pytest -v
```

## Run tests with coverage

```bash
python -m pytest --cov=prompt_forge --cov-report=term-missing
```

## Run a focused test module

```bash
python -m pytest tests/test_providers.py -v
python -m pytest tests/test_templates.py -v
python -m pytest tests/test_web_api.py -v
python -m pytest tests/test_output.py -v
```

Tests use mocked HTTP responses and temporary directories, so they do not require a real AI API key or modify the user's saved templates.
