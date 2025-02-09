# Grammate

**Grammate** is a lightweight Python module for localization based on formal grammars.

---

## Installation

You can install Grammate via `pip`:

```bash
pip install grammate
```

---

## Features

- **Custom Formatters For Classes.**
- **Complex Grammatical Rules.**
- **YAML-based Configuration.**
- **Inheritance Support:** Locales can inherit settings from other locales, making it easy to define regional variations or dialects.
- **Proxy Locale Support:** Allows dynamic locale selection in applications (e.g., Flask).

---

## Limitations

Grammate is **not a comprehensive localization library** and does **not contain any localization knowledge** out of the box, such as currencies, number and date formats. You need to implement grammar formatters and modifiers in your code and configuration files.

---

## Basic Usage

### YAML Files for Localization

Grammate uses YAML files to store your translations for different locales.

#### locales/en.yaml

This file contains the translation for the English locale:

```yaml
greeting: "Hello"
```

#### locales/ar.yaml

This file contains the translation for the Arabic locale:

```yaml
greeting: "أهلاً"
```

#### example.py

```python
from grammate import get_locale, setup_locale, get_text

# Set up default locale (English)
setup_locale()

# Get greeting text in the default locale (English)
print(get_text('greeting'))  # Output: Hello

# Get greeting text in Arabic
print(get_locale('ar').get_text('greeting'))  # Output: أهلاً

# Use placeholders in text
print(get_text('[greeting] {name}!', name='Ahmed'))  # Output: Hello Ahmed!
```

---

## Advanced Usage

### Proxy Locale for Dynamic Locale Resolution (e.g., Flask)

You can set up a proxy locale to dynamically resolve the locale for a user, for instance, based on a session in a Flask application.

```python
from grammate import get_locale, setup_locale, get_text, ProxyLocale
from flask import session

class FlaskSessionLocale(ProxyLocale):
    def get_locale(s) -> Locale:
        # Resolve the current locale based on Flask session
        return get_locale(session.get('locale') or 'ar')

# Set up locale with dynamic resolution using Flask's session
setup_locale(FlaskSessionLocale(), default_locale='ar', locales_dir=None)
```

In this example, `FlaskSessionLocale` overrides the `get_locale` method to dynamically return the locale based on the session's `locale` key, with a fallback to `'ar'` if not specified.

### Custom Formatters

Grammate supports custom formatters any class. This allows you to localize your own classes.
The following example shows how to format a custom HijriDate that implements the `__localized_format__` method:




#### example.py (Custom Date Formatter)

We can create a custom `HijriDate` class that implements the `__localized_format__` method to format Hijri dates.


```python
from grammate import get_locale, setup_locale, get_text
from dataclasses import dataclass

@dataclass
class HijriDate:
    year: int
    month: int
    day: int

    @property
    def weekday(self):
        return 0  # Always Monday :)

    def __localized_format__(self, locale, fmt='long'):
        key = f"date.format.long" if fmt == 'long' else 'date.format.short'
        fmt = locale.get(key, default='%Y-%m-%d')

        fmt = fmt.replace('%A', locale.get(f'date.week_day.{self.weekday}', default='None'))  # Full weekday name
        fmt = fmt.replace('%B', locale.get(f'hijridate.months.{self.month}', default='None'))  # Full month name
        fmt = fmt.replace('%Y', str(self.year))
        fmt = fmt.replace('%m', str(self.month))
        fmt = fmt.replace('%d', str(self.day))

        return fmt

setup_locale()

result = get_locale('ar').get_text("{date:long}", date=HijriDate(1442, 9, 21))
print(result)  # الإثنين، 21 رمضان 1442
```

#### locales/ar.yaml (Custom Date Formatter)

```yaml
date:
  format:
    long: '%A، %d %B %Y'  # Example: الإثنين، 01 يناير 2024
    short: '%d/%m/%Y'     # Example: 01/01/2024
  months:
    1: يناير
    2: فبراير
    3: مارس
  week_day:
    0: الإثنين
    1: الثلاثاء
hijridate:
  months:
    1: محرم
    2: صفر
```


---

### Custom Formatters for Imported Classes

Grammate also allows you to define formatters for imported classes, like `date`. You can use the `@formatter` decorator to create custom formatters for these classes.

```python
from grammate import formatter
from datetime import date

@formatter(date)
def date_formatter(dt, locale, fmt='long'):
    key = f"date.format.long" if fmt == 'long' else 'date.format.short'
    fmt = locale.get(key, default='%Y-%m-%d')

    fmt = fmt.replace('%A', locale.get(f'date.week_day.{dt.weekday()}', default='None'))  # Full weekday name
    fmt = fmt.replace('%B', locale.get(f'date.months.{dt.month}', default='None'))  # Full month name

    return dt.strftime(fmt)

result = get_locale('ar').get_text("{date:long}", date=date(2021, 5, 4))
print(result)  # الثلاثاء، 04 مايو 2021
```

---

### Configuration Inheritance

By default, a locale such as `ar_MA` (for Morocco) inherits from a parent locale like `ar` (Arabic). All locales inherit from the default locale unless otherwise specified.

You can override specific parts of the locale configuration. In the example below, `ar_MA.yaml` inherits from `ar.yaml` but customizes the month names for the Moroccan variant.

#### locales/ar_MA.yaml (inherits from `ar.yaml` by default)

```yaml
date:
  months:
    5: ماي
    6: يونيو
    7: يوليوز
    8: غشت
    9: شتنبر
    11: نونبر
    12: دجنبر
```

Example usage:

```python
result = get_locale('ar_MA').get_text("{date:long}", date=date(2021, 5, 4))
print(result)  # الثلاثاء، 04 ماي 2021
```

You can also define custom inheritance using the key `$extends` for the entire configuration or for specific subkeys. For instance:

#### locales/ur.yaml

```yaml
$extends: 'en'
hijridate:
  months:
    $extends: 'ar'
```

Example usage:

```python
result = get_locale('ur').get_text("{date:long}", date=HijriDate(1442, 9, 21))
print(result)  # Monday, رمضان 21, 1442
```

In this example, the Urdu locale inherits from English, except for the Hijri date months, which are inherited from Arabic.

---

### Custom Grammar Rules

Custom grammar rules can be defined as modifiers. The expression format is `[!modifier_id:args]`, where `args` are YAML/JSON lists without the brackets. If an argument starts with a `$`, it is searched in the provider's kwargs.

Example of a simple plural modifier:

```python
@modifier('plural', locale='en')
def plural_en(locale, singular, value, *args):
    form = locale.get(singular, default=singular)
    if value != 1:
        # find the plural form in the locale config or add 's' if not found
        form = locale.get(singular + '.plural', default=None) or f'{form}s'

    return f'{value} {form}'
```

Usage example:

```python
result = get_text("I have [!plural:apple,$count]!", count=1)
print(result)  # I have 1 apple!

result = get_text("I have [!plural:apple,$count]!", count=2)
print(result)  # I have 2 apples!
```

Modifiers can be as simple or as complex as needed, and they can request locale configurations based on the passed arguments.

It is also possible to chain modifiers by returning a valid `get_text` expression. For example:

```python
@modifier('adj', locale='ar')  # Gender should be specified for agreement
def adj_ar(locale, word, adj, *args):
    word = locale.get(word, default=word)
    adj_forms = locale.get(f'{adj}.forms', default={})
    adj = locale.get(adj, default=adj)
    if 'fem' in args:
        adj = adj_forms.get('fem') or adj
    else:
        adj = adj_forms.get('masc') or adj

    return f'{word} {adj}'


@modifier('adj2', locale='ar')  # Gender is resolved from locale configuration then passed to the first modifier
def adj2_ar(locale, word, adj, *args):  # Find gender
    rules = locale.get(f'{word}.rules', default={})
    gender = rules.get('gender', 'masc')
    args = [word, adj, gender]
    return f"[!adj:{json.dumps(args)[1:-1]}]"

result = get_text("عندي [!adj2:$thing,$adj]!", thing='apple', adj='red')
print(result) # عندي تفاحة حمراء!
result = get_text("عندي [!adj2:$thing,$adj]!", thing='apple', adj='red')
print(result) # عندي دفتر أحمر!
```

In this example, the `adj2` modifier resolves `thing`'s gender from the locale configuration and passes it to the `adj` modifier,
enabling gender-based adjective agreement in the final output.

---

## License

Grammate is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

