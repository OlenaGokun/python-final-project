import contextlib
import os
import pickle
import sys
import tempfile
from pathlib import Path

from personal_helper.models.book import AddressBook
from personal_helper.models.personal_helper import PersonalHelper

APP_NAME = "personal-helper-bot"
DATA_FILENAME = "addressbook.pkl"


def get_data_dir() -> Path:
    """Per-user data directory, following each OS's convention.

    Windows: %APPDATA%\\personal-helper-bot
    macOS:   ~/Library/Application Support/personal-helper-bot
    Linux:   $XDG_DATA_HOME/personal-helper-bot (default ~/.local/share/personal-helper-bot)
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


def save_data(data: PersonalHelper, filename=None):
    """Write atomically: a crash mid-write never leaves a truncated file behind."""
    path = Path(filename) if filename is not None else get_data_file()
    path.parent.mkdir(parents=True, exist_ok=True)

    # The temp file must live in the same directory so os.replace is atomic.
    tmp = tempfile.NamedTemporaryFile(
        mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
    )
    try:
        with tmp as f:
            pickle.dump(data, f)
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
            data = pickle.load(f)
    except FileNotFoundError:
        return PersonalHelper()

    if isinstance(data, AddressBook):
        if "_notes" in data.__dict__:
            raise ValueError("Unsupported saved address book containing development-version notes.")
        return PersonalHelper(data)
    if not isinstance(data, PersonalHelper):
        raise TypeError("Saved data must contain a PersonalHelper or AddressBook object.")
    return data
