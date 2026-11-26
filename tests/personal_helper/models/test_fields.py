"""Tests for field classes (Name, Phone, Birthday)"""

import unittest
from personal_helper.models.fields import Field, Name, Phone, Tag, Text, Title
from personal_helper.core import (
    InvalidInputError,
    InvalidNameError,
    InvalidPhoneFormatError,
    InvalidNoteError,
)


class TestField(unittest.TestCase):
    def test_str_returns_the_value(self):
        self.assertEqual(str(Field("abc")), "abc")

    def test_str_converts_non_strings(self):
        self.assertEqual(str(Field(42)), "42")

    def test_repr_includes_concrete_type_and_value(self):
        self.assertEqual(repr(Field("abc")), "Field('abc')")
        self.assertEqual(repr(Name("John")), "Name('John')")

    def test_equality_requires_the_same_type(self):
        self.assertEqual(Phone("1234567890"), Phone("1234567890"))
        self.assertNotEqual(Phone("1234567890"), Field("1234567890"))

    def test_equality_with_non_field_returns_not_implemented(self):
        field = Field("abc")
        self.assertIs(field.__eq__("abc"), NotImplemented)
        self.assertNotEqual(field, "abc")

    def test_is_hashable(self):
        self.assertEqual(len({Phone("1234567890"), Phone("1234567890")}), 1)

    def test_value_is_read_only(self):
        with self.assertRaises(AttributeError):
            Phone("1234567890").value = "0000000000"


class TestName(unittest.TestCase):
    def test_stores_the_value(self):
        self.assertEqual(Name("John").value, "John")

    def test_strips_surrounding_whitespace(self):
        self.assertEqual(Name("  John  ").value, "John")

    def test_key_is_casefolded(self):
        self.assertEqual(Name("  JoHn ").key, "john")

    def test_empty_name_is_rejected(self):
        with self.assertRaises(InvalidNameError):
            Name("")

    def test_whitespace_only_name_is_rejected(self):
        with self.assertRaises(InvalidNameError):
            Name("   ")

    def test_non_string_is_rejected(self):
        with self.assertRaises(InvalidNameError):
            Name(None)


class TestPhone(unittest.TestCase):
    def test_accepts_ten_digits(self):
        self.assertEqual(Phone("1234567890").value, "1234567890")

    def test_too_short_is_rejected(self):
        with self.assertRaises(InvalidPhoneFormatError):
            Phone("123456789")

    def test_too_long_is_rejected(self):
        with self.assertRaises(InvalidPhoneFormatError):
            Phone("12345678901")

    def test_empty_is_rejected(self):
        with self.assertRaises(InvalidPhoneFormatError):
            Phone("")

    def test_non_string_is_rejected(self):
        with self.assertRaises(InvalidPhoneFormatError):
            Phone(1234567890)

    def test_non_digits_are_rejected(self):
        with self.assertRaises(InvalidPhoneFormatError):
            Phone("123456789a")

    def test_normalizes_various_input_formats(self):
        self.assertEqual(Phone("    +38(050)123-32-34").value, "0501233234")
        self.assertEqual(Phone("     0503451234").value, "0503451234")
        self.assertEqual(Phone("(050)8889900").value, "0508889900")
        self.assertEqual(Phone("38050-111-22-22").value, "0501112222")
        self.assertEqual(Phone("38050 111 22 11   ").value, "0501112211")
        self.assertEqual(Phone("123-456-7890").value, "1234567890")
        self.assertEqual(Phone("80501234567").value, "0501234567")
        self.assertEqual(str(Phone("+38(050)123-45-67")), "0501234567")

    def test_non_ascii_digits_are_rejected(self):
        with self.assertRaises(InvalidPhoneFormatError):
            # Fullwidth digits
            Phone("１２３４５６７８９０")

    def test_invalid_alias_is_rejected(self):
        for alias in ("", "two words", 123):
            with (
                self.subTest(alias=alias),
                self.assertRaises(InvalidInputError),
            ):
                Phone("1234567890", alias)

    def test_error_message_mentions_the_value(self):
        with self.assertRaises(InvalidPhoneFormatError) as context:
            Phone("abc")
        self.assertIn("abc", str(context.exception))


class TestNoteFields(unittest.TestCase):
    def test_title_preserves_original_value_and_casefolds_key(self):
        title = Title("  Große Straße  ")
        self.assertEqual(title.value, "Große Straße")
        self.assertEqual(title.key, "grosse strasse")
        self.assertIsInstance(title, Field)

    def test_tag_casefolds_and_deduplicates(self):
        self.assertEqual({Tag("FOOD"), Tag("food")}, {Tag("food")})
        self.assertIsInstance(Tag("food"), Field)

    def test_text_trims_outer_whitespace_and_preserves_inner_text(self):
        text = Text("  Buy  milk  ")
        self.assertIsInstance(text, Field)
        self.assertEqual(text.value, "Buy  milk")
        self.assertEqual(str(text), "Buy  milk")
        with self.assertRaises(AttributeError):
            text.value = "changed"

    def test_text_rejects_empty_or_non_string_values(self):
        for value in ("", "  ", None, 123):
            with (
                self.subTest(value=value),
                self.assertRaises(InvalidNoteError),
            ):
                Text(value)

    def test_title_and_tag_reject_invalid_values(self):
        for cls in (Title, Tag):
            for value in ("", " ", None):
                with (
                    self.subTest(cls=cls, value=value),
                    self.assertRaises(InvalidNoteError),
                ):
                    cls(value)
        with self.assertRaises(InvalidNoteError):
            Tag("two words")


if __name__ == "__main__":
    unittest.main()
