from typing import List, Union, Optional, Tuple
from dataclasses import dataclass
import re
import yaml
from yaml.parser import ParserError as YAMLParserError

BRACKET_PATTERN = re.compile(r'^\[(\$|!)?([a-z0-9_]+(?:\.[a-z0-9_]+)*)(?::(.+))?\]$', re.IGNORECASE)
BRACE_PATTERN = re.compile(r'^{([a-z_][a-z0-9_]*?)(:[^\}]+)?}$', re.IGNORECASE)


@dataclass
class BracketExpression:
    stem: str
    special: Optional[str] = None
    args: Optional[tuple[str]] = None

    @staticmethod
    def parse(expression):
        match = BRACKET_PATTERN.match(expression)
        if match:
            args_string = match.group(3).strip() if match.group(3) else None
            args = None
            if args_string:
                args = []
                try:
                    args = yaml.safe_load(f"[{args_string}]")
                except YAMLParserError:
                    # TODO: log warning
                    return expression

            return BracketExpression(match.group(2), special=match.group(1) or None,
                                     args=tuple(args) if args is not None else None)

        return expression


@dataclass
class BraceExpression:
    formatted_obj: str
    format_spec: str = ''

    @staticmethod
    def parse(expression):
        match = BRACE_PATTERN.match(expression)
        if match:
            return BraceExpression(formatted_obj=match.group(1),
                                   format_spec=match.group(2)[1:] if match.group(2) else '')

        return expression


class ExpressionParser:
    def __init__(self):
        self.result: List[Union[str, BracketExpression, BraceExpression]] = []
        self.buffer = []
        self.state = "TEXT"

    def pop_buffer(self):
        content = "".join(self.buffer)
        self.buffer.clear()
        return content

    def flush_buffer(self):
        if self.buffer:
            self.result.append(self.pop_buffer())

    def parse(self, text: str) -> Tuple[List[Union[str, BracketExpression, BraceExpression]], bool]:
        self.result: List[Union[str, BracketExpression, BraceExpression]] = []
        self.buffer = []
        self.state = "TEXT"
        previous_state = self.state
        it = iter(text)
        resolved = True
        for char in it:
            if self.state == "TEXT":
                if char == "{":
                    self.flush_buffer()
                    self.state = "BRACE"
                    self.buffer.append(char)
                elif char == "[":
                    self.flush_buffer()
                    self.state = "BRACKET"
                    self.buffer.append(char)
                elif char == '\\':
                    previous_state = self.state
                    self.state = 'ESCAPE'
                else:
                    self.buffer.append(char)

            elif self.state == "BRACE":
                if char == "}":  # Closing brace
                    self.buffer.append(char)
                    expression = self.pop_buffer()
                    content = BraceExpression.parse(expression)
                    if isinstance(content, BraceExpression):
                        resolved = False
                    self.result.append(content)
                    self.state = "TEXT"
                elif char == '\\':
                    previous_state = self.state
                    self.state = 'ESCAPE'
                else:
                    self.buffer.append(char)

            elif self.state == "BRACKET":
                if char == "]":  # Closing bracket
                    self.buffer.append(char)
                    expression = self.pop_buffer()
                    content = BracketExpression.parse(expression)
                    if isinstance(content, BracketExpression):
                        resolved = False
                    self.result.append(content)
                    self.state = "TEXT"
                elif char == '\\':
                    previous_state = self.state
                    self.state = 'ESCAPE'
                else:
                    self.buffer.append(char)
            elif self.state == "ESCAPE":
                if char not in ('\\', '{', '[', '}', ']'):
                    self.buffer.append('\\')
                self.buffer.append(char)
                self.state = previous_state

        self.flush_buffer()
        return self.result, resolved
