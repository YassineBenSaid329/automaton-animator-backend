# test_fuzzing.py

from hypothesis import given, strategies as st, settings
from logic import regex_to_nfa, RegexSyntaxError

@given(st.text())
# Keep the deadline to protect against infinite loops.
@settings(max_examples=2000, deadline=500)
def test_parser_does_not_crash_on_random_input(regex_string):
    """
    Fuzz test to ensure the parser can handle any string input
    without raising an unexpected, unhandled exception.
    """
    try:
        # We now use the main logic entry point
        regex_to_nfa(regex_string)
    except (ValueError, RegexSyntaxError):
        # We expect these errors for invalid inputs.
        pass