# tests/test_parser.py

import pytest
import re
from logic.tokenizer import tokenize, RegexSyntaxError
from logic.parser import RegexParser
from logic.ast_nodes import *


class TestRegexParser:
    # --- 1. Correctness Tests (Valid Inputs) ---

    def test_parses_simple_concat(self):
        tokens = tokenize("ab")
        ast = RegexParser(tokens).parse()
        assert isinstance(ast, ConcatNode)
        assert isinstance(ast.left, OperandNode) and ast.left.value == 'a'
        assert isinstance(ast.right, OperandNode) and ast.right.value == 'b'

    def test_parses_left_associativity_for_union(self):
        tokens = tokenize("a|b|c")
        ast = RegexParser(tokens).parse()

        assert isinstance(ast, UnionNode)
        assert isinstance(ast.right, OperandNode) and ast.right.value == 'c'
        assert isinstance(ast.left, UnionNode)
        assert isinstance(ast.left.left, OperandNode) and ast.left.left.value == 'a'
        assert isinstance(ast.left.right, OperandNode) and ast.left.right.value == 'b'

    def test_parses_precedence_of_concat_over_union(self):
        tokens = tokenize("a|bc")
        ast = RegexParser(tokens).parse()

        assert isinstance(ast, UnionNode)
        assert isinstance(ast.left, OperandNode) and ast.left.value == 'a'
        assert isinstance(ast.right, ConcatNode)
        assert isinstance(ast.right.left, OperandNode) and ast.right.left.value == 'b'
        assert isinstance(ast.right.right, OperandNode) and ast.right.right.value == 'c'

    def test_parses_complex_nested_expression(self):
        tokens = tokenize("a(b|c)*")
        ast = RegexParser(tokens).parse()

        assert isinstance(ast, ConcatNode)
        assert isinstance(ast.left, OperandNode) and ast.left.value == 'a'
        assert isinstance(ast.right, StarNode)

        union_node = ast.right.operand
        assert isinstance(union_node, UnionNode)
        assert isinstance(union_node.left, OperandNode) and union_node.left.value == 'b'
        assert isinstance(union_node.right, OperandNode) and union_node.right.value == 'c'

    # --- 2. Validation Tests (Invalid Inputs) ---

    @pytest.mark.parametrize("invalid_regex, expected_error_message", [
        ("*a", "Invalid syntax: Unexpected token '*'"),
        ("|a", "Invalid syntax: Unexpected token '|'"),
        (".a", "Invalid syntax: Unexpected token '.'"),
        (")", "Invalid syntax: Unexpected token ')'"),
        ("a**", "cannot follow another '*'"),
        ("a|)", "Invalid syntax: Unexpected token ')'"),
        ("a||b", "Invalid syntax: Unexpected token '|'"),
        ("a(b|)", "Invalid syntax: Unexpected token ')'"),
        ("a|", "Unexpected end of expression"),
        ("a.", "Unexpected end of expression"),
        ("a(", "Unexpected end of expression, expecting an operand or '('"),
        ("()", "Invalid syntax: Unexpected token ')'")
    ])
    def test_raises_specific_error_for_invalid_grammar(self, invalid_regex, expected_error_message):
        with pytest.raises(RegexSyntaxError, match=re.escape(expected_error_message)):
            tokens = tokenize(invalid_regex)
            RegexParser(tokens).parse()