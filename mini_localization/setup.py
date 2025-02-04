from typing import Optional

_setup_config: Optional[dict] = None


def setup(default_locale=None, locales_dir=None, **kwargs):
    from mini_localization.config import set_default_locale, DEFAULT_LOCAL_DIR
    from mini_localization.config import default_locale as _default_locale

    if default_locale:
        set_default_locale(default_locale)
    else:
        default_locale = _default_locale

    global _setup_config
    config = dict(
        default_locale=default_locale,
        locales_dir=locales_dir or DEFAULT_LOCAL_DIR,
    )
    config.update(kwargs)

    _setup_config = config


def get_setup_config():
    global _setup_config
    if _setup_config is None:
        setup()

    return _setup_config
