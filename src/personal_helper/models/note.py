from personal_helper.core import InvalidNoteError
from .fields import Tag, Text, Title


class Note:
    def __init__(self, title: str, text: str, tags: set[str] | None = None):
        self._title = Title(title)
        self._text = Text(text)
        self._tags: set[Tag] = set()
        if tags:
            self.add_tags(tags)

    @property
    def title(self) -> Title:
        return self._title

    @property
    def text(self) -> Text:
        return self._text

    @property
    def tags(self) -> frozenset[Tag]:
        return frozenset(self._tags)

    def update_text(self, text: str) -> None:
        self.update(text=text)

    def update(self, text: str | None = None, tags: set[str] | None = None) -> None:
        if text is None and tags is None:
            raise InvalidNoteError("Provide text or tags to update.")
        new_text = Text(text) if text is not None else self._text
        new_tags = {Tag(tag) for tag in tags} if tags is not None else self._tags
        self._text = new_text
        self._tags = new_tags

    def add_tags(self, tags: set[str]) -> None:
        if not tags:
            raise InvalidNoteError("At least one tag is required.")
        new_tags = {Tag(tag) for tag in tags}
        self._tags.update(new_tags)

    def remove_tags(self, tags: set[str]) -> None:
        if not tags:
            raise InvalidNoteError("At least one tag is required.")
        requested = {Tag(tag) for tag in tags}
        missing = requested - self._tags
        if missing:
            names = ", ".join(sorted(tag.value for tag in missing))
            raise InvalidNoteError(f"Tags not found on note '{self.title}': {names}.")
        self._tags.difference_update(requested)

    def __str__(self) -> str:
        tags = ", ".join(sorted(tag.value for tag in self.tags))
        return f"Note title: {self.title.value}, text: {self.text.value}, tags: {tags}"

    def __repr__(self) -> str:
        tags = sorted(tag.value for tag in self.tags)
        tags_repr = "{" + ", ".join(repr(tag) for tag in tags) + "}" if tags else "set()"
        return f"Note({self.title.value!r}, {self.text.value!r}, tags={tags_repr})"
