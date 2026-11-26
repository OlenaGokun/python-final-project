from personal_helper.commands.base_command import NotebookCommand
from personal_helper.core.data import parse_options
from personal_helper.core.decorators import input_error
from personal_helper.core.exceptions import InvalidInputError
from personal_helper.models.notes import Notebook


class SortNotesByTagsCommand(NotebookCommand):
    """Command to sort notes prioritizing matching tags."""

    def get_command_name(self) -> str:
        return "sort-notes-by-tags"

    def get_description(self) -> str:
        return "sort notes by tags (matching tags first)"

    def get_usage(self) -> str:
        return "sort-notes-by-tags --tags <tag> [tag2 ...]"

    @input_error
    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        options = parse_options(
            args,
            {"--tags"},
            set(),
            self.get_usage(),
        )
        raw_tags = options.get("--tags")
        if not raw_tags:
            raise InvalidInputError(
                f"Invalid arguments. Provide at least one tag.\n"
                f"Usage: {self.get_usage()}"
            )

        notes = notebook.sort_by_tags(set(raw_tags))
        if not notes:
            return "ℹ️  No notes found."
        return "\n".join(self.format_note_compact(note) for note in notes)