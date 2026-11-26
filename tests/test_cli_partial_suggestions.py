import pytest


ADD_MATCHES = (
    "add-birthday, add-contact, add-email, add-note, add-note-tags, add-phone"
)


@pytest.mark.parametrize("include_address", [True, False])
def test_add_returns_every_match(cli_turns, registry, include_address):
    if not include_address:
        registry.commands.pop("add-address")
        registry.commands.pop("delete-address")
    expected = f"add-address, {ADD_MATCHES}, delete-address" if include_address else ADD_MATCHES

    assert cli_turns(["add", "exit"]) == [
        ["Invalid command.", f"Did you mean: {expected}?"]
    ]


def test_partial_and_uppercase_names(cli_turns):
    birthday = [
        "Invalid command.",
        "Did you mean: add-birthday, delete-birthday, show-birthday, show-birthdays?",
    ]
    birthday_typo = ["Invalid command.", "Did you mean: show-birthdays?"]
    assert cli_turns([
        "birthday", "BIRTHDAY", "show-all-c", "show-birthdayss", "SHOW-BIRTHDAYSS", "exit"
    ]) == [
        birthday,
        birthday,
        ["Invalid command.", "Did you mean: show-all-contacts?"],
        birthday_typo,
        birthday_typo,
    ]
