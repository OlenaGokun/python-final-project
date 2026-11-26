import pytest
import io

from colorama import Fore, Style

from personal_helper.core import formatting
from personal_helper.models import Record


@pytest.mark.parametrize("answer", [" Y ", "yEs", " N ", "nO"])
def test_delete_contact_requires_explicit_confirmation(
    registry, data, monkeypatch, answer
):
    original = data.address_book.add_record(Record("Mary Jane"))
    prompts = []

    def confirm(prompt):
        assert data.address_book["Mary Jane"] is original
        prompts.append(prompt)
        return answer

    monkeypatch.setattr("builtins.input", confirm)
    result = registry.get_command("delete-contact").run(
        ["--name", "mary", "jane"], data
    )

    assert len(prompts) == 1
    assert "Mary Jane" in prompts[0] and "(Y)es/(N)o" in prompts[0]
    affirmative = answer.strip().casefold().startswith("y")
    assert (data.address_book.find("Mary Jane") is None) == affirmative
    assert ("deleted" if affirmative else "canceled") in result


def test_delete_missing_contact_does_not_prompt(registry, data, monkeypatch):
    monkeypatch.setattr(
        "builtins.input", lambda _: pytest.fail("Unexpected prompt")
    )
    result = registry.get_command("delete-contact").run(
        ["--name", "Missing"], data
    )
    assert "not found" in result


@pytest.mark.parametrize("interruption", [EOFError, KeyboardInterrupt])
def test_delete_contact_reprompts_then_cancels(
    registry, data, monkeypatch, capsys, interruption
):
    original = data.address_book.add_record(Record("Mary Jane"))
    answers = iter(["", "maybe", interruption])

    def confirm(_prompt):
        assert data.address_book["Mary Jane"] is original
        answer = next(answers)
        if answer is interruption:
            raise interruption
        return answer

    monkeypatch.setattr("builtins.input", confirm)
    result = registry.get_command("delete-contact").run(
        ["--name", "Mary", "Jane"], data
    )

    assert result == "Contact deletion canceled."
    assert data.address_book["Mary Jane"] is original
    assert capsys.readouterr().out.count("Please enter yes or no.") == 2


def test_delete_contact_colors_invalid_confirmation(
    registry, data, monkeypatch
):
    class Terminal(io.StringIO):
        def isatty(self):
            return True

    terminal = Terminal()
    data.address_book.add_record(Record("Mary Jane"))
    answers = iter(["maybe", "no"])
    monkeypatch.setattr(formatting.sys, "stdout", terminal)
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = registry.get_command("delete-contact").run(
        ["--name", "Mary Jane"], data
    )

    assert result == "Contact deletion canceled."
    assert (
        terminal.getvalue()
        == f"{Fore.RED}Please enter yes or no.{Style.RESET_ALL}\n"
    )
