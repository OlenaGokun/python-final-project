import contextlib
import os
import pickle
import sys
import tempfile
from pathlib import Path

from address_book.book import AddressBook

APP_NAME = "phone-book-bot"
DATA_FILENAME = "addressbook.pkl"


def get_data_dir() -> Path:
    """Per-user data directory, following each OS's convention.

    Windows: %APPDATA%\\phone-book-bot
    macOS:   ~/Library/Application Support/phone-book-bot
    Linux:   $XDG_DATA_HOME/phone-book-bot (default ~/.local/share/phone-book-bot)
    """
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        xdg = os.environ.get("XDG_DATA_HOME")
        # The XDG spec says relative paths must be ignored.
        base = Path(xdg) if xdg and os.path.isabs(xdg) else Path.home() / ".local" / "share"
    return base / APP_NAME


def get_data_file() -> Path:
    return get_data_dir() / DATA_FILENAME


def save_data(book, filename=None):
    """Write atomically: a crash mid-write never leaves a truncated file behind."""
    path = Path(filename) if filename is not None else get_data_file()
    path.parent.mkdir(parents=True, exist_ok=True)

    # The temp file must live in the same directory so os.replace is atomic.
    tmp = tempfile.NamedTemporaryFile(
        mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
    )
    try:
        with tmp as f:
            pickle.dump(book, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp.name, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.remove(tmp.name)
        raise


def load_data(filename=None):
    path = Path(filename) if filename is not None else get_data_file()
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
