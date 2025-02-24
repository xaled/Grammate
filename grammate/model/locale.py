from typing import Optional

from .base import BaseLocale
from ..config import ConfigDict
from ..parser import ExpressionParser, BracketExpression, BraceExpression


class Locale(BaseLocale):
    def __init__(self, config: 'ConfigDict', fallback_locale: Optional['Locale'] = None):
        self.config = config
        self.modifiers = dict()
        self.formatters = dict()
        self.fallback_locale = fallback_locale

    def get(self, key, default=None):
        return self.config.get(key) or (self.fallback_locale.get(key, default) if self.fallback_locale else default)

    def get_modifier(self, key, default=None):
        return self.modifiers.get(key) or (
            self.fallback_locale.get_modifier(key, default) if self.fallback_locale else default)

    def get_formatter(self, key, default=None):
        return self.formatters.get(key) or (
            self.fallback_locale.get_formatter(key, default) if self.fallback_locale else default)

    def format(self, obj: object, fmt: str = '', default_formatter=None, formatter_id: str = None):
        formatter_id = formatter_id or self.get_formatter_id(obj.__class__)

        formatter = self.get_formatter(formatter_id, default=default_formatter)

        if obj is None:
            return str(obj)
        if formatter:
            return formatter(obj, self, fmt)
        if hasattr(obj, '__localized_format__'):
            return getattr(obj, '__localized_format__')(self, fmt)
        if hasattr(obj, '__format__'):
            return getattr(obj, '__format__')(fmt)
        return str(obj)

    def apply_modifier(self, modifier_id, *args):
        modifier = self.get_modifier(modifier_id)
        if not modifier:
            raise ValueError(f"Modifier {modifier_id=} not found!")
        return modifier(self, *args)

    def get_text(self, text_key, **kwargs):
        text = self.get(text_key, default=text_key)
        expression_parser = ExpressionParser()
        resolved = False
        while not resolved:
            result, resolved = expression_parser.parse(text)
            buffer = list()
            for part in result:
                if isinstance(part, BraceExpression):  # formatting
                    buffer.append(self.format(kwargs.get(part.formatted_obj, None), part.format_spec))
                elif isinstance(part, BracketExpression):
                    buffer.append(self._process_bracket_expr(part, **kwargs))
                else:
                    buffer.append(part)

                text = ''.join(buffer)

        return text

    def register_modifier(self, modifier_id, modifier_func):
        self.modifiers[modifier_id] = modifier_func

    def register_formatter(self, formatter_id, formatter_func):
        self.formatters[formatter_id] = formatter_func

    def _process_bracket_expr(self, bracket_expr: 'BracketExpression', **kwargs) -> str:
        key = bracket_expr.stem

        if bracket_expr.special == '!':
            # modifier
            resolved_args = [kwargs.get(arg[1:], None) if arg and arg[0] == '$' else arg for arg in
                             bracket_expr.args or []]
            return self.apply_modifier(key, *resolved_args)
        else:
            # getter
            if bracket_expr.special == '$':
                key = kwargs.get(key, key)  # resolve key
            return self.get(key, default=key)

    @staticmethod
    def get_formatter_id(cls):
        return f"{cls.__module__}.{cls.__name__}"
