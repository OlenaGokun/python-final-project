import os
import pickle
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import personal_helper.core.pickle_manager as pickle_manager
from personal_helper.core.pickle_manager import get_data_dir, load_data, save_data
from personal_helper.models.book import AddressBook
from personal_helper.models.personal_helper import PersonalHelper
from personal_helper.models.fields import Tag
from personal_helper.models.record import Record

class TestGetDataDir(unittest.TestCase):
    def test_windows_uses_appdata(self):
        with mock.patch.object(pickle_manager.sys, "platform", "win32"), \
                mock.patch.dict(os.environ, {"APPDATA": r"C:\Users\u\AppData\Roaming"}):
            self.assertEqual(get_data_dir(), Path(r"C:\Users\u\AppData\Roaming") / "personal-helper-bot")

    def test_macos_uses_application_support(self):
        with mock.patch.object(pickle_manager.sys, "platform", "darwin"):
            self.assertEqual(
                get_data_dir(),
                Path.home() / "Library" / "Application Support" / "personal-helper-bot",
            )

    def test_linux_uses_xdg_data_home(self):
        with mock.patch.object(pickle_manager.sys, "platform", "linux"), \
                mock.patch.dict(os.environ, {"XDG_DATA_HOME": "/xdg/data"}):
            self.assertEqual(get_data_dir(), Path("/xdg/data/personal-helper-bot"))

    def test_linux_falls_back_to_local_share(self):
        env = {k: v for k, v in os.environ.items() if k != "XDG_DATA_HOME"}
        with mock.patch.object(pickle_manager.sys, "platform", "linux"), \
                mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(get_data_dir(), Path.home() / ".local" / "share" / "personal-helper-bot")

    def test_linux_ignores_relative_xdg_data_home(self):
        with mock.patch.object(pickle_manager.sys, "platform", "linux"), \
                mock.patch.dict(os.environ, {"XDG_DATA_HOME": "relative/dir"}):
            self.assertEqual(get_data_dir(), Path.home() / ".local" / "share" / "personal-helper-bot")

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
        save_data(PersonalHelper(self._book()), path)
        loaded = load_data(path)
        self.assertEqual(str(loaded.address_book["JOHN"]), str(self._book()["john"]))

    def test_note_round_trip(self):
        path = self.dir / "book.pkl"
        data = PersonalHelper(self._book())
        data.notebook.add("shopping", "Buy milk")
        data.notebook.add("plans", "Call next week")
        data.notebook.add_tags("plans", {"personal", "work"})

        save_data(data, path)
        loaded = load_data(path)

        self.assertEqual(loaded.notebook.search(tags={"WORK"})[0].title.value, "plans")
        self.assertEqual(loaded.notebook.search(tags={"work"})[0].tags, {Tag("personal"), Tag("work")})
        self.assertEqual(loaded.notebook["shopping"].text.value, "Buy milk")
        loaded.notebook.update_note("PLANS", "Call tomorrow")
        loaded.notebook.delete("SHOPPING")
        save_data(loaded, path)
        reloaded = load_data(path)
        self.assertEqual(reloaded.notebook["plans"].text.value, "Call tomorrow")
        self.assertNotIn("shopping", reloaded.notebook)
        self.assertEqual(reloaded.notebook.search(tags={"personal"})[0].text.value, "Call tomorrow")
        self.assertIsNotNone(reloaded.address_book.find("John"))
        self.assertNotIn("_notes", reloaded.address_book.__dict__)

    def test_unexpected_saved_data_fails_explicitly(self):
        path = self.dir / "book.pkl"
        path.write_bytes(pickle.dumps({"contacts": []}))
        with self.assertRaisesRegex(TypeError, "Saved data must contain"):
            load_data(path)

    def test_address_book_with_development_notes_is_not_silently_discarded(self):
        path = self.dir / "book.pkl"
        book = self._book()
        book._notes = {"shopping": "Buy milk"}
        path.write_bytes(pickle.dumps(book))
        with self.assertRaisesRegex(ValueError, "Unsupported saved address book"):
            load_data(path)

    def test_old_book_without_notes_can_use_notes(self):
        path = self.dir / "book.pkl"
        book = self._book()
        self.assertNotIn("_notes", book.__dict__)
        path.write_bytes(pickle.dumps(book))

        loaded = load_data(path)
        self.assertEqual(len(loaded.notebook), 0)
        loaded.notebook.add("shopping", "Buy milk")
        self.assertEqual(loaded.notebook["shopping"].text.value, "Buy milk")
        self.assertIsNotNone(loaded.address_book.find("John"))

    def test_creates_missing_directories(self):
        path = self.dir / "a" / "b" / "book.pkl"
        save_data(PersonalHelper(self._book()), path)
        self.assertTrue(path.exists())

    def test_missing_file_returns_empty_data(self):
        data = load_data(self.dir / "nope.pkl")
        self.assertIsInstance(data, PersonalHelper)
        self.assertEqual(len(data.address_book), 0)
        self.assertEqual(len(data.notebook), 0)

    def test_failed_save_keeps_old_file_and_leaves_no_temp_files(self):
        path = self.dir / "book.pkl"
        save_data(PersonalHelper(self._book()), path)
        original = path.read_bytes()

        with mock.patch.object(pickle_manager.pickle, "dump", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                save_data(PersonalHelper(), path)

        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(os.listdir(self.dir), ["book.pkl"])

    def test_default_location_is_used_without_filename(self):
        with mock.patch.object(pickle_manager, "get_data_dir", return_value=self.dir / "app"):
            save_data(PersonalHelper(self._book()))
            self.assertTrue((self.dir / "app" / "addressbook.pkl").exists())
            self.assertIsNotNone(load_data().address_book.find("john"))

if __name__ == "__main__":
    unittest.main()
