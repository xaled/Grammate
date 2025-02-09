import unittest
from mini_localization.parser import ExpressionParser, BraceExpression, BracketExpression


class TestExpressionParser(unittest.TestCase):

    def setUp(self):
        self.parser = ExpressionParser()

    def test_simple_text(self):
        result, resolved = self.parser.parse("Hello World!")
        self.assertEqual(result, ["Hello World!"])
        self.assertTrue(resolved)

    def test_brace_expression_1(self):
        result, resolved = self.parser.parse("Hello {name:uppercase}!")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "Hello ")
        self.assertIsInstance(result[1], BraceExpression)
        self.assertEqual(result[1].formatted_obj, "name")
        self.assertEqual(result[1].format_spec, "uppercase")
        self.assertTrue(not resolved)

    def test_brace_expression_2(self):
        result, resolved = self.parser.parse("Today is {date:long}!")
        self.assertIsInstance(result[1], BraceExpression)
        self.assertEqual(result[1].formatted_obj, "date")
        self.assertEqual(result[1].format_spec, "long")
        self.assertTrue(not resolved)
        result, resolved = self.parser.parse("Balance: ${balance:.2f}")
        self.assertEqual(result[0], "Balance: $")
        self.assertIsInstance(result[1], BraceExpression)
        self.assertEqual(result[1].formatted_obj, "balance")
        self.assertEqual(result[1].format_spec, ".2f")
        self.assertTrue(not resolved)

    def test_bracket_expression_1(self):
        result, resolved = self.parser.parse("[Name]: [apple]")
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], BracketExpression)
        self.assertIsInstance(result[2], BracketExpression)
        self.assertEqual(result[1], ": ")
        self.assertEqual(result[0].stem, "Name")
        self.assertEqual(result[0].args, None)
        self.assertTrue(not resolved)

    def test_bracket_expression_2(self):
        result, resolved = self.parser.parse("[!adj:apple,$color,fem,indef,marfu3]")
        self.assertIsInstance(result[0], BracketExpression)
        self.assertEqual(result[0].stem, "adj")
        self.assertEqual(result[0].special, "!")
        self.assertEqual(result[0].args, ("apple", "$color", "fem", "indef", "marfu3"))

    def test_bracket_expression_3(self):
        result, resolved = self.parser.parse("[!adj:apple,$color,null,2,true]")
        self.assertIsInstance(result[0], BracketExpression)
        self.assertEqual(result[0].stem, "adj")
        self.assertEqual(result[0].special, "!")
        self.assertEqual(result[0].args, ("apple", "$color", None, 2, True))

    def test_multiple_expressions(self):
        result, resolved = self.parser.parse("Hello {name} and [!plural:friend,$count]!")
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], "Hello ")
        self.assertIsInstance(result[1], BraceExpression)
        self.assertEqual(result[1].formatted_obj, "name")
        self.assertEqual(result[1].format_spec, '')
        self.assertEqual(result[2], " and ")
        self.assertIsInstance(result[3], BracketExpression)
        self.assertEqual(result[3].stem, "plural")
        self.assertEqual(result[3].special, "!")
        self.assertEqual(result[3].args, ('friend', '$count'))
        self.assertTrue(not resolved)

    def test_escape_braces(self):
        result, resolved = self.parser.parse("Hello \\{name}!")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Hello {name}!")
        self.assertTrue(resolved)
        result, resolved = self.parser.parse("Hello \\{name\\}!")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Hello {name}!")
        self.assertTrue(resolved)

    def test_escape_brackets(self):
        # obligatory open bracket escape
        result, resolved = self.parser.parse("Hello \\[name]!")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Hello [name]!")
        self.assertTrue(resolved)

        # optional close bracket escape
        result, resolved = self.parser.parse("Hello \\[name\\]!")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Hello [name]!")
        self.assertTrue(resolved)

        # escaping inside bracket expression
        result, resolved = self.parser.parse(r"[!adj:apple,'key\subkey',\[1,2,3\],null,2,true]")
        self.assertIsInstance(result[0], BracketExpression)
        self.assertEqual(result[0].stem, "adj")
        self.assertEqual(result[0].special, "!")
        self.assertEqual(result[0].args, ('apple', r'key\subkey', [1, 2, 3], None, 2, True))


if __name__ == '__main__':
    unittest.main()
