from typing import Union

from .model import Locale, BaseLocale

_locales: dict[str, Locale] = dict()


def get_locale(locale_id: str = '', fallback_locale_id: str = None) -> Locale:
    global _locales
    from mini_localization.config import load_locale_config
    from .setup import get_setup_config

    setup_config = get_setup_config()
    default_locale = setup_config['default_locale']

    if locale_id not in _locales:
        locale_config = load_locale_config(locale_id,
                                           locales_dir=setup_config['locales_dir'],
                                           fallback_locale=fallback_locale_id)
        lang, _, country = locale_id.partition('_')

        if fallback_locale_id is None and locale_id != lang:
            fallback_locale_id = lang
        elif fallback_locale_id is None and locale_id != default_locale:
            fallback_locale_id = default_locale

        fallback_locale = get_locale(fallback_locale_id) if fallback_locale_id else None

        _locales[locale_id] = Locale(config=locale_config, fallback_locale=fallback_locale)

    return _locales[locale_id]


def get_default_locale():
    from mini_localization.config import default_locale

    return get_locale(default_locale)


def setup_locale(locale: Union[BaseLocale, str], fallback_locale_id=None, default_locale=None,
                 locales_dir=None, **setup_kwargs) -> Locale:
    from .setup import setup
    setup(default_locale=default_locale, locales_dir=locales_dir, **setup_kwargs)
    global _locales
    _locales[''] = get_locale(locale, fallback_locale_id=fallback_locale_id) if isinstance(locale, str) else locale
    return _locales['']


def get(key, default=None, locale=''):
    return get_locale(locale).get(key, default=default)


def get_modifier(key, default=None, locale=''):
    return get_locale(locale).get_modifier(key, default=default)


def get_formatter(key, default=None, locale=''):
    return get_locale(locale).get_formatter(key, default=default)


def format(obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None, locale=''):
    return get_locale(locale).format(obj, fmt=fmt, default_formatter=default_formatter, formatter_id=formatter_id)


def apply_modifier(modifier_id, *args, locale=''):
    return get_locale(locale).apply_modifier(modifier_id, *args)


def get_text(text_key, locale='', **kwargs):
    return get_locale(locale).get_text(text_key, **kwargs)


def register_modifier(modifier_id, modifier_func, locale=None):
    if locale is None:
        from mini_localization.config import default_locale
        locale = default_locale

    return get_locale(locale).register_modifier(modifier_id, modifier_func)


def register_formatter(formatter_id, formatter_func, locale=None):
    if locale is None:
        from mini_localization.config import default_locale
        locale = default_locale

    return get_locale(locale).register_formatter(formatter_id, formatter_func)


def modifier(modifier_id, locale):
    def decorator(modifier_func):
        register_modifier(modifier_id, modifier_func, locale=locale)
        return modifier_func

    return decorator


def formatter(cls, locale=''):
    formatter_id = Locale.get_formatter_id(cls)

    def decorator(formatter_func):
        register_formatter(formatter_id, formatter_func, locale=locale)
        return formatter_func

    return decorator
