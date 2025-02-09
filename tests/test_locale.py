import unittest
from decimal import Decimal

from grammate.globals import get_locale
from grammate.model import Locale
from grammate.config import ConfigDict
from dataclasses import dataclass


@dataclass
class Date1:
    year: int
    month: int
    day: int

    def __localized_format__(self, locale, fmt='long'):
        key = f"date.long" if fmt == 'long' else 'date.short'
        string_format = locale.get(key, default='{year}-{month}-{day}')
        return string_format.format(year=self.year, month=self.month, day=self.day)


@dataclass
class Date2:
    year: int
    month: int
    day: int

    def __format__(self, format_spec: str = 'long'):
        string_format = "{day}th {month} Month, {year}" if format_spec == 'long' else '{year}-{month}-{day}'
        return string_format.format(year=self.year, month=self.month, day=self.day)


@dataclass
class Date3:
    year: int
    month: int
    day: int


def format_date3(self, locale, format_spec: str = 'long'):
    key = f"date.long" if format_spec == 'long' else 'date.short'
    string_format = locale.get(key, default='{year}-{month}-{day}')
    return string_format.format(year=self.year, month=self.month, day=self.day)


class TestLocale(unittest.TestCase):

    def setUp(self):
        self.locale = Locale(ConfigDict(
            {
                'greeting': 'Hello {name}!',
                'price': '${price:.2f}',
                'currency.format': '${value:.2f}',
                'shout': '[!uppercase:hello]',
                "nested": "[$key1] and {name}",
                "key1": "Value1",
                'unresolved': "Hello {name}, your [$balance] is {balance:.2f}",
                "date": {
                    "short": "{year}-{month}-{day}",
                    "long": "{day}th {month} Month, {year}",
                }
            }
        ))

        # Mock formatter for currency
        # def currency_formatter(value, locale, fmt=None):
        #     return f""
        #
        date3_formatter_id = Locale.get_formatter_id(Date3)
        self.locale.register_formatter(date3_formatter_id, format_date3)

        # Mock modifier for uppercase
        def uppercase_modifier(locale, text):
            return text.upper()

        self.locale.register_modifier('uppercase', uppercase_modifier)

    def test_get_text_plain_string(self):
        result = self.locale.get_text("plain_text")
        self.assertEqual(result, "plain_text")

    def test_get_text_with_brace_expression(self):
        result = self.locale.get_text("greeting", name="John")
        self.assertEqual(result, "Hello John!")

        # test format spec
        result = self.locale.get_text("${price:.2f}", price=5.5)
        self.assertEqual(result, "$5.50")

        # test non existent parameter
        result = self.locale.get_text("greeting", namo="John")
        self.assertEqual(result, "Hello None!")

    def test_get_text_with_bracket_expression(self):
        result = self.locale.get_text("price", price=19.9)
        self.assertEqual(result, "$19.90")

    def test_get_text_with_custom_formatter(self):
        # using __localized_format__
        result = self.locale.get_text("{date:long}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "4th 5 Month, 2021")

        result = self.locale.get_text("{date:short}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "2021-5-4")

        result = self.locale.get_text("{date}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "2021-5-4")

        # using __format__
        result = self.locale.get_text("{date:long}", date=Date2(2021, 5, 4))
        self.assertEqual(result, "4th 5 Month, 2021")

        result = self.locale.get_text("{date:short}", date=Date2(2021, 5, 4))
        self.assertEqual(result, "2021-5-4")

        result = self.locale.get_text("{date}", date=Date2(2021, 5, 4))
        self.assertEqual(result, "2021-5-4")

        # using custom function
        result = self.locale.get_text("{date:long}", date=Date3(2021, 5, 4))
        self.assertEqual(result, "4th 5 Month, 2021")

        result = self.locale.get_text("{date:short}", date=Date3(2021, 5, 4))
        self.assertEqual(result, "2021-5-4")

        result = self.locale.get_text("{date}", date=Date3(2021, 5, 4))
        self.assertEqual(result, "2021-5-4")

    def test_get_text_with_modifier(self):
        result = self.locale.get_text("shout")
        self.assertEqual(result, "HELLO")

    def test_get_text_with_unknown_key_returns_key(self):
        result = self.locale.get_text("unknown_key")
        self.assertEqual(result, "unknown_key")

    def test_get_text_with_nested_expressions(self):
        result = self.locale.get_text("nested", name="Bob")
        self.assertEqual(result, "Value1 and Bob")

    def test_get_text_with_unresolved_expressions(self):
        result = self.locale.get_text("unresolved", name="Alice")
        self.assertEqual(result, "Hello Alice, your balance is None")

    def test_get_text_with_invalid_modifier(self):
        with self.assertRaises(ValueError):
            self.locale.get_text("[!nonexistent:hello]")


if __name__ == '__main__':
    unittest.main()
