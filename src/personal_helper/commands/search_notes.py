from personal_helper.commands.base_command import NotebookCommand
from personal_helper.core.decorators import input_error
from personal_helper.core.data import parse_options
from personal_helper.core.exceptions import InvalidInputError
from personal_helper.models.notes import Notebook


class SearchNotesCommand(NotebookCommand):
    """Command to search notes by title, text, and tags."""

    def get_command_name(self) -> str:
        return "search-notes"

    def get_description(self) -> str:
        return "search notes by title, text, or tags"

    def get_usage(self) -> str:
        return (
            "search-notes (--query <query> | [--title <title>] [--text <text>] "
            "[--tags <tag> ...])"
        )

    @input_error
    def run_with_notebook(self, args: list, notebook: Notebook) -> str:
        options = parse_options(
            args, {"--query", "--title", "--text", "--tags"}, set(), self.get_usage()
        )
        if not options:
            raise InvalidInputError(
                f"Invalid arguments. Provide --query or at least one field.\n"
                f"Usage: {self.get_usage()}"
            )
        if "--query" in options and len(options) > 1:
            raise InvalidInputError(
                f"Invalid arguments. --query cannot be combined with field filters.\n"
                f"Usage: {self.get_usage()}"
            )
        values = {
            key[2:]: set(items) if key == "--tags" else " ".join(items)
            for key, items in options.items()
        }
        notes = notebook.search(**values)
        if not notes:
            return "ℹ️  No notes found."
        return "\n".join(
            f"{note.title}: {note.text}"
            + (
                f" [tags: {', '.join(sorted(tag.value for tag in note.tags))}]"
                if note.tags
                else ""
            )
            for note in notes
        )
