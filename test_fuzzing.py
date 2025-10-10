# test_fuzzing.py

from hypothesis import given, strategies as st, settings
from automata_logic import regex_to_nfa, RegexSyntaxError


# The @given decorator tells pytest to run this test many times with generated data.
# st.text() is a "strategy" that generates all sorts of strings.
@given(st.text())
# The @settings decorator can be used to control hypothesis.
# Here, we set a deadline of 500ms per example to catch infinite loops.
@settings(deadline=500)
def test_parser_does_not_crash_on_random_input(regex_string):
    """
    Fuzz test to ensure the parser can handle any string input
    without raising an unexpected, unhandled exception.
    """
    try:
        # We run our main function with the randomly generated string.
        regex_to_nfa(regex_string)

    except (ValueError, RegexSyntaxError):
        # These are our EXPECTED errors for invalid syntax.
        # If we catch one, it means our validation is working correctly.
        # We simply 'pass', and hypothesis considers this a successful test case.
        pass

    # If any OTHER exception occurs (like IndexError, TypeError, RecursionError),
    # it will not be caught here. Hypothesis will see the unhandled exception,
    # fail the test, and report the exact input that caused the crash.