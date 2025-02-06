from typing import Optional
import yaml
import os
from collections.abc import Mapping
import re

DEFAULT_LOCAL_DIR = 'locales'
default_locale = 'en'
_INTEGER_REGEX = re.compile('^\d+$')


class ConfigDict(Mapping):
    def __init__(self, config: dict):
        self.config = config

    def __getitem__(self, k):
        key_path = tuple(k.split('.'))
        return ConfigDict.config_get(self.config, key_path)

    def __len__(self):
        return self.config.__len__()

    def __iter__(self):
        return self.config.__iter__()

    @staticmethod
    def config_get(obj: dict, key_path: tuple[str]):
        for i in range(len(key_path)):
            stem, child = key_path[:-i], key_path[-i:]
            if i == 0:
                stem, child = child, stem
            stem_key = '.'.join(stem)
            if stem_key in obj:
                value = obj[stem_key]
                if len(child) == 1 and isinstance(value, dict):
                    if child[0] in value:
                        return value[child[0]]
                    elif _INTEGER_REGEX.match(child[0]) and int(child[0]) in value:
                        return value[int(child[0])]
                    return None

                elif len(child) == 1 and isinstance(value, list):
                    return value[int(child[0])]
                elif child and isinstance(value, dict):
                    return ConfigDict.config_get(value, child)
                elif not child:
                    return value
        return None


def set_default_locale(locale):
    global default_locale
    default_locale = locale


def flatten_config(obj: dict, parent_key: str = '', ) -> dict:
    items = {}
    for k, v in obj.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_config(v, new_key, ))
        else:
            items[new_key] = v
    return items


def _load_single(yaml_path: str) -> Optional[dict]:
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return None


def _load_config(locale: str, locales_dir: str = DEFAULT_LOCAL_DIR):
    locale_path = os.path.join(locales_dir, f'{locale}.yaml')
    return _load_single(locale_path)


# def _load_multiple(yaml_path: str) -> Optional[List[dict]]:
#     if os.path.exists(yaml_path):
#         with open(yaml_path, 'r', encoding='utf-8') as f:
#             return list(yaml.safe_load_all(f))
#     return None


def merge_dicts(base: dict, override: dict) -> dict:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = merge_dicts(base[key], value)
        else:
            base[key] = value
    return base


def load_locale_config(locale: str, locales_dir: str = DEFAULT_LOCAL_DIR,
                       fallback_locale: Optional[str] = None) -> ConfigDict:
    lang, _, country = locale.partition('_')
    # Load locale configurations

    locale_config = _load_config(locale, locales_dir=locales_dir)

    if locale_config is None:
        if fallback_locale:
            return load_locale_config(fallback_locale, locales_dir=locales_dir)
        if locale != lang:
            return load_locale_config(lang, locales_dir=locales_dir)
        if locale != default_locale:
            return load_locale_config(lang, locales_dir=locales_dir)
        locale_config = dict()

    # default inheritance
    if not locale_config.get('$extends'):
        if locale != lang:
            locale_config['$extends'] = lang
        elif locale != default_locale:
            locale_config['$extends'] = default_locale

    # # Load default configurations
    # default_path = os.path.join(locales_dir, 'defaults.yaml')
    # default_configs = _load_multiple(default_path) or []
    # resolved_defaults = {}
    # for config in default_configs:
    #     if 'condition' in config and 'config' in config and 'else' in config:
    #         condition = config['condition']
    #         config_value = config['config'] if eval_condition(condition, locale, lang) else config.get('else')
    #         resolved_defaults.update(config_value)
    # # Merge defaults
    # locale_config = merge_dicts(resolved_defaults, locale_config)

    # Resolve inheritance
    locale_config = resolve_inheritance(locale_config, locales_dir)

    return ConfigDict(locale_config)


# def eval_condition(condition: Union[str, List[str]], locale: str, lang: str) -> bool:
#     if isinstance(condition, str):
#         return condition in (locale, lang)
#     return locale in condition or lang in condition


def resolve_inheritance(config: dict, locales_dir: str, path=()) -> dict:
    for key, value in config.items():
        if isinstance(value, dict):
            sub_path = path + (key,)
            config[key] = resolve_inheritance(value, locales_dir=locales_dir, path=sub_path)

    if '$extends' in config:
        parent_locale = config.pop('$extends')
        parent_config = _load_config(parent_locale, locales_dir=locales_dir) or {}
        sub_parent_config = resolve_dict_path(parent_config, path)
        config = merge_dicts(sub_parent_config, config)

    return config


def resolve_dict_path(obj, path):
    if not obj:
        return obj
    for key in path:
        obj = obj.get(key, None) or dict()
    return obj
