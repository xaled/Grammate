from typing import Optional

_setup_config: Optional[dict] = None


def setup(default_locale=None, locales_dir=None, **kwargs):
    from grammate.config import set_default_locale_id, DEFAULT_CONFIG_DIR
    from grammate.config import default_locale_id

    if default_locale:
        set_default_locale_id(default_locale)
    else:
        default_locale = default_locale_id

    global _setup_config
    config = dict(
        default_locale=default_locale,
        locales_dir=locales_dir or DEFAULT_CONFIG_DIR,
    )
    config.update(kwargs)

    _setup_config = config


def get_setup_config():
    global _setup_config
    if _setup_config is None:
        setup()

    return _setup_config
