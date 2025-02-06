import unittest
from mini_localization import get_locale, get_text, setup_locale, ProxyLocale, Locale
from dataclasses import dataclass
from datetime import date


@dataclass
class Date1:
    year: int
    month: int
    day: int

    def __localized_format__(self, locale, fmt='long'):
        key = f"date.format.long" if fmt == 'long' else 'date.format.short'
        fmt = locale.get(key, default='%Y-%m-%d')
        dt = date(self.year, self.month, self.day)

        fmt = fmt.replace('%A', locale.get(f'date.week_day.{dt.weekday()}', default='None'))  # Full weekday name
        fmt = fmt.replace('%B', locale.get(f'date.months.{dt.month}', default='None'))  # Full month name

        return dt.strftime(fmt)


class TestLocale(unittest.TestCase):

    def setUp(self):
        self.current_locale = 'en'

        class DummyProxyLocale(ProxyLocale):
            def get_locale(s) -> Locale:
                return get_locale(self.current_locale)

        setup_locale(DummyProxyLocale())

        # TODO: formatters & modifiers
        #
        # # modifiers
        #
        # def plural_default(singular, value, *args):
        #     if value == 1:
        #
        #     pass


    def test_get_text_plain_string(self):
        self.current_locale = 'en'
        result = get_text("plain_text")
        self.assertEqual(result, "plain_text")

        self.current_locale = 'ar'
        result = get_text("plain_text")
        self.assertEqual(result, "نص عادي")

    def test_get_text_with_brace_expression(self):
        self.current_locale = 'en'

        result = get_text("[greeting] {name}!", name="John")
        self.assertEqual(result, "Hello John!")

        # test format spec
        result = get_text("${price:.2f}", price=5.5)
        self.assertEqual(result, "$5.50")

        # test non existent parameter
        result = get_text("[greeting] {name}!", namo="John")
        self.assertEqual(result, "Hello None!")

        self.current_locale = 'ar'

        result = get_text("[greeting] {name}!", name="John")
        self.assertEqual(result, "أهلاً John!")

        # test format spec
        result = get_text("${price:.2f}", price=5.5)
        self.assertEqual(result, "5.50 دينار")

        # test non existent parameter
        result = get_text("[greeting] {name}!", namo="John")
        self.assertEqual(result, "أهلاً None!")

        self.current_locale = 'ar_MA'
        result = get_text("${price:.2f}", price=5.5)
        self.assertEqual(result, "5.50 درهم")

    def test_get_text_with_custom_formatter(self):
        # using __localized_format__
        self.current_locale = 'en'
        result = get_text("{date:long}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "Tuesday, May 04, 2021")

        result = get_text("{date:short}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "04/05/2021")

        result = get_text("{date}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "04/05/2021")

        # using __localized_format__
        self.current_locale = 'ar'

        result = get_text("{date:long}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "الثلاثاء، 04 مايو 2021")

        result = get_text("{date:short}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "04/05/2021")

        self.current_locale = 'ar_MA'

        result = get_text("{date:long}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "الثلاثاء، 04 ماي 2021")

        result = get_text("{date:long}", date=Date1(1988, 9, 21))
        self.assertEqual(result, "الأربعاء، 21 شتنبر 1988")

    # def test_get_text_with_modifier(self):
    #     result = self.locale.get_text("shout")
    #     self.assertEqual(result, "HELLO")
    #
    # def test_decorators(self):
    #     pass # TODO


if __name__ == '__main__':
    unittest.main()
