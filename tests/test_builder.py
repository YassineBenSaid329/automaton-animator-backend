# tests/test_builder.py

import pytest
from logic.ast_nodes import *
from logic.nfa_builder import NFABuilder, NFA


class TestNFABuilder:

    def test_builds_from_operand_node(self):
        ast = OperandNode('a')
        nfa = NFABuilder().build(ast)

        assert isinstance(nfa, NFA)
        assert len(nfa.states) == 2
        assert len(nfa.transitions) == 1
        assert nfa.alphabet == ['a']

    def test_builds_from_concat_node(self):
        ast = ConcatNode(OperandNode('a'), OperandNode('b'))
        nfa = NFABuilder().build(ast)

        assert len(nfa.states) == 4
        assert len(nfa.transitions) == 3
        epsilon_transitions = [t for t in nfa.transitions if t[1] == '']
        assert len(epsilon_transitions) == 1

    def test_builds_from_union_node(self):
        ast = UnionNode(OperandNode('a'), OperandNode('b'))
        nfa = NFABuilder().build(ast)

        assert len(nfa.states) == 6
        assert len(nfa.transitions) == 6
        epsilon_transitions = [t for t in nfa.transitions if t[1] == '']
        assert len(epsilon_transitions) == 4
        assert len([t for t in epsilon_transitions if t[0] == nfa.start_state]) == 2

    def test_builds_from_star_node(self):
        ast = StarNode(OperandNode('a'))
        nfa = NFABuilder().build(ast)

        assert len(nfa.states) == 4
        assert len(nfa.transitions) == 5
        epsilon_transitions = [t for t in nfa.transitions if t[1] == '']
        assert len(epsilon_transitions) == 4

    def test_builds_from_deeply_nested_ast(self):
        """
        An integration test for the builder that uses a complex, nested AST
        representing the expression: a(b|c)*
        """
        ast = ConcatNode(
            OperandNode('a'),
            StarNode(
                UnionNode(
                    OperandNode('b'),
                    OperandNode('c')
                )
            )
        )

        nfa = NFABuilder().build(ast)

        # Expected states = 2(a) + 2(b) + 2(c) + 2(union) + 2(star) = 10
        assert len(nfa.states) == 10

        # Expected transitions = 1(a) + 1(b) + 1(c) + 4(union) + 4(star) + 1(concat) = 12
        assert len(nfa.transitions) == 12

        assert nfa.alphabet == ['a', 'b', 'c']

        epsilon_transitions = [t for t in nfa.transitions if t[1] == '']
        assert len(epsilon_transitions) == 9