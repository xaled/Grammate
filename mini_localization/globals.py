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


def setup_locale(locale: Union[BaseLocale, str], fallback_locale_id=None, default_locale=None,
                 locales_dir=None, **setup_kwargs) -> Locale:
    from .setup import setup
    setup(default_locale=default_locale, locales_dir=locales_dir, **setup_kwargs)
    global _locales
    _locales[''] = get_locale(locale, fallback_locale_id=fallback_locale_id) if isinstance(locale, str) else locale
    return _locales['']
