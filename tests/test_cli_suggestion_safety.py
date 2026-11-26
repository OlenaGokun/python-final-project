from main import main
from personal_helper.models import Record


def test_delete_typo_requires_exact_retry_and_confirmation(monkeypatch, capsys, data):
    name = "Private Test Contact"
    data.address_book.add_record(Record(name))
    steps = iter([
        ("Enter a command: ", f"delete-contatc --name {name}"),
        ("Enter a command: ", f"delete-contact --name {name}"),
        (f"Delete contact '{name}'? (Y)es/(N)o: ", "yes"),
        ("Enter a command: ", "exit"),
    ])
    saved = []
    turns = []

    def read(prompt):
        expected_prompt, response = next(steps)
        assert prompt == expected_prompt
        turns.append(capsys.readouterr().out.splitlines())
        if len(turns) in (2, 3):
            assert data.address_book.find(name) is not None
        return response

    monkeypatch.setattr("builtins.input", read)
    monkeypatch.setattr("main.load_data", lambda: data)
    monkeypatch.setattr("main.save_data", saved.append)

    main()

    assert turns[1] == ["Invalid command.", "Did you mean: delete-contact?"]
    assert turns[2] == []
    assert turns[3] == [f"✅ Contact '{name}' deleted."]
    assert saved == [data]
    assert data.address_book.find(name) is None
