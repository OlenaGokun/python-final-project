import pytest

from personal_helper.core.data import parse_input, parse_options
from personal_helper.core.exceptions import InvalidInputError


def test_parse_input_and_options_preserve_unquoted_multiword_values():
    command, *args = parse_input("  ADD   --phone  0123456789 --name  Mary  Jane ")
    assert command == "add"
    assert parse_options(
        args, {"--name", "--phone"}, {"--name"}, "usage", {"--phone"}
    ) == {"--name": ["Mary", "Jane"], "--phone": ["0123456789"]}


@pytest.mark.parametrize(
    "args",
    [
        ["Mary"],
        ["--name"],
        ["--name", "Mary", "--name", "Jane"],
        ["--name", "Mary", "--unknown", "value"],
        ["--phone", "123", "456", "--name", "Mary"],
        ["--name", "Mary", "--phone"],
    ],
)
def test_parse_options_rejects_invalid_input(args):
    with pytest.raises(InvalidInputError, match="Invalid arguments"):
        parse_options(args, {"--name", "--phone"}, {"--name"}, "usage", {"--phone"})


def test_parse_options_reports_missing_required_values():
    with pytest.raises(InvalidInputError, match="--name"):
        parse_options(["--phone", "123"], {"--name", "--phone"}, {"--name"}, "usage")
