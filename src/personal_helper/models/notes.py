from collections import UserDict

from personal_helper.core import (
    InvalidNoteError,
    NoteAlreadyExistsError,
    NoteNotFoundError,
)
from .fields import Tag, Text, Title
from .note import Note


class Notebook(UserDict):
    """Notes indexed by case-insensitive titles."""

    def __getitem__(self, title: str) -> Note:
        return self.data[Title(title).key]

    def __setitem__(self, title: str, note: Note) -> None:
        key = Title(title).key
        if not isinstance(note, Note):
            raise TypeError("Notebook values must be Note objects.")
        if key != note.title.key:
            raise InvalidNoteError("Notebook key must match the note title.")
        self.data[key] = note

    def __delitem__(self, title: str) -> None:
        del self.data[Title(title).key]

    def __contains__(self, title: object) -> bool:
        if not isinstance(title, str):
            return False
        return Title(title).key in self.data

    def _find(self, title: str) -> Note | None:
        return self.data.get(Title(title).key)

    def _require(self, title: str) -> Note:
        note = self._find(title)
        if note is None:
            raise NoteNotFoundError(f"Note '{title}' not found.")
        return note

    def add(self, title: str, text: str, tags: set[str] | None = None) -> None:
        note = Note(title, text, tags)
        if note.title.key in self.data:
            raise NoteAlreadyExistsError(f"Note '{title}' already exists.")
        self[note.title.value] = note

    def update_note(
        self, title: str, text: str | None = None, tags: set[str] | None = None
    ) -> None:
        self._require(title).update(text, tags)

    def delete(self, title: str) -> None:
        note = self._require(title)
        del self[note.title.value]

    def search(
        self,
        query: str | None = None,
        *,
        title: str | None = None,
        text: str | None = None,
        tags: set[str] | None = None,
    ) -> tuple[Note, ...]:
        title_query = (
            Text(title).value.casefold() if title is not None else None
        )
        text_query = Text(text).value.casefold() if text is not None else None
        query_value = (
            query.strip().casefold()
            if isinstance(query, str) and query.strip()
            else None
        )
        if tags is not None and not tags:
            raise InvalidNoteError("At least one tag is required.")
        selected = {Tag(tag) for tag in tags} if tags is not None else None
        if query_value is not None:
            title_query = text_query = None
            selected = None
        if (
            query_value is None
            and title_query is None
            and text_query is None
            and selected is None
        ):
            return ()

        return tuple(
            note
            for note in self.data.values()
            if (
                query_value is None
                or any(
                    query_value in value
                    for value in (
                        note.title.value.casefold(),
                        note.text.value.casefold(),
                        *(tag.value for tag in note.tags),
                    )
                )
            )
            and (title_query is None or title_query in note.title.key)
            and (
                text_query is None or text_query in note.text.value.casefold()
            )
            and (selected is None or bool(selected.intersection(note.tags)))
        )

    def add_tags(self, title: str, tags: set[str]) -> None:
        self._require(title).add_tags(tags)

    def remove_tags(self, title: str, tags: set[str]) -> None:
        self._require(title).remove_tags(tags)

    def sort_by_tags(self) -> tuple[Note, ...]:
        def sort_key(note: Note) -> tuple[int, str, str]:
            sorted_tags = sorted(tag.value for tag in note.tags)
            if sorted_tags:
                return (0, sorted_tags[0], note.title.key)
            return (1, "", note.title.key)

        return tuple(sorted(self.data.values(), key=sort_key))
        
    def __str__(self) -> str:
        if not self.data:
            return "Notebook is empty."
        return "\n".join(str(note) for note in self.data.values())

    def __repr__(self) -> str:
        return f"Notebook({self.data!r})"
