"""Tests for output rendering, file saving, and clipboard fallbacks."""
import pytest
import json
import sys
import prompt_forge.output as output_module

from prompt_forge.models import OutputFormat, PromptSpec
from prompt_forge.output import copy_to_clipboard, render, save_to_file

def test_render_json_is_valid_json():
    result = json.loads(render(PromptSpec(task="JSON task"), OutputFormat.JSON))
    assert "JSON task" in result["prompt"]


def test_render_plain_returns_plain_output():
    result = render(PromptSpec(task="Plain task"), OutputFormat.PLAIN)
    assert isinstance(result, str)
    assert "Plain task" in result


def test_render_markdown_returns_prompt():
    result = render(PromptSpec(task="Markdown task"), OutputFormat.MD)
    assert "Markdown task" in result


def test_render_yaml_returns_yaml():
    result = render(PromptSpec(task="YAML task"), OutputFormat.YAML)
    assert "prompt:" in result
    assert "YAML task" in result


def test_save_to_file_creates_parent_directories(tmp_path):
    target = tmp_path / "nested" / "prompt.md"
    returned = save_to_file(target, "content")
    assert returned == target
    assert target.read_text(encoding="utf-8") == "content"


def test_copy_to_clipboard_returns_true_when_pyperclip_succeeds(monkeypatch):
    class FakePyperclip:
        @staticmethod
        def copy(text):
            assert text == "hello"
    monkeypatch.setitem(sys.modules, "pyperclip", FakePyperclip)
    assert copy_to_clipboard("hello") is True


def test_copy_to_clipboard_returns_false_when_no_backend(monkeypatch):
    class BrokenPyperclip:
        @staticmethod
        def copy(text):
            raise RuntimeError("clipboard unavailable")
    monkeypatch.setitem(sys.modules, "pyperclip", BrokenPyperclip)
    monkeypatch.setattr("prompt_forge.output.shutil.which", lambda command: None)
    assert copy_to_clipboard("hello") is False

def test_copy_to_clipboard_uses_system_fallback(monkeypatch):
    class BrokenPyperclip:
        @staticmethod
        def copy(text):
            raise RuntimeError("clipboard unavailable")

    monkeypatch.setitem(sys.modules, "pyperclip", BrokenPyperclip)
    monkeypatch.setattr(output_module.sys, "platform", "win32")
    monkeypatch.setattr(output_module.shutil, "which", lambda command: "clip.exe")

    def fake_run(command, input, check):
        assert command == ["clip"]
        assert input == b"hello"
        assert check is True

    monkeypatch.setattr(output_module.subprocess, "run", fake_run)

    assert copy_to_clipboard("hello") is True


def test_copy_to_clipboard_returns_false_when_system_command_fails(monkeypatch):
    class BrokenPyperclip:
        @staticmethod
        def copy(text):
            raise RuntimeError("clipboard unavailable")

    monkeypatch.setitem(sys.modules, "pyperclip", BrokenPyperclip)
    monkeypatch.setattr(output_module.sys, "platform", "win32")
    monkeypatch.setattr(output_module.shutil, "which", lambda command: "clip.exe")

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "clip")

    monkeypatch.setattr(output_module.subprocess, "run", fake_run)

    assert copy_to_clipboard("hello") is False


def test_save_to_file_raises_when_write_fails(monkeypatch, tmp_path):
    target = tmp_path / "prompt.md"

    def fake_write_text(*args, **kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(output_module.Path, "write_text", fake_write_text)

    with pytest.raises(OSError, match="disk unavailable"):
        save_to_file(target, "content")


def test_render_yaml_raises_when_pyyaml_is_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "yaml", None)

    with pytest.raises(RuntimeError, match="PyYAML"):
        render(PromptSpec(task="YAML task"), OutputFormat.YAML)


def test_render_unknown_format_returns_prompt():
    class UnknownFormat:
        value = "unknown"

    result = render(PromptSpec(task="Unknown format task"), UnknownFormat())

    assert "Unknown format task" in result

@pytest.mark.parametrize(
    ("platform", "expected_command"),
    [
        ("darwin", ["pbcopy"]),
        ("linux", ["xclip", "-selection", "clipboard"]),
    ],
)
def test_copy_to_clipboard_uses_platform_fallback(
    monkeypatch,
    platform,
    expected_command,
):
    class BrokenPyperclip:
        @staticmethod
        def copy(text):
            raise RuntimeError("clipboard unavailable")

    monkeypatch.setitem(sys.modules, "pyperclip", BrokenPyperclip)
    monkeypatch.setattr(output_module.sys, "platform", platform)
    monkeypatch.setattr(
        output_module.shutil,
        "which",
        lambda command: "/usr/bin/" + command,
    )

    def fake_run(command, input, check):
        assert command == expected_command
        assert input == b"hello"
        assert check is True

    monkeypatch.setattr(output_module.subprocess, "run", fake_run)

    assert copy_to_clipboard("hello") is True
