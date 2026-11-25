"""Shared pytest fixtures for all tests"""

import pytest
from personal_helper.models import AddressBook, PersonalHelper, Record
from personal_helper.command_registry import CommandRegistry


@pytest.fixture
def book():
    """Create a fresh address book for each test"""
    return AddressBook()


@pytest.fixture
def data():
    return PersonalHelper()


@pytest.fixture
def registry():
    """Create command registry"""
    return CommandRegistry()


@pytest.fixture
def book_with_contacts(book):
    """Create book with sample data"""
    record1 = Record("John")
    record1.add_phone("5012345671")  # 10 digits as string
    record1.add_birthday("25.12.1990")
    book.add_record(record1)

    record2 = Record("Alice")
    record2.add_phone("5098765432")  # 10 digits as string
    book.add_record(record2)

    return book


@pytest.fixture
def cli_turns(monkeypatch, capsys, registry, data):
    """Capture the output between successive CLI command prompts."""
    from main import main

    class EndSession(Exception):
        pass

    monkeypatch.setattr("main.CommandRegistry", lambda: registry)
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", lambda data: None)

    def run(submissions):
        inputs = iter(submissions)
        turns = []

        def read(prompt):
            assert prompt == "Enter a command: "
            turns.append(capsys.readouterr().out.splitlines())
            try:
                return next(inputs)
            except StopIteration:
                raise EndSession from None

        monkeypatch.setattr("builtins.input", read)
        if "exit" in registry.commands:
            main()
            assert capsys.readouterr().out.strip() == "Good bye!"
        else:
            with pytest.raises(EndSession):
                main()

        return turns[1:]

    return run
