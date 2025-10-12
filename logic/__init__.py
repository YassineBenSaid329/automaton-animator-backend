# logic/__init__.py

# Import the necessary components from our new modules.
from .tokenizer import tokenize, RegexSyntaxError
from .parser import RegexParser
from .nfa_builder import NFABuilder, NFA


def regex_to_nfa(regex_string: str) -> NFA:
    """
    The main public entry point for the logic package.
    Orchestrates the three-stage conversion process:
    1. Tokenize the raw string.
    2. Parse the tokens into an Abstract Syntax Tree (AST).
    3. Build the NFA by walking the AST.
    """
    if not regex_string:
        raise ValueError("Regex string cannot be empty.")

    try:
        # Stage 1: Tokenize the raw string into a stream of Tokens.
        tokens = tokenize(regex_string)

        # Stage 2: Parse the token stream into a structured AST.
        parser = RegexParser(tokens)
        ast = parser.parse()

        # Stage 3: Build the final NFA by walking the AST.
        builder = NFABuilder()
        nfa = builder.build(ast)

        return nfa

    except RegexSyntaxError as e:
        # For any syntax error found during the process, convert it to a
        # ValueError for the API layer to handle as a 400 Bad Request.
        raise ValueError(str(e))