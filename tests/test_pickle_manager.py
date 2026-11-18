import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pickle_manager
from pickle_manager import get_data_dir, load_data, save_data
from address_book.book import AddressBook
from address_book.record import Record


class TestGetDataDir(unittest.TestCase):
    def test_windows_uses_appdata(self):
        with mock.patch.object(pickle_manager.sys, "platform", "win32"), \
                mock.patch.dict(os.environ, {"APPDATA": r"C:\Users\u\AppData\Roaming"}):
            self.assertEqual(get_data_dir(), Path(r"C:\Users\u\AppData\Roaming") / "phone-book-bot")

    def test_macos_uses_application_support(self):
        with mock.patch.object(pickle_manager.sys, "platform", "darwin"):
            self.assertEqual(
                get_data_dir(),
                Path.home() / "Library" / "Application Support" / "phone-book-bot",
            )

    def test_linux_uses_xdg_data_home(self):
        with mock.patch.object(pickle_manager.sys, "platform", "linux"), \
                mock.patch.dict(os.environ, {"XDG_DATA_HOME": "/xdg/data"}):
            self.assertEqual(get_data_dir(), Path("/xdg/data/phone-book-bot"))

    def test_linux_falls_back_to_local_share(self):
        env = {k: v for k, v in os.environ.items() if k != "XDG_DATA_HOME"}
        with mock.patch.object(pickle_manager.sys, "platform", "linux"), \
                mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(get_data_dir(), Path.home() / ".local" / "share" / "phone-book-bot")

    def test_linux_ignores_relative_xdg_data_home(self):
        with mock.patch.object(pickle_manager.sys, "platform", "linux"), \
                mock.patch.dict(os.environ, {"XDG_DATA_HOME": "relative/dir"}):
            self.assertEqual(get_data_dir(), Path.home() / ".local" / "share" / "phone-book-bot")


class TestSaveLoad(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _book(self):
        book = AddressBook()
        record = Record("John")
        record.add_phone("1234567890")
        record.add_birthday("15.03.1990")
        book.add_record(record)
        return book

    def test_round_trip(self):
        path = self.dir / "book.pkl"
        save_data(self._book(), path)
        loaded = load_data(path)
        self.assertEqual(str(loaded["JOHN"]), str(self._book()["john"]))

    def test_creates_missing_directories(self):
        path = self.dir / "a" / "b" / "book.pkl"
        save_data(self._book(), path)
        self.assertTrue(path.exists())

    def test_missing_file_returns_empty_book(self):
        book = load_data(self.dir / "nope.pkl")
        self.assertIsInstance(book, AddressBook)
        self.assertEqual(len(book), 0)

    def test_failed_save_keeps_old_file_and_leaves_no_temp_files(self):
        path = self.dir / "book.pkl"
        save_data(self._book(), path)
        original = path.read_bytes()

        with mock.patch.object(pickle_manager.pickle, "dump", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                save_data(AddressBook(), path)

        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(os.listdir(self.dir), ["book.pkl"])

    def test_default_location_is_used_without_filename(self):
        with mock.patch.object(pickle_manager, "get_data_dir", return_value=self.dir / "app"):
            save_data(self._book())
            self.assertTrue((self.dir / "app" / "addressbook.pkl").exists())
            self.assertIsNotNone(load_data().find("john"))


if __name__ == "__main__":
    unittest.main()
