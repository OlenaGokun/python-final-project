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


@pytest.mark.parametrize(
    ("token", "names", "expected"),
    [
        ("add", ["add-g", "add-c", "add-a", "add-f", "add-e", "add-b",
                 "add-a", "ad"], ["add-a", "add-b", "add-c", "add-e", "add-f", "add-g"]),
        ("help", ["yelp", "phelp", "helmet"], ["phelp"]),
        ("help", ["yelp", "held", "helm", "heap", "held",
                  "kelp", "helt", "hepl"], ["heap", "held", "helm", "helt", "hepl"]),
        ("zzzzzzzz", ["help"], []),
        ("help", [], []),
    ],
)
def test_suggest_commands(token, names, expected):
    from personal_helper import command_suggestions

    assert command_suggestions.suggest_commands(token, iter(names)) == expected
