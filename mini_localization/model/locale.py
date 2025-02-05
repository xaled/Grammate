from .base import BaseLocale
from ..config import ConfigDict


class Locale(BaseLocale):
    def __init__(self, config: ConfigDict, fallback_locale: 'Locale'):
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

    def format(self, obj: object, fmt: str = None, default_formatter=None, formatter_id: str = None):
        formatter_id = formatter_id or f"{obj.__class__.__module__}.{obj.__class__.__name__}"

        formatter = self.get_formatter(formatter_id, default=default_formatter)

        if formatter:
            return formatter(obj, self, fmt=fmt)
        if hasattr(obj, '__localized_format__'):
            return getattr(obj, '__localized_format__')(self, fmt=fmt)
        return str(obj)

    def apply_modifier(self, modifier_id, *args):
        modifier = self.get_modifier(modifier_id)
        if not modifier:
            raise ValueError(f"Rule {modifier_id=} not found!")
        resolved_config = self.get(config_key)
        return modifier(resolved_config, *args, **kwargs)

    def get_text(self, text_key, **kwargs):
        default = default or text_key
        resolved_config = self.get(text_key, default=default)

        if isinstance(resolved_config, list) and resolved_config:
            text = str(resolved_config[0])
        else:
            text = str(resolved_config)

        if args:
            text = text % args
        return text

    def register_modifier(self, modifier_id, modifier_func):
        self.modifiers[modifier_id] = modifier_func

    def register_formatter(self, formatter_id, formatter_func):
        self.formatters[formatter_id] = formatter_func

    def format_ex(self, string: str, **kwargs):

        string = self.get_text(string)
        unresolved = True

        def parse_rule_args(args_str: str):
            args = []
            for arg in args_str.split(','):
                if arg.startswith('$'):
                    key = arg[1:]
                    args.append(kwargs.get(key, arg))  # Replace dynamic args with value from kwargs
                else:
                    args.append(arg)
            return args

        def replace_rule(match):
            nonlocal unresolved
            unresolved = True
            rule_str = match.group(1)
            key, rule_with_args = rule_str.split('.', 1)
            rule_id, args_str = rule_with_args.split(':', 1)
            args = parse_rule_args(args_str)

            # Apply the rule (For now, we only handle mock rules like plural)
            return self.apply_modifier(key, rule_id, *args)

        def replace_placeholder(match):
            nonlocal unresolved
            unresolved = True
            key = match.group(1)
            return str(kwargs.get(key, f'{{{key}}}'))

        while unresolved:
            unresolved = False
            string = RULE_PATTERN.sub(replace_rule, string)

            unresolved = False
            string = PLACEHOLDER_PATTERN.sub(replace_placeholder, string)

        return string
