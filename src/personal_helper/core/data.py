import shlex

from .exceptions import InvalidInputError


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "",
    cmd, *args = parts
    cmd = cmd.strip().lower()
    if cmd in {"add", "change", "delete"}:
        try:
            _, *args = shlex.split(user_input)
        except ValueError as error:
            raise InvalidInputError(f"Invalid arguments. {error}.") from error
    return cmd, *args


def parse_options(
    args: list[str], allowed: set[str], required: set[str], usage: str,
    single: set[str] | None = None,
) -> dict[str, list[str]]:
    options: dict[str, list[str]] = {}
    current: str | None = None

    def invalid(message: str) -> InvalidInputError:
        return InvalidInputError(f"Invalid arguments. {message}\nUsage: {usage}")

    for word in args:
        if word.startswith("--"):
            if word not in allowed:
                raise invalid(f"Unknown option: {word}.")
            if word in options:
                raise invalid(f"Repeated option: {word}.")
            current = word
            options[current] = []
        elif current is None:
            raise invalid(f"Unexpected value: {word}.")
        else:
            options[current].append(word)
    for name, values in options.items():
        if not values or any(not value.strip() for value in values):
            raise invalid(f"Option {name} requires a value.")
        if single and name in single and len(values) != 1:
            raise invalid(f"Option {name} requires exactly one value.")
    missing = required - options.keys()
    if missing:
        raise invalid(f"Missing required options: {', '.join(sorted(missing))}.")
    return options
