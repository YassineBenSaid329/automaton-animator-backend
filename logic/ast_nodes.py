# logic/ast_nodes.py

class ASTNode:
    """Base class for all AST nodes."""
    pass

class OperandNode(ASTNode):
    """Represents a literal character (e.g., 'a', 'b'). This is a leaf node."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Operand({self.value})"

class UnaryOpNode(ASTNode):
    """Base class for unary operators (like Kleene Star)."""
    def __init__(self, operand):
        self.operand = operand

class StarNode(UnaryOpNode):
    """Represents the Kleene Star (*) operation."""
    def __repr__(self):
        return f"Star({self.operand})"

class BinaryOpNode(ASTNode):
    """Base class for binary operators (like Union, Concat)."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

class ConcatNode(BinaryOpNode):
    """Represents the Concatenation (.) operation."""
    def __repr__(self):
        return f"Concat({self.left}, {self.right})"

class UnionNode(BinaryOpNode):
    """Represents the Union (|) operation."""
    def __repr__(self):
        return f"Union({self.left}, {self.right})"