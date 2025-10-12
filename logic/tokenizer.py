# logic/tokenizer.py
import collections

# A simple data class to represent a token.
Token = collections.namedtuple('Token', ['type', 'value'])

class RegexSyntaxError(Exception):
    """Custom exception for syntax errors in the regular expression."""
    pass

def tokenize(regex_string: str) -> list[Token]:
    """
    Converts a raw regex string into a list of Tokens.
    This function also handles invalid characters and inserts implicit concatenation operators.
    """
    tokens = []
    ending_tokens = {'OPERAND', 'CLOSE_PAREN', 'STAR'}
    beginning_tokens = {'OPERAND', 'OPEN_PAREN'}

    for char in regex_string:
        current_token = None
        if char.isalnum():
            current_token = Token('OPERAND', char)
        elif char == '*':
            current_token = Token('STAR', char)
        elif char == '|':
            current_token = Token('UNION', char)
        elif char == '.':
            current_token = Token('CONCAT', char)
        elif char == '(':
            current_token = Token('OPEN_PAREN', char)
        elif char == ')':
            current_token = Token('CLOSE_PAREN', char)
        else:
            raise RegexSyntaxError(f"Invalid character in expression: '{char}'")

        if tokens:
            previous_token = tokens[-1]
            if previous_token.type in ending_tokens and current_token.type in beginning_tokens:
                tokens.append(Token('CONCAT', '.'))

        tokens.append(current_token)

    return tokens