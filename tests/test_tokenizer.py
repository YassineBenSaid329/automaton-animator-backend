# tests/test_tokenizer.py

import pytest
from logic.tokenizer import tokenize, Token, RegexSyntaxError


class TestTokenizer:
    # --- 1. Basic Token Classification ---
    def test_basic_operators_and_operands(self):
        """Tests that all individual characters are classified correctly."""
        assert tokenize("a|b*()") == [
            Token('OPERAND', 'a'),
            Token('UNION', '|'),
            Token('OPERAND', 'b'),
            Token('STAR', '*'),
            Token('CONCAT', '.'),
            Token('OPEN_PAREN', '('),
            Token('CLOSE_PAREN', ')')
        ]

    # --- 2. Explicit Concatenation ---
    def test_handles_explicit_concat_operator(self):
        """Tests that a user-typed '.' is correctly tokenized."""
        assert tokenize("a.b") == [
            Token('OPERAND', 'a'),
            Token('CONCAT', '.'),
            Token('OPERAND', 'b')
        ]

    def test_handles_mixed_explicit_and_implicit_concat(self):
        """Tests that the tokenizer handles both implicit and explicit cases together."""
        # The expression a.bc should become a.b.c
        assert tokenize("a.bc") == [
            Token('OPERAND', 'a'),
            Token('CONCAT', '.'),
            Token('OPERAND', 'b'),
            Token('CONCAT', '.'),
            Token('OPERAND', 'c')
        ]

    # --- 3. Implicit Concatenation Logic ---
    def test_concat_between_operands(self):
        assert tokenize("ab") == [Token('OPERAND', 'a'), Token('CONCAT', '.'), Token('OPERAND', 'b')]

    def test_concat_after_close_paren_before_operand(self):
        assert tokenize("(a)b") == [Token('OPEN_PAREN', '('), Token('OPERAND', 'a'), Token('CLOSE_PAREN', ')'),
                                    Token('CONCAT', '.'), Token('OPERAND', 'b')]

    def test_concat_after_operand_before_open_paren(self):
        assert tokenize("a(b)") == [Token('OPERAND', 'a'), Token('CONCAT', '.'), Token('OPEN_PAREN', '('),
                                    Token('OPERAND', 'b'), Token('CLOSE_PAREN', ')')]

    def test_concat_after_star_before_operand(self):
        assert tokenize("a*b") == [Token('OPERAND', 'a'), Token('STAR', '*'), Token('CONCAT', '.'),
                                   Token('OPERAND', 'b')]

    def test_concat_after_star_before_open_paren(self):
        assert tokenize("a*(") == [Token('OPERAND', 'a'), Token('STAR', '*'), Token('CONCAT', '.'),
                                   Token('OPEN_PAREN', '(')]

    # --- 4. No Concatenation (Negative Cases) ---
    def test_no_concat_around_union(self):
        assert tokenize("a|b") == [Token('OPERAND', 'a'), Token('UNION', '|'), Token('OPERAND', 'b')]

    def test_no_concat_before_star_or_close_paren(self):
        assert tokenize("a*)") == [Token('OPERAND', 'a'), Token('STAR', '*'), Token('CLOSE_PAREN', ')')]

    def test_no_concat_after_open_paren_or_union(self):
        assert tokenize("(|a") == [Token('OPEN_PAREN', '('), Token('UNION', '|'), Token('OPERAND', 'a')]

    # --- 5. Complex and Nested Structures ---
    def test_deeply_nested_parentheses(self):
        """Tests complex nesting to ensure concat rules hold."""
        # a(b(c))d should be a.(b.(c)).d
        assert tokenize("a(b(c))d") == [
            Token('OPERAND', 'a'), Token('CONCAT', '.'),
            Token('OPEN_PAREN', '('),
            Token('OPERAND', 'b'), Token('CONCAT', '.'),
            Token('OPEN_PAREN', '('), Token('OPERAND', 'c'), Token('CLOSE_PAREN', ')'),
            Token('CLOSE_PAREN', ')'), Token('CONCAT', '.'),
            Token('OPERAND', 'd')
        ]

    def test_complex_combination_of_operators(self):
        """A stress test with multiple operators and groups."""
        # a(b|c)*d should be a.(b|c)*.d
        assert tokenize("a(b|c)*d") == [
            Token('OPERAND', 'a'), Token('CONCAT', '.'),
            Token('OPEN_PAREN', '('),
            Token('OPERAND', 'b'),
            Token('UNION', '|'),
            Token('OPERAND', 'c'),
            Token('CLOSE_PAREN', ')'),
            Token('STAR', '*'), Token('CONCAT', '.'),
            Token('OPERAND', 'd')
        ]

    # --- 6. Error Handling ---
    def test_invalid_character_raises_error(self):
        with pytest.raises(RegexSyntaxError, match="Invalid character in expression: '%'"):
            tokenize("a%b")

    def test_empty_string_is_handled(self):
        assert tokenize("") == []