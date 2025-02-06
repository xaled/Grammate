from typing import List, Union, Optional, Tuple
from dataclasses import dataclass
import re

BRACKET_PATTERN = re.compile(r'^\[(\$|!)?([a-z0-9_]+(?:\.[a-z0-9_]+)*)(?::([^\]]+))?\]$', re.IGNORECASE)
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
            args = tuple(match.group(3).split(',')) if match.group(3) else None
            # TODO validate args
            return BracketExpression(match.group(2), special=match.group(1) or None, args=args)

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
                elif char == "}" and self.buffer[-1] == '}':
                    pass
                elif char == "]" and self.buffer[-1] == ']':
                    pass
                else:
                    self.buffer.append(char)

            elif self.state == "BRACE":
                if char == "{":  # Escaped {{
                    # self.buffer.append(char)  # Keep first '{'
                    self.flush_buffer()
                    self.state = "TEXT"
                elif char == "}":  # Closing brace
                    self.buffer.append(char)
                    expression = self.pop_buffer()
                    content = BraceExpression.parse(expression)
                    if isinstance(content, BraceExpression):
                        resolved = False
                    self.result.append(content)
                    self.state = "TEXT"
                else:
                    self.buffer.append(char)

            elif self.state == "BRACKET":
                if char == "[":  # Escaped [[
                    # self.buffer.append(char)  # Keep first '['
                    self.flush_buffer()
                    self.state = "TEXT"
                elif char == "]":  # Closing bracket
                    self.buffer.append(char)
                    expression = self.pop_buffer()
                    content = BracketExpression.parse(expression)
                    if isinstance(content, BracketExpression):
                        resolved = False
                    self.result.append(content)
                    self.state = "TEXT"
                else:
                    self.buffer.append(char)

        self.flush_buffer()
        return self.result, resolved
