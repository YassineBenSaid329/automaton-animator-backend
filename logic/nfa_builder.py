# logic/nfa_builder.py

# Imports from our own package to know the AST structure
from .ast_nodes import ASTNode, OperandNode, StarNode, ConcatNode, UnionNode

# --- NFA Data Structures and Component "Toolbox" ---
# (This is the familiar code from our original automata_logic.py)

class StateFactory:
    def __init__(self):
        self.count = 0
    def new_state(self):
        state_name = f"q{self.count}"; self.count += 1; return state_name

class NFA:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = sorted(list(set(alphabet)))
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states
    def to_dict(self):
        return {"states": self.states, "alphabet": self.alphabet, "transitions": self.transitions, "start_state": self.start_state, "final_states": self.final_states}

def _create_nfa_for_char(char: str, state_factory: StateFactory) -> NFA:
    start_state = state_factory.new_state(); final_state = state_factory.new_state()
    return NFA(states=[start_state, final_state], alphabet=[char], transitions=[[start_state, char, final_state]], start_state=start_state, final_states=[final_state])

def concatenate_nfas(nfa1: NFA, nfa2: NFA) -> NFA:
    EPSILON = ""
    new_transitions = nfa1.transitions + nfa2.transitions
    for final_state in nfa1.final_states:
        new_transitions.append([final_state, EPSILON, nfa2.start_state])
    return NFA(states=nfa1.states + nfa2.states, alphabet=nfa1.alphabet + nfa2.alphabet, transitions=new_transitions, start_state=nfa1.start_state, final_states=nfa2.final_states)

def union_nfas(nfa1: NFA, nfa2: NFA, state_factory: StateFactory) -> NFA:
    EPSILON = ""; new_start_state = state_factory.new_state(); new_final_state = state_factory.new_state()
    new_transitions = nfa1.transitions + nfa2.transitions
    new_transitions.append([new_start_state, EPSILON, nfa1.start_state])
    new_transitions.append([new_start_state, EPSILON, nfa2.start_state])
    for final_state in nfa1.final_states: new_transitions.append([final_state, EPSILON, new_final_state])
    for final_state in nfa2.final_states: new_transitions.append([final_state, EPSILON, new_final_state])
    new_states = nfa1.states + nfa2.states + [new_start_state, new_final_state]
    return NFA(states=new_states, alphabet=nfa1.alphabet + nfa2.alphabet, transitions=new_transitions, start_state=new_start_state, final_states=[new_final_state])

def kleene_star_nfa(nfa: NFA, state_factory: StateFactory) -> NFA:
    EPSILON = ""; new_start_state = state_factory.new_state(); new_final_state = state_factory.new_state()
    new_transitions = nfa.transitions[:] # Make a copy
    new_transitions.append([new_start_state, EPSILON, new_final_state])
    new_transitions.append([new_start_state, EPSILON, nfa.start_state])
    for final_state in nfa.final_states:
        new_transitions.append([final_state, EPSILON, new_final_state])
        new_transitions.append([final_state, EPSILON, nfa.start_state])
    new_states = nfa.states + [new_start_state, new_final_state]
    return NFA(states=new_states, alphabet=nfa.alphabet, transitions=new_transitions, start_state=new_start_state, final_states=[new_final_state])


# --- The NFA Builder (AST Visitor) ---

class NFABuilder:
    """
    Walks a completed Abstract Syntax Tree and uses the component functions
    to build the final NFA. This implements the 'Visitor' design pattern.
    """
    def __init__(self):
        self.state_factory = StateFactory()

    def build(self, ast_node: ASTNode) -> NFA:
        """The main public entry point for visiting the AST."""
        # This is a dispatch table that maps node types to their visit methods.
        visit_method = getattr(self, f'_visit_{type(ast_node).__name__}', self._generic_visit)
        return visit_method(ast_node)

    def _generic_visit(self, node):
        # This will be called if we ever create an AST node we forgot to handle.
        raise Exception(f'No _visit method for AST node of type {type(node).__name__}')

    def _visit_OperandNode(self, node: OperandNode) -> NFA:
        # Base case of the recursion.
        return _create_nfa_for_char(node.value, self.state_factory)

    def _visit_ConcatNode(self, node: ConcatNode) -> NFA:
        # Recursively build the NFAs for the left and right children.
        left_nfa = self.build(node.left)
        right_nfa = self.build(node.right)
        # Combine the results.
        return concatenate_nfas(left_nfa, right_nfa)

    def _visit_UnionNode(self, node: UnionNode) -> NFA:
        left_nfa = self.build(node.left)
        right_nfa = self.build(node.right)
        return union_nfas(left_nfa, right_nfa, self.state_factory)

    def _visit_StarNode(self, node: StarNode) -> NFA:
        operand_nfa = self.build(node.operand)
        return kleene_star_nfa(operand_nfa, self.state_factory)