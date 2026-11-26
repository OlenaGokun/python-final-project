import pytest


@pytest.mark.parametrize(
    ("field", "initial", "replacement", "delete_args"),
    [
        ("phone", "5012345671", "5098765432", ["--phone", "5098765432"]),
        ("email", "first@example.com", "second@example.com", []),
        ("birthday", "25.12.1990", "26.12.1990", []),
    ],
)
def test_can_edit_and_delete_each_contact_field(
    registry, data, field, initial, replacement, delete_args
):
    name = ["--name", "Jane", "Doe"]

    def run(command_name, args):
        command = registry.get_command(command_name)
        assert command is not None, f"Missing command: {command_name}"
        assert command.run(args, data).startswith("✅")

    run("add-contact", [*name, f"--{field}", initial])
    if field == "phone":
        run("add-contact", [*name, "--phone", "5011111111"])
        run(
            "change-phone",
            [*name, "--old-phone", initial, "--new-phone", replacement],
        )
    else:
        run(f"add-{field}", [*name, f"--{field}", replacement])

    record = data.address_book["Jane Doe"]
    if field == "phone":
        assert [phone.value for phone in record.phones] == [
            replacement,
            "5011111111",
        ]
    else:
        assert str(getattr(record, field)) == replacement

    run(f"delete-{field}", [*name, *delete_args])
    assert data.address_book["Jane Doe"] is record
    if field == "phone":
        assert [phone.value for phone in record.phones] == ["5011111111"]
    else:
        assert getattr(record, field) is None
