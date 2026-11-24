import pickle

import pytest

from personal_helper import parse_input
from personal_helper.core import DuplicatePhoneError
from personal_helper.models import Record


def run(registry, data, line):
    name, *args = parse_input(line)
    command = registry.get_command(name)
    assert command is not None, f"Missing command: {name}"
    return command.run(args, data)


@pytest.mark.parametrize("change_selector", ["mobile", "6660006666"])
@pytest.mark.parametrize("delete_selector", ["mobile", "8889990001"])
def test_phone_alias_lifecycle(registry, data, change_selector, delete_selector):
    assert run(registry, data, "add Jane 5550009999").startswith("✅")
    assert run(registry, data, "add Jane mobile 6660006666").startswith("✅")
    assert run(registry, data, "add Jane MOBILE 7770007777").startswith(
        "❌ Phone alias"
    )

    data = pickle.loads(pickle.dumps(data))
    record = data.address_book["Jane"]
    assert [(phone.alias, phone.value) for phone in record.phones] == [
        ("main", "5550009999"),
        ("mobile", "6660006666"),
    ]
    assert run(registry, data, f"change-phone --name Jane --old-phone {change_selector} --new-phone 8889990001").startswith("✅")
    assert record.find_phone("mobile").value == "8889990001"
    assert "mobile" in run(registry, data, "phone --name Jane")
    assert run(registry, data, f"delete Jane {delete_selector}").startswith("✅")
    assert [(phone.alias, phone.value) for phone in record.phones] == [
        ("main", "5550009999")
    ]


def test_phone_aliases_coexist_with_existing_flag_commands(registry, data):
    assert registry.get_command("change") is None
    assert run(registry, data, "add-contact --name Jane --phone 5550009999 1110001111").startswith("✅")
    record = data.address_book["Jane"]
    for phone in record.phones:
        del phone._alias  # Simulate phone objects saved before aliases existed.

    assert run(registry, data, "add Jane custom-label 6660006666").startswith("✅")
    assert run(registry, data, "change-phone --name Jane --old-phone custom-label --new-phone 8889990001").startswith("✅")
    assert run(registry, data, "delete-phone --name Jane --phone custom-label").startswith("✅")
    assert run(registry, data, "change-phone --name Jane --old-phone 5550009999 --new-phone 5550001111").startswith("✅")
    assert [phone.value for phone in record.phones] == ["5550001111", "1110001111"]


def test_selector_cannot_point_to_two_phones():
    record = Record("Jane")
    record.add_phone("5550009999", alias="main")
    record.add_phone("6660006666", alias="8889990001")

    with pytest.raises(DuplicatePhoneError):
        record.edit_phone("main", "8889990001")

    assert record.find_phone("main").value == "5550009999"
    assert record.find_phone("8889990001").value == "6660006666"


def test_phone_aliases_with_a_quoted_contact_name(registry, data):
    assert run(registry, data, 'add "Mary Jane" home 5550009999').startswith("✅")
    assert run(registry, data, 'change-phone --name Mary Jane --old-phone HOME --new-phone 8889990001').startswith("✅")
    assert run(registry, data, 'phone --name Mary Jane') == "home: 8889990001"
    assert run(registry, data, 'delete "Mary Jane" home').startswith("✅")


def test_change_phone_requires_named_arguments(registry, data):
    assert run(registry, data, "add Jane 5550009999").startswith("✅")
    result = run(registry, data, "change-phone Jane main 8889990001")
    assert result.startswith("❌ Invalid arguments.")
    assert data.address_book["Jane"].find_phone("main").value == "5550009999"
