"""Tests for output rendering, file saving, and clipboard fallbacks."""
import json
import sys

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
