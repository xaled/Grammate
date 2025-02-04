from abc import abstractmethod, ABC


class BaseLocale(ABC):
    @abstractmethod
    def get(self, key, default=None):
        pass

    @abstractmethod
    def get_rule(self, key, default=None):
        pass

    @abstractmethod
    def get_formatter(self, key, default=None):
        pass

    @abstractmethod
    def format(self, obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None):
        pass

    @abstractmethod
    def apply_rule(self, key, rule_id, *args, **kwargs):
        pass

    @abstractmethod
    def get_text(self, text_key, default=None, *args):
        pass

    @abstractmethod
    def register_rule(self, rule_id, rule_func):
        pass

    @abstractmethod
    def register_formatter(self, formatter_id, formatter_func):
        pass