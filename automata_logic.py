# automata_logic.py
import collections

# --- Helper Classes and NFA Representation (largely unchanged) ---


Token = collections.namedtuple('Token', ['type', 'value']) # A simple data class to represent a token.


class RegexSyntaxError(Exception):
    """Custom exception for syntax errors in the regular expression."""
    pass


def tokenize(regex_string: str) -> list[Token]:
    """
    Converts a raw regex string into a list of Tokens.
    This function also handles invalid characters and inserts implicit concatenation operators.
    """
    tokens = []
    # Sets of character types for our concatenation rule
    ending_tokens = {'OPERAND', 'CLOSE_PAREN', 'STAR'}
    beginning_tokens = {'OPERAND', 'OPEN_PAREN'}

    for char in regex_string:

        # 1. Classify the character into a Token
        if char.isalnum():
            current_token = Token('OPERAND', char)
        elif char == '*':
            # We give star its own type to help with validation later
            current_token = Token('STAR', char)
        elif char == '|':
            current_token = Token('UNION', char)
        elif char == '(':
            current_token = Token('OPEN_PAREN', char)
        elif char == ')':
            current_token = Token('CLOSE_PAREN', char)
        else:
            # If character is unknown, fail fast.
            raise RegexSyntaxError(f"Invalid character in expression: '{char}'")

        # 2. Check if an implicit concatenation is needed
        if tokens:  # Can only concatenate if there's a previous token
            previous_token = tokens[-1]
            if previous_token.type in ending_tokens and current_token.type in beginning_tokens:
                tokens.append(Token('CONCAT', '.'))

        # 3. Add the current token to the list
        tokens.append(current_token)

    return tokens


class StateFactory:
    def __init__(self): self.count = 0

    def new_state(self):
        state_name = f"q{self.count}"
        self.count += 1
        return state_name


class NFA:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = sorted(list(set(alphabet)))
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def to_dict(self):
        return {"states": self.states, "alphabet": self.alphabet, "transitions": self.transitions,
                "start_state": self.start_state, "final_states": self.final_states}


# --- Component Functions (Our "Lego Bricks") ---

def _create_nfa_for_char(char: str, state_factory: StateFactory) -> NFA:
    start_state = state_factory.new_state()
    final_state = state_factory.new_state()
    return NFA(states=[start_state, final_state], alphabet=[char], transitions=[[start_state, char, final_state]],
               start_state=start_state, final_states=[final_state])


def concatenate_nfas(nfa1: NFA, nfa2: NFA) -> NFA:
    EPSILON = ""
    new_transitions = nfa1.transitions + nfa2.transitions
    for final_state in nfa1.final_states:
        new_transitions.append([final_state, EPSILON, nfa2.start_state])
    return NFA(states=nfa1.states + nfa2.states, alphabet=nfa1.alphabet + nfa2.alphabet, transitions=new_transitions,
               start_state=nfa1.start_state, final_states=nfa2.final_states)


def union_nfas(nfa1: NFA, nfa2: NFA, state_factory: StateFactory) -> NFA:
    EPSILON = ""
    new_start_state = state_factory.new_state()
    new_final_state = state_factory.new_state()
    new_transitions = nfa1.transitions + nfa2.transitions
    new_transitions.append([new_start_state, EPSILON, nfa1.start_state])
    new_transitions.append([new_start_state, EPSILON, nfa2.start_state])
    for final_state in nfa1.final_states: new_transitions.append([final_state, EPSILON, new_final_state])
    for final_state in nfa2.final_states: new_transitions.append([final_state, EPSILON, new_final_state])
    new_states = nfa1.states + nfa2.states + [new_start_state, new_final_state]
    return NFA(states=new_states, alphabet=nfa1.alphabet + nfa2.alphabet, transitions=new_transitions,
               start_state=new_start_state, final_states=[new_final_state])


def kleene_star_nfa(nfa: NFA, state_factory: StateFactory) -> NFA:
    """
    Creates a new NFA for the Kleene Star (*) of a given NFA.
    """
    EPSILON = ""
    new_start_state = state_factory.new_state()
    new_final_state = state_factory.new_state()

    # The new transitions include all the old ones
    new_transitions = nfa.transitions

    # 1. Add epsilon transition from the new start to the new final state (zero matches)
    new_transitions.append([new_start_state, EPSILON, new_final_state])

    # 2. Add epsilon transition from the new start to the old start state
    new_transitions.append([new_start_state, EPSILON, nfa.start_state])

    # 3. For each old final state, add epsilon transitions to the new final state AND back to the old start state (loop)
    for final_state in nfa.final_states:
        new_transitions.append([final_state, EPSILON, new_final_state])
        new_transitions.append([final_state, EPSILON, nfa.start_state])

    # The new states are all the old states plus the two new ones
    new_states = nfa.states + [new_start_state, new_final_state]

    return NFA(
        states=new_states,
        alphabet=nfa.alphabet,  # The alphabet doesn't change
        transitions=new_transitions,
        start_state=new_start_state,
        final_states=[new_final_state]
    )


# --- The Intelligent Parser (The "Master Builder") ---

class RegexParser:
    def __init__(self, state_factory: StateFactory):
        self.nfa_stack = []
        self.operator_stack = []
        self.state_factory = state_factory
        # Precedence now includes parentheses
        self.precedence = {'UNION': 1, 'CONCAT': 2, 'STAR': 3}

    def _apply_operator(self, operator_token: Token):
        """Applies an operator to the NFA stack based on the token type."""
        if operator_token.type == 'UNION':
            if len(self.nfa_stack) < 2:
                raise RegexSyntaxError("Invalid syntax: '|' requires two operands.")
            nfa2 = self.nfa_stack.pop()
            nfa1 = self.nfa_stack.pop()
            self.nfa_stack.append(union_nfas(nfa1, nfa2, self.state_factory))
        elif operator_token.type == 'CONCAT':
            if len(self.nfa_stack) < 2:
                raise RegexSyntaxError("Invalid syntax for concatenation.")
            nfa2 = self.nfa_stack.pop()
            nfa1 = self.nfa_stack.pop()
            self.nfa_stack.append(concatenate_nfas(nfa1, nfa2))
        elif operator_token.type == 'STAR':
            if not self.nfa_stack:
                raise RegexSyntaxError("Invalid syntax: '*' must follow an operand.")
            nfa_to_star = self.nfa_stack.pop()
            self.nfa_stack.append(kleene_star_nfa(nfa_to_star, self.state_factory))

    def parse(self, tokens: list[Token]) -> NFA:
        for token in tokens:
            if token.type == 'OPERAND':
                self.nfa_stack.append(_create_nfa_for_char(token.value, self.state_factory))
            elif token.type == 'OPEN_PAREN':
                self.operator_stack.append(token)
            elif token.type == 'CLOSE_PAREN':
                while self.operator_stack and self.operator_stack[-1].type != 'OPEN_PAREN':
                    self._apply_operator(self.operator_stack.pop())

                if not self.operator_stack:  # Unmatched closing parenthesis
                    raise RegexSyntaxError("Mismatched parentheses: Unexpected ')'")
                self.operator_stack.pop()  # Pop the matching OPEN_PAREN
            else:  # Token is an operator (UNION, CONCAT, STAR)
                while (self.operator_stack and
                       self.operator_stack[-1].type != 'OPEN_PAREN' and
                       self.precedence.get(self.operator_stack[-1].type, 0) >= self.precedence.get(token.type, 0)):
                    self._apply_operator(self.operator_stack.pop())
                self.operator_stack.append(token)

        while self.operator_stack:
            operator = self.operator_stack.pop()
            if operator.type == 'OPEN_PAREN':  # Unmatched opening parenthesis
                raise RegexSyntaxError("Mismatched parentheses: Missing ')'")
            self._apply_operator(operator)

        # Final validation
        if len(self.nfa_stack) != 1:
            raise RegexSyntaxError("Invalid expression syntax.")

        return self.nfa_stack[0]


# --- The Main Entry Point Function ---

def regex_to_nfa(regex_string: str) -> NFA:
    """The main entry point. Tokenizes the string and then parses the tokens."""
    if not regex_string:
        # We can handle this case gracefully without a full parser error
        raise ValueError("Regex string cannot be empty.")

    # The new three-part process:
    try:
        # 1. Tokenize (and insert concatenation)
        tokens = tokenize(regex_string)

        # 2. Parse (with validation)
        state_factory = StateFactory()
        parser = RegexParser(state_factory)
        return parser.parse(tokens)

    # 3. Handle Errors
    except RegexSyntaxError as e:
        # We re-raise it as a ValueError for the API layer to catch as a 400 error
        raise ValueError(str(e))