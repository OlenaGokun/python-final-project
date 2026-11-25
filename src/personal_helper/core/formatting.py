import sys

from colorama import Fore, Style


def colored(value: str, color: str) -> str:
    if not sys.stdout.isatty():
        return value
    return f"{color}{value}{Style.RESET_ALL}"


def error_message(message: str) -> str:
    return colored(message, Fore.RED)
