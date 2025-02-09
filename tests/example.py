import json
from grammate import get_locale, get_text, setup_locale, ProxyLocale, Locale, register_modifier, \
    modifier, formatter
from dataclasses import dataclass
from datetime import date


# setup
setup_locale()


# Formatting
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
        fmt = fmt.replace('%Y', self.year)
        fmt = fmt.replace('%m', self.month)
        fmt = fmt.replace('%d', self.day)

        return fmt


default_date_formats = dict(
    short="%Y-%m-%d",
    long="%A, %B %d, %Y"
)


@formatter(cls=Date)
def formate_date(dt: Date, locale, fmt=None):
    from datetime import date as _date
    fmt = fmt or 'medium'
    if fmt in ('medium', 'short', 'long'):
        fmt = locale.get(f'date.formats.{fmt}') or default_date_formats[fmt]
    if fmt == 'medium' or fmt:
        locale.get('date.formats.short', "%B %d %Y")

    dt2 = _date(dt.year, dt.month, dt.day)
    weekday = dt2.weekday()

    fmt = fmt.replace('%A', locale.get(f'date.weekdays.{weekday}', default='%A'))  # Full weekday name
    fmt = fmt.replace('%a', locale.get(f'date.weekdays_short.{weekday}', default='%a'))  # Abbreviated weekday name.
    fmt = fmt.replace('%B', locale.get(f'date.months.{weekday}', default='%B'))  # Full month name
    fmt = fmt.replace('%b', locale.get(f'date.months_short.{weekday}', default='%b'))  # Abbreviated month name.

    return dt2.strftime(fmt)


def register_format_method(format_func, cls=None):
    def __format__(self, format_spec):
        locale_id = None  # TODO: extract locale form format spec

        return format_func(self, locale_id=locale_id, fmt=format_spec)
    # TODO: assign method to class


register_format_method(format_func=formate_date, cls=Date)

print(get_locale().format(Date(2025, 1, 1)))


# custom rules

# @mini_localistion.rule(locale_id='ar', rule_id='plural')
def plural_form_ar(value, forms, **kwargs):
    with_value = kwargs.get('with_value', True)
    rest = value % 100

    base_form = forms[0]
    plural_form = forms[1] if len(forms) > 1 else base_form
    dual_form = forms[2] if len(forms) > 2 else base_form
    mansub_form = forms[3] if len(forms) > 3 else base_form

    if value == 1:
        formatted = base_form
    elif value == 2:
        formatted = dual_form
    elif 2 < rest <= 10:
        formatted = plural_form
    elif rest > 10:
        formatted = mansub_form
    else:
        formatted = base_form

    return f"{value} {formatted}" if with_value else formatted


get_locale('ar').register_modifier(modifier_id='plural', modifier_func=plural_form_ar)

print(get_locale().gettext(key='month', rule_id='plural', value=5))

_('text', )

# extended formating

_('{hijri_date:long} corresponding to {gregorian_date:medium}', hijri_date=hijri_date, gregorian_date=gregorian_date)

# ar {hijri_date:long} الموافق لـ {gregorian_date:medium}

_('I have a [apple.adj:$color]', color='red')
# en [apple.adj:$color] => {red} apple => red apple
# ar [apple.adj:$color,fem,indef,marfuu] عندي
# ar [apple.adj:$color,fem,indef,marfuu] => تفاحة {red.fem.indef.marfuu} => تفاحة حمراء
_('I have [!plural:apple,ste$count]', count=5)
# en [apple!plural:$count] =>  plural('apple', 1) => {count} [apple] => 1 apple
# en [apple!plural:$count] =>  plural('apple', 5) => {count} [apple.plural] => 5 apples
# ar [apple!plural:$count] عندي
# ar [apple!plural:$count] => plural('apple', 1) => {count} [apple.plural.0] => 1 تفاحة
# ar [apple!plural:$count] => plural('apple', 2) => [apple.plural.2] => تفاحتين
# ar [apple!plural:$count] => plural('apple', 5) => {count} [apple.plural.1] => 5 تفاحات
# ar [apple!plural:$count] => plural('apple', 11) => {count} [apple.plural.3] => 11 تفاحة
# ar [apple!plural:$count,without_value] => plural('apple', 11, 'without_value') => [apple.plural.3] => َتفاحة

# [apple!plural:$count,arg2] => plural(locale, 'apple', count, 'arg2'): forms = locale.get('apple' + '.plural')...
