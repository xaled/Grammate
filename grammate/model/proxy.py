from .base import BaseLocale
from .locale import Locale
from abc import abstractmethod, ABC


class ProxyLocale(BaseLocale, ABC):
    @abstractmethod
    def get_locale(self) -> Locale:
        pass

    def get(self, key, default=None):
        return self.get_locale().get(key, default=default)

    def get_modifier(self, key, default=None):
        return self.get_locale().get_modifier(key, default=default)

    def get_formatter(self, key, default=None):
        return self.get_locale().get_formatter(key, default=default)

    def format(self, obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None):
        return self.get_locale().format(obj, fmt=fmt, default_formatter=default_formatter, formatter_id=formatter_id)

    def apply_modifier(self, modifier_id, *args):
        return self.get_locale().apply_modifier(modifier_id, *args)

    def get_text(self, text_key, **kwargs):
        return self.get_locale().get_text(text_key, **kwargs)

    def register_modifier(self, modifier_id, modifier_func):
        return self.get_locale().register_modifier(modifier_id, modifier_func)

    def register_formatter(self, formatter_id, formatter_func):
        return self.get_locale().register_formatter(formatter_id, formatter_func)
