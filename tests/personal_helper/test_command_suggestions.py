import pytest


@pytest.mark.parametrize(
    ("token", "name", "expected"),
    [
        ("hep", "help", True),
        ("helpp", "help", True),
        ("hemp", "help", True),
        ("hepl", "help", True),
        ("hel", "help", True),
        ("elp", "help", True),
        ("help", "help", False),
        ("hmp", "help", False),
        ("hp", "help", False),
        ("pelh", "help", False),
        ("hlab", "help", False),
    ],
)
def test_one_edit_apart(token, name, expected):
    from personal_helper import command_suggestions

    assert command_suggestions.is_one_edit_apart(token, name) is expected
