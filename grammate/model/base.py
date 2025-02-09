from abc import abstractmethod, ABC


class BaseLocale(ABC):
    @abstractmethod
    def get(self, key, default=None):
        pass

    @abstractmethod
    def get_modifier(self, key, default=None):
        pass

    @abstractmethod
    def get_formatter(self, key, default=None):
        pass

    @abstractmethod
    def format(self, obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None):
        pass

    @abstractmethod
    def apply_modifier(self, modifier_id, *args):
        pass

    @abstractmethod
    def get_text(self, text_key, **kwargs):
        pass

    @abstractmethod
    def register_modifier(self, modifier_id, modifier_func):
        pass

    @abstractmethod
    def register_formatter(self, formatter_id, formatter_func):
        pass
