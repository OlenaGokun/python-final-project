import pytest

from personal_helper.models import Record


@pytest.mark.parametrize(
    ("token", "first"),
    [
        ("show-all-contatcs", "show-all-contacts"),
        ("show-all-notse", "show-all-notes"),
        ("show-birthdayss", "show-birthdays"),
    ],
)
def test_reference_typos(cli_turns, token, first):
    turns = cli_turns([token, "exit"])
    assert turns[0][0] == "Invalid command."
    assert len(turns[0]) == 2
    suggestions = turns[0][1].removeprefix("Did you mean: ").removesuffix("?")
    assert suggestions.split(", ")[0] == first


@pytest.mark.parametrize("with_birthday", [True, False])
def test_birthday_tie_uses_names_only(cli_turns, data, with_birthday):
    if with_birthday:
        record = Record("Birthday Contact")
        record.add_birthday("01.01.2000")
        data.address_book.add_record(record)

    assert cli_turns(["show-birthdayx", "exit"]) == [
        ["Invalid command.", "Did you mean: show-birthday, show-birthdays?"]
    ]


def test_help_only_registry_checks_all_four_edit_types(cli_turns, registry):
    help_command = registry.get_command("help")
    registry.commands = {"help": help_command}

    assert cli_turns(["hep", "helpp", "hemp", "hepl", "hmp"]) == [
        *[["Invalid command.", "Did you mean: help?"]] * 4,
        ["Invalid command."],
    ]
