# test_automata_logic.py

import pytest
from automata_logic import tokenize, Token, RegexSyntaxError, regex_to_nfa


# We group related tests together in a class for organization.
class TestTokenizer:

    def test_tokenize_simple_union(self):
        """Tests that the tokenizer correctly handles a simple expression
        with operands and a union operator."""
        regex = "a|b"
        expected_tokens = [
            Token(type='OPERAND', value='a'),
            Token(type='UNION', value='|'),
            Token(type='OPERAND', value='b')
        ]
        assert tokenize(regex) == expected_tokens

    def test_tokenize_adds_concatenation(self):
        """Tests that the tokenizer correctly inserts the implicit CONCAT token."""
        regex = "ab"
        expected_tokens = [
            Token(type='OPERAND', value='a'),
            Token(type='CONCAT', value='.'),
            Token(type='OPERAND', value='b')
        ]
        assert tokenize(regex) == expected_tokens

    def test_tokenize_handles_all_token_types(self):
        """Tests a complex expression with parentheses and stars to ensure
        all token types are correctly identified."""
        regex = "(a|b)*"
        expected_tokens = [
            Token(type='OPEN_PAREN', value='('),
            Token(type='OPERAND', value='a'),
            Token(type='UNION', value='|'),
            Token(type='OPERAND', value='b'),
            Token(type='CLOSE_PAREN', value=')'),
            Token(type='STAR', value='*')
        ]
        assert tokenize(regex) == expected_tokens

    def test_tokenize_invalid_character_raises_error(self):
        """
        Tests that the tokenizer raises our custom syntax error for unknown characters.
        This test PASSES if the correct exception is raised.
        """
        # pytest.raises is a context manager that checks for exceptions.
        with pytest.raises(RegexSyntaxError) as excinfo:
            tokenize("a^b")

        # We can optionally assert that the error message is what we expect.
        assert "Invalid character in expression: '^'" in str(excinfo.value)


# ===== 2. FULL PARSER TESTS (Integration Tests) =====

class TestRegexParser:

    def test_parser_fails_on_invalid_star_syntax(self):
        """Tests that the full parser catches grammatical errors like '*a'."""
        with pytest.raises(ValueError) as excinfo:
            regex_to_nfa("*a")
        # We catch ValueError because our main function converts RegexSyntaxError to ValueError
        assert "Invalid syntax: '*' must follow an operand" in str(excinfo.value)

    def test_parser_fails_on_dangling_binary_operator(self):
        """Tests for an incomplete expression like 'a|'."""
        with pytest.raises(ValueError) as excinfo:
            regex_to_nfa("a|")
        assert "requires two operands" in str(excinfo.value)

    def test_parser_fails_on_mismatched_parentheses(self):
        """Tests for a missing closing parenthesis."""
        with pytest.raises(ValueError) as excinfo:
            regex_to_nfa("(a|b")
        assert "Mismatched parentheses: Missing ')'" in str(excinfo.value)

    def test_parser_correctly_handles_parentheses_precedence(self):
        """
        Tests the full regex_to_nfa function with a case where parentheses
        override the default operator precedence.
        """
        # This is our test case for a(b|c)
        nfa = regex_to_nfa("a(b|c)")

        # Asserting the full NFA structure is complex and brittle.
        # Instead, we assert key properties that prove the structure is correct.
        # The exact numbers depend on the state factory, but we can check counts.
        assert len(nfa.states) == 8
        assert len(nfa.transitions) == 8  # 1 for 'a', 1 for 'b', 1 for 'c', 1 for concat, 4 for union = 8
        assert nfa.start_state == 'q0'
        assert len(nfa.final_states) == 1
        assert nfa.final_states[0] == 'q7'