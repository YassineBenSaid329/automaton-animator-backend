# logic/parser.py

from .tokenizer import Token, RegexSyntaxError
from .ast_nodes import ASTNode, OperandNode, StarNode, ConcatNode, UnionNode


class RegexParser:
    """
    Parses a stream of tokens into an Abstract Syntax Tree (AST).
    This parser uses a Recursive Descent approach to handle
    operator precedence and scope correctly.
    """

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> ASTNode:
        """The main public entry point to start the parsing process."""
        if not self.tokens:
            raise RegexSyntaxError("Cannot parse an empty expression.")

        ast = self._parse_union()

        if self._current_token() is not None:
            raise RegexSyntaxError(f"Invalid syntax or unexpected characters at end of expression.")

        return ast

    def _parse_union(self) -> ASTNode:
        """Parses a sequence of union operations (lowest precedence)."""
        node = self._parse_concat()

        while self._current_token() is not None and self._current_token().type == 'UNION':
            self._advance()  # Consume '|'
            right_node = self._parse_concat()
            node = UnionNode(node, right_node)

        return node

    def _parse_concat(self) -> ASTNode:
        """Parses a sequence of concatenations (medium precedence)."""
        node = self._parse_star()

        while self._current_token() is not None and self._current_token().type == 'CONCAT':
            self._advance()  # Consume '.'
            right_node = self._parse_star()
            node = ConcatNode(node, right_node)

        return node

    def _parse_star(self) -> ASTNode:
        """Parses a primary expression and then checks for a Kleene Star (high precedence)."""
        node = self._parse_primary()

        while self._current_token() is not None and self._current_token().type == 'STAR':
            if isinstance(node, StarNode):
                raise RegexSyntaxError("Invalid syntax: '*' cannot follow another '*'.")
            self._advance()  # Consume '*'
            node = StarNode(node)

        return node

    def _parse_primary(self) -> ASTNode:
        """Parses the highest-precedence expressions: Operands and parenthesized groups."""
        token = self._current_token()

        if token is None:
            raise RegexSyntaxError("Unexpected end of expression, expecting an operand or '('")

        if token.type == 'OPERAND':
            self._advance()
            return OperandNode(token.value)

        elif token.type == 'OPEN_PAREN':
            self._advance()  # Consume '('

            sub_ast = self._parse_union()

            if self._current_token() is None or self._current_token().type != 'CLOSE_PAREN':
                raise RegexSyntaxError("Mismatched parentheses: Missing ')'")

            self._advance()  # Consume ')'
            return sub_ast

        else:
            raise RegexSyntaxError(f"Invalid syntax: Unexpected token '{token.value}'")

    # --- Helper methods ---

    def _current_token(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self):
        self.pos += 1