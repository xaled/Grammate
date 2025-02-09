import json
import unittest
from grammate import get_locale, get_text, setup_locale, ProxyLocale, Locale, register_modifier, \
    modifier, formatter
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


@dataclass
class HijriDate:
    year: int
    month: int
    day: int

    @property
    def weekday(self):
        return 0  # always monday :(

    def __localized_format__(self, locale, fmt='long'):
        key = f"date.format.long" if fmt == 'long' else 'date.format.short'
        fmt = locale.get(key, default='%Y-%m-%d')

        fmt = fmt.replace('%A', locale.get(f'date.week_day.{self.weekday}', default='None'))  # Full weekday name
        fmt = fmt.replace('%B', locale.get(f'hijridate.months.{self.month}', default='None'))  # Full month name
        fmt = fmt.replace('%Y', str(self.year))
        fmt = fmt.replace('%m', str(self.month))
        fmt = fmt.replace('%d', str(self.day))

        return fmt

def plural_default(locale, singular, value, *args):
    form = locale.get(singular, default=singular)
    if value != 1:
        form = locale.get(singular + '.plural', default=form)

    if 'without_value' in args:
        return form
    return f'{value} {form}'

def plural_ar(locale, singular, value, *args):
    forms = locale.get(singular + '.plural') or [locale.get(singular)]
    base_form = forms[0]
    plural_form = forms[1] if len(forms) > 1 else base_form
    dual_form = forms[2] if len(forms) > 2 else base_form
    mansub_form = forms[3] if len(forms) > 3 else base_form
    rest = value % 100

    with_value = 'without_value' not in args

    if value == 1:
        formatted = base_form
        # return f"{formatted} {value}" if with_value else formatted # reversed form for 1
    elif value == 2:
        formatted = dual_form
        if dual_form != base_form:
            return dual_form
    elif 2 < rest <= 10:
        formatted = plural_form
    elif rest > 10:
        formatted = mansub_form
    else:
        formatted = base_form

    return f"{value} {formatted}" if with_value else formatted


def adj_en(locale, word, adj, *args):
    word = locale.get(word, default=word)
    adj = locale.get(adj, default=adj)

    return f'{adj} {word}'


def adj_ar(locale, word, adj, *args):
    word = locale.get(word, default=word)
    adj_forms = locale.get(f'{adj}.forms', default={})
    adj = locale.get(adj, default=adj)
    if 'fem' in args:
        adj = adj_forms.get('fem') or adj
    else:
        adj = adj_forms.get('masc') or adj

    return f'{word} {adj}'


class TestLocale(unittest.TestCase):

    def setUp(self):
        self.current_locale = 'en'

        class DummyProxyLocale(ProxyLocale):
            def get_locale(s) -> Locale:
                return get_locale(self.current_locale)

        setup_locale(DummyProxyLocale())

        # register plural modifiers
        register_modifier('plural', plural_default)
        register_modifier('plural', plural_ar, locale='ar')

        # register adj modifier
        register_modifier('adj', adj_en, locale='en')
        register_modifier('adj', adj_ar, locale='ar')

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

        result = get_text("{date:long}", date=HijriDate(1442, 9, 21))
        self.assertEqual(result, "الإثنين، 21 رمضان 1442")

        self.current_locale = 'ar_MA'

        result = get_text("{date:long}", date=Date1(2021, 5, 4))
        self.assertEqual(result, "الثلاثاء، 04 ماي 2021")

        result = get_text("{date:long}", date=Date1(1988, 9, 21))
        self.assertEqual(result, "الأربعاء، 21 شتنبر 1988")

        # formatting and extending
        self.current_locale = 'ur'
        result = get_text("{date:long}", date=HijriDate(1442, 9, 21))
        self.assertEqual(result, "Monday, رمضان 21, 1442")

    def test_get_text_with_plural_modifier(self):
        self.current_locale = 'en'

        result = get_text("I have [!plural:apple,$count]!", count=1)
        self.assertEqual(result, "I have 1 apple!")
        result = get_text("I have [!plural:apple,$count]!", count=2)
        self.assertEqual(result, "I have 2 apples!")

        self.current_locale = 'ar'

        result = get_text("I have [!plural:apple,$count]!", count=0)
        self.assertEqual(result, "عندي 0 تفاحة!")

        result = get_text("I have [!plural:apple,$count]!", count=1)
        self.assertEqual(result, "عندي 1 تفاحة!")

        result = get_text("I have [!plural:apple,$count]!", count=2)
        self.assertEqual(result, "عندي تفاحتين!")

        result = get_text("I have [!plural:apple,$count]!", count=5)
        self.assertEqual(result, "عندي 5 تفاحات!")

        result = get_text("I have [!plural:apple,$count]!", count=60)
        self.assertEqual(result, "عندي 60 تفاحةً!")

        result = get_text("I have [!plural:apple,$count]!", count=105)
        self.assertEqual(result, "عندي 105 تفاحات!")

        result = get_text("I have [!plural:apple,$count]!", count=1000)
        self.assertEqual(result, "عندي 1000 تفاحة!")

    def test_get_text_with_adj_modifier(self):
        self.current_locale = 'en'
        result = get_text("I have a [!adj:apple,$adj]!", adj='red')
        self.assertEqual(result, "I have a red apple!")
        result = get_text("I have a [!adj:notebook,$adj]!", adj='red')
        self.assertEqual(result, "I have a red notebook!")

        self.current_locale = 'ar'
        result = get_text("I have a [!adj:apple,$adj]!", adj='red')
        self.assertEqual(result, "عندي تفاحة حمراء!")
        result = get_text("I have a [!adj:notebook,$adj]!", adj='red')
        self.assertEqual(result, "عندي دفتر أحمر!")

    def test_modifier_decorator(self):
        @modifier('plural2', '')
        def plural_default2(*args):
            return plural_default(*args)

        @modifier('plural2', 'ar')
        def plural_ar2(*args):
            return plural_ar(*args)

        self.current_locale = 'en'

        result = get_text("I have [!plural2:apple,$count]!", count=0)
        self.assertEqual(result, "I have 0 apples!")
        result = get_text("I have [!plural2:apple,$count]!", count=1)
        self.assertEqual(result, "I have 1 apple!")

        self.current_locale = 'ar'

        result = get_text("I have [!plural2:apple,$count]!", count=0)
        self.assertEqual(result, "عندي 0 تفاحة!")
        result = get_text("I have [!plural2:apple,$count]!", count=1)
        self.assertEqual(result, "عندي 1 تفاحة!")

    def test_formatter_decorator(self):
        @formatter(date)
        def date_formatter(dt, locale, fmt='long'):
            key = f"date.format.long" if fmt == 'long' else 'date.format.short'
            fmt = locale.get(key, default='%Y-%m-%d')

            fmt = fmt.replace('%A', locale.get(f'date.week_day.{dt.weekday()}', default='None'))  # Full weekday name
            fmt = fmt.replace('%B', locale.get(f'date.months.{dt.month}', default='None'))  # Full month name

            return dt.strftime(fmt)

        self.current_locale = 'en'
        result = get_text("{date:long}", date=date(2021, 5, 4))
        self.assertEqual(result, "Tuesday, May 04, 2021")

        result = get_text("{date:short}", date=date(2021, 5, 4))
        self.assertEqual(result, "04/05/2021")

        # using __localized_format__
        self.current_locale = 'ar'
        result = get_text("{date:long}", date=date(2021, 5, 4))
        self.assertEqual(result, "الثلاثاء، 04 مايو 2021")

        self.current_locale = 'ar_MA'
        result = get_text("{date:long}", date=date(2021, 5, 4))
        self.assertEqual(result, "الثلاثاء، 04 ماي 2021")

    def test_get_text_with_advanced_modifiers(self):
        @modifier('a', locale='en')
        def indefinite_article_english(locale, word, *args):
            rules = locale.get(f'{word}.rules', default={})
            word = locale.get(word, default=word)
            return rules.get('a', None) or ('an' if word[0].lower().startswith(tuple('aeiou')) else 'a')

        self.current_locale = 'en'
        result = get_text("I have [!a:$adj] [!adj:apple,$adj]!", adj='red')
        self.assertEqual(result, "I have a red apple!")
        result = get_text("I have [!a:$adj] [!adj:apple,$adj]!", adj='orange')
        self.assertEqual(result, "I have an orange apple!")
        result = get_text("I have [!a:$adj] [!adj:apple,$adj]!", adj='honest')
        self.assertEqual(result, "I have an honest apple!")

    def test_get_text_with_chained_modifiers(self):

        @modifier('adj', locale='ar')  # gender should be specified for agreement
        def adj_ar(locale, word, adj, *args):
            word = locale.get(word, default=word)
            adj_forms = locale.get(f'{adj}.forms', default={})
            adj = locale.get(adj, default=adj)
            if 'fem' in args:
                adj = adj_forms.get('fem') or adj
            else:
                adj = adj_forms.get('masc') or adj

            return f'{word} {adj}'

        @modifier('adj2', locale='ar')  # gender is gotten from locale rules then passed to the first modifier
        def adj2_ar(locale, word, adj, *args):  # get gender
            rules = locale.get(f'{word}.rules', default={})
            gender = rules.get('gender', 'masc')
            args = [word, adj, gender]
            return f"[!adj:{json.dumps(args)[1:-1]}]"

        self.current_locale = 'ar'
        expression = "عندي [!adj2:$thing,$adj]!"
        result = get_text(expression, thing='apple', adj='red')
        self.assertEqual(result, "عندي تفاحة حمراء!")
        result = get_text(expression, thing='notebook', adj='red')
        self.assertEqual(result, "عندي دفتر أحمر!")


if __name__ == '__main__':
    unittest.main()
