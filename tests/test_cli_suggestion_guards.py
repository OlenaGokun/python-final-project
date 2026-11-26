import socket
from unittest.mock import Mock

from personal_helper.commands.base_command import ExitRequest


def test_lookup_misses_work_offline_without_dispatch(cli_turns, registry, monkeypatch):
    network = Mock(side_effect=AssertionError("CLI attempted to open a socket"))
    monkeypatch.setattr(socket, "socket", network)
    read = Mock()
    mutation = Mock()
    exit_command = Mock(return_value=ExitRequest())
    monkeypatch.setattr(registry.get_command("show-all-contacts"), "run", read)
    monkeypatch.setattr(registry.get_command("delete-contact"), "run", mutation)
    monkeypatch.setattr(registry.get_command("exit"), "run", exit_command)

    turns = cli_turns([
        "zzzzzzzz", "s", "sh", "show-all-c", "show-all-contatcs",
        "delete-cont", "delete-contatc", "exi", "exitt", "exit",
    ])

    assert turns[:3] == [["Invalid command."]] * 3
    assert turns[3:] == [
        ["Invalid command.", f"Did you mean: {name}?"]
        for name in ("show-all-contacts", "show-all-contacts",
                     "delete-contact", "delete-contact", "exit", "exit")
    ]
    read.assert_not_called()
    mutation.assert_not_called()
    exit_command.assert_called_once()
    network.assert_not_called()
