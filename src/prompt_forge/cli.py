"""Точка входа CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prompt_forge import __version__
from prompt_forge.builder import build_bundle, build_prompt
from prompt_forge.console_setup import setup_console_encoding
from prompt_forge.examples import example_spec
from prompt_forge.i18n import t
from prompt_forge.models import Detail, Lang, OutputFormat, Profile, PromptSpec
from prompt_forge.output import copy_to_clipboard, render, save_to_file
from prompt_forge.profiles import PROFILES, get_profile
from prompt_forge.doctor import run_checks
from prompt_forge.providers import ProviderConfig, ProviderError, enhance_prompt
from prompt_forge.templates import delete_template, list_templates, load_template, save_template
from prompt_forge.wizard import PromptForgeError, RichPrompter, collect_spec

app = typer.Typer(
    name="prompt-forge",
    help="Генератор структурированных промптов для ИИ.",
    add_completion=False,
    no_args_is_help=False,
)

setup_console_encoding()

console = Console(stderr=True)
out_console = Console()


def _banner(lang: str) -> None:
    console.print(
        Panel(
            f"{t('app_tagline', lang)}\n"
            "[dim]введите ответ и нажмите Enter, Enter без ответа - оставить значение по умолчанию[/dim]",
            title=f"[bold cyan]{t('app_name', lang)}[/bold cyan] v{__version__}",
            border_style="cyan",
        )
    )


def _emit(spec: PromptSpec, fmt: OutputFormat, save: Path | None, do_copy: bool) -> None:
    text = render(spec, fmt)
    typer.echo(text)

    if do_copy:
        prompt_md = build_prompt(spec)
        if copy_to_clipboard(prompt_md):
            console.print(f"[green]OK[/green] {t('copied', spec.lang)}")
        else:
            console.print(f"[yellow]![/yellow] {t('copy_failed', spec.lang)}")

    if save is not None:
        try:
            path = save_to_file(save, text)
            console.print(f"[green]OK[/green] {t('saved', spec.lang, path=path)}")
        except OSError as error:
            console.print(f"[red]![/red] {t('saved_failed', spec.lang, error=error)}")


def _run_wizard(lang: str) -> None:
    _banner(lang)
    try:
        spec = collect_spec(RichPrompter())
    except PromptForgeError as error:
        console.print(f"[red]{error}[/red]")
        console.print(t("usage_hint", lang))
        raise typer.Exit(code=1) from error
    except (EOFError, KeyboardInterrupt):
        console.print("[yellow]Ввод прерван.[/yellow]")
        raise typer.Exit(code=1) from None
    _emit(spec, OutputFormat.MD, None, True)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Показать версию и выйти."),
    lang: Lang = typer.Option(Lang.RU, "--lang", "-l", help="Язык промпта."),
) -> None:
    """Prompt Forge - превращает ваше описание в грамотный промпт для ИИ."""
    setup_console_encoding()
    if version:
        typer.echo(f"prompt-forge {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        _run_wizard(lang.value)


@app.command()
def build(
    task: str = typer.Option(..., "--task", "-t", help="Описание задачи."),
    profile: Profile = typer.Option(Profile.CODE, "--profile", "-p", help="Тип задачи."),
    stack: str = typer.Option("", "--stack", "-s", help="Язык, библиотека или стек."),
    context: str = typer.Option("", "--context", "-c", help="Контекст: что уже есть и где это нужно."),
    requirement: list[str] = typer.Option([], "--require", "-r", help="Требование (можно указать несколько раз)."),
    input_spec: str = typer.Option("", "--input", "-i", help="Входные данные или интерфейс."),
    output_format: str = typer.Option("", "--output-format", "-f", help="Формат ответа."),
    acceptance: list[str] = typer.Option([], "--accept", "-a", help="Критерий готовности (можно несколько раз)."),
    example: list[str] = typer.Option([], "--example", "-e", help="Пример или краевой случай (можно несколько раз)."),
    constraint: list[str] = typer.Option([], "--constraint", "-n", help="Ограничение (можно несколько раз)."),
    audience: str = typer.Option("", "--audience", help="Для кого результат."),
    detail: Detail = typer.Option(Detail.STANDARD, "--detail", "-d", help="Детализация промпта."),
    lang: Lang = typer.Option(Lang.RU, "--lang", "-l", help="Язык промпта."),
    fmt: OutputFormat = typer.Option(OutputFormat.MD, "--format", help="Формат вывода: md, plain, json, yaml."),
    save: Path = typer.Option(None, "--save", help="Сохранить промпт в файл."),
    copy: bool = typer.Option(True, "--copy/--no-copy", help="Скопировать промпт в буфер обмена."),
    questions: bool = typer.Option(True, "--questions/--no-questions", help="Разрешить ИИ задать уточняющие вопросы."),
    enhance: bool = typer.Option(False, "--enhance", help="Улучшить готовый промпт через AI API."),
    provider: str = typer.Option(None, "--provider", help="openai-compatible, openai, openrouter или ollama; можно задать PROMPT_FORGE_PROVIDER."),
    model: str = typer.Option(None, "--model", help="Имя модели для --enhance; можно задать PROMPT_FORGE_MODEL."),
    base_url: str = typer.Option(None, "--base-url", help="Базовый URL API (необязательно)."),
) -> None:
    """Собрать промпт без интерактива - все данные через аргументы."""
    spec = PromptSpec(
        task=task.strip(),
        profile=profile,
        stack=stack.strip(),
        context=context.strip(),
        requirements=[item for item in requirement if item.strip()],
        input_spec=input_spec.strip(),
        output_format=output_format.strip(),
        acceptance=[item for item in acceptance if item.strip()],
        examples=[item for item in example if item.strip()],
        constraints=[item for item in constraint if item.strip()],
        audience=audience.strip(),
        detail=detail,
        lang=lang.value,
        allow_questions=questions,
    )
    if not spec.task:
        console.print(f"[red]{t('task_required', spec.lang)}[/red]")
        raise typer.Exit(code=1)
    if enhance:
        try:
            prompt = enhance_prompt(build_prompt(spec), ProviderConfig(provider=provider or os.getenv("PROMPT_FORGE_PROVIDER", "openai-compatible"), model=model or os.getenv("PROMPT_FORGE_MODEL", "gpt-4o-mini"), base_url=base_url or os.getenv("PROMPT_FORGE_BASE_URL"), api_key=os.getenv("PROMPT_FORGE_API_KEY")))
        except ProviderError as error:
            console.print(f"[red]Не удалось улучшить промпт: {error}[/red]")
            raise typer.Exit(code=2) from error
        typer.echo(prompt)
        if save is not None:
            try: console.print(f"[green]OK[/green] {t('saved', spec.lang, path=save_to_file(save, prompt))}")
            except OSError as error: raise typer.Exit(code=1) from error
        if copy and not copy_to_clipboard(prompt): console.print(f"[yellow]![/yellow] {t('copy_failed', spec.lang)}")
    else:
        _emit(spec, fmt, save, copy)


@app.command()
def profiles(
    lang: Lang = typer.Option(Lang.RU, "--lang", "-l", help="Язык описаний."),
    show: str = typer.Option("", "--show", help="Показать пример промпта для указанного профиля."),
) -> None:
    """Список доступных профилей задач."""
    if show:
        profile = get_profile(show)
        if profile is None:
            console.print(f"[red]{t('unknown_profile', lang.value, key=show)}[/red]")
            raise typer.Exit(code=1)
        spec = example_spec(profile.key, lang.value)
        typer.echo(build_prompt(spec))
        return

    table = Table(title=f"{t('app_name', lang.value)} - профили задач", title_justify="left")
    table.add_column("key", style="cyan", no_wrap=True)
    table.add_column("описание")
    table.add_column("стек", no_wrap=True)
    for profile in PROFILES:
        spec = get_profile(profile)
        if spec is None:
            continue
        table.add_row(profile.value, spec.label(lang.value), t("yes", lang.value) if spec.asks_stack else "-")
    out_console.print(table)
    console.print("[dim]prompt-forge profiles --show code[/dim]")


@app.command("json")
def json_command(
    task: str = typer.Option(..., "--task", "-t", help="Описание задачи."),
    profile: Profile = typer.Option(Profile.CODE, "--profile", "-p", help="Тип задачи."),
    lang: Lang = typer.Option(Lang.RU, "--lang", "-l", help="Язык промпта."),
) -> None:
    """Показать, как выглядит структура данных промпта в JSON."""
    spec = PromptSpec(task=task.strip(), profile=profile, lang=lang.value)
    typer.echo(json.dumps(build_bundle(spec), ensure_ascii=False, indent=2))


@app.command()
def doctor() -> None:
    """Проверить окружение, кодировку, PATH и компоненты."""
    checks = run_checks()
    table = Table(title="Prompt Forge — диагностика", title_justify="left")
    table.add_column("Проверка"); table.add_column("Статус"); table.add_column("Детали")
    for check in checks:
        table.add_row(check.name, "[green]OK[/green]" if check.ok else "[yellow]WARN[/yellow]", check.detail)
    out_console.print(table)
    if any(not item.ok and item.name == "Python" for item in checks): raise typer.Exit(code=1)


templates_app = typer.Typer(help="Сохранённые пользовательские шаблоны.")
app.add_typer(templates_app, name="templates")

@templates_app.command("list")
def templates_list() -> None:
    """Показать сохранённые шаблоны."""
    items = list_templates()
    if not items:
        console.print("Пока нет пользовательских шаблонов.")
        return
    for item in items: console.print(f"[cyan]{item['name']}[/cyan] — {item['path']}")

@templates_app.command("save")
def templates_save(name: str = typer.Argument(...), task: str = typer.Option(..., "--task"), profile: Profile = typer.Option(Profile.CODE, "--profile"), stack: str = typer.Option("", "--stack"), context: str = typer.Option("", "--context"), lang: Lang = typer.Option(Lang.RU, "--lang")) -> None:
    """Сохранить шаблон из основных полей."""
    path = save_template(name, PromptSpec(task=task, profile=profile, stack=stack, context=context, lang=lang.value))
    console.print(f"[green]Шаблон сохранён:[/green] {path}")

@templates_app.command("show")
def templates_show(name: str) -> None:
    """Вывести промпт из сохранённого шаблона."""
    try: typer.echo(build_prompt(load_template(name)))
    except (FileNotFoundError, ValueError) as error:
        console.print(f"[red]{error}[/red]"); raise typer.Exit(code=1) from error

@templates_app.command("delete")
def templates_delete(name: str) -> None:
    """Удалить пользовательский шаблон."""
    if not delete_template(name):
        console.print(f"[red]Шаблон не найден: {name}[/red]"); raise typer.Exit(code=1)
    console.print(f"[green]Удалён шаблон:[/green] {name}")

if __name__ == "__main__":  # pragma: no cover
    app()
