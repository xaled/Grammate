from .base import BaseLocale
from .locale import Locale
from abc import abstractmethod, ABC


class ProxyLocale(BaseLocale, ABC):
    @abstractmethod
    def get_locale(self) -> Locale:
        pass

    def get(self, key, default=None):
        return self.get_locale().get(key, default=default)

    def get_rule(self, key, default=None):
        return self.get_locale().get_rule(key, default=default)

    def get_formatter(self, key, default=None):
        return self.get_locale().get_formatter(key, default=default)

    def format(self, obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None):
        return self.get_locale().format(obj, fmt=fmt, default_formatter=default_formatter, formatter_id=formatter_id)

    def apply_rule(self, key, rule_id, *args, **kwargs):
        return self.get_locale().apply_rule(key, rule_id, *args, **kwargs)

    def get_text(self, text_key, default=None, *args):
        return self.get_locale().get_text(text_key, default=default, *args)

    def register_rule(self, rule_id, rule_func):
        return self.get_locale().register_rule(rule_id, rule_func)

    def register_formatter(self, formatter_id, formatter_func):
        return self.get_locale().register_formatter(formatter_id, formatter_func)
